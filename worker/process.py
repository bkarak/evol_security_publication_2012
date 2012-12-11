#!/usr/bin/env python
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

""" Read URLs from an AMQP queue, download referenced JAR, process it with
Findbugs, store the results to a MongoDB collection.

"""
import json

import pika
import sys
import os
import logging
import pymongo
import time
import urllib
from subprocess import Popen, PIPE, STDOUT
from signal import signal, SIGINT, SIGUSR1, SIGTERM
from daemon import daemon

# Take care of differences between python-daemon versions.
try:
    from daemon import pidfile
except:
    from daemon import pidlockfile

__author__ = 'Georgios Gousios <gousiosg@gmail.com>'


RETRY_ATTEMPTS = 3

#format=('%(asctime)s %(levelname)s %(name)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format=format)
log = logging.getLogger("process")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s(%(process)d) -"
                              "%(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)


class RunFindbugs:
    options = None
    clienttags = []
    chan = None
    conn = None
    closing = False
    amqp_nodes = None
    current_amqp_node = None
    db = None
    msgs = 0
    msgs_acked = 0
    msgs_rejected = 0

    def __init__(self, opts):
        self.options = opts
        self.amqp_nodes = self.options.queue_hosts.split(",")
        self.connect(False)

    def connect(self, same):
        """
        Connects to an AMQP host. The same argument defines whether the host
        to connect to will be the same as the one used before or whether
        a new host from the host list will be tried.
        """
        self._connect_to(same, 1)

    def _connect_to(self, same, depth):
        """
        Connects to an AMQP host.
        """
        if depth > len(self.amqp_nodes):
            log.error("No more nodes to connect to, failing")
            return

        if same is False:
            first = self.amqp_nodes.pop(0)
            self.amqp_nodes.append(first)
            self.current_amqp_node = first

        log.info("Attempting to connect to %s", self.current_amqp_node)
        credentials = pika.PlainCredentials(self.options.queue_uname,
                                            self.options.queue_passwd)
        params = pika.ConnectionParameters(host=self.current_amqp_node,
                                           credentials=credentials,
                                           virtual_host="/")
        try:
            conn = pika.SelectConnection(parameters=params,
                                         on_open_callback=self.on_connected)
            conn.ioloop.start()
        except StatsException:
            self.stats()
            return self._connect_to(True, depth)
        except SystemExit:
            log.info("System exit caught, exiting")
            self.closing = True
            conn.close()
        except Exception:
            log.warn("Could not connect to AMQP node %s" %
                     self.current_amqp_node)
            if same is False:
                return self._connect_to(False, depth + 1)

    def on_connected(self, connection):
        """
        Called when a connection has been succesfully opened. Attempts to
        open a channel.
        """
        self.conn = connection
        self.conn.channel(self.on_channel_open)
        self.conn.add_on_close_callback(self.on_closed)
        log.info("Connection open, opening channel")

    def on_closed(self, frame):
        """
        Called when a connection has been closed, either because the program
        has been shut down or because of an error. In the second case, it
        will retry to connect to the same host for a configurable number of
        times and will then fallback to the remaining AMQP nodes.
        """
        if self.closing:
            log.info("Connection to AMQP closed")
            self.conn.ioloop.stop()
            return

        log.warn("Connection closed unexpectedly, attempting reconnect")
        self.conn = None
        attemts = 0
        while self.conn == None:
            if attemts == RETRY_ATTEMPTS:
                log.warn("Failed all %d attempts to connect to %s, \
                          trying with remaining nodes" %
                         (RETRY_ATTEMPTS, self.current_amqp_node))
                self.connect(False)
                attemts = 0
                continue

            try:
                attemts += 1
                self.connect(True)
            except Exception, e:
                retry = attemts * RETRY_ATTEMPTS
                log.warn("Cannot connect to %s after %d attempts, retrying\
                after %d sec" % (self.current_amqp_node, attemts, retry))
                time.sleep(retry)

    def on_channel_open(self, channel_):
        """
        Called when a channel has been opened.
        """

        self.chan = channel_

        log.info("Setting message prefetch count to 1")
        self.chan.basic_qos(prefetch_count=1)

        log.info("Channel opened, declaring exchanges and queues")
        self.chan.exchange_declare(exchange=self.options.queue_exchange,
                                   type="topic", durable=True,
                                   auto_delete=False)
        # Declare a queue
        self.chan.queue_declare(queue="urls", durable=True,
                                exclusive=False, auto_delete=False,
                                callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        log.info("Queue declared")
        self.chan.queue_bind(callback=self.on_queue_bound,
                             queue='urls', exchange=self.options.queue_exchange,
                             routing_key="url.#")

    def on_queue_bound(self, frame):
        log.info("Binding %s(%s) to queue %s with handler %s",
                  self.options.queue_exchange, "urls" , "urls", "run_findbugs")
        self.chan.basic_consume(self.run_findbugs, queue='urls')

    def run_findbugs(self, channel, method, header, body):
        try:
            body = body.strip()
            file = os.path.basename(body)
            findbugs_output = "%s.xml" % file


            # Download jar
            if not os.path.exists(file):
                log.info("Downloading URL %s to file %s", body, file)
                urllib.urlretrieve(body, file)

            # Exec findbugs
            cmd = '%s -textui -xml -output %s %s' % (os.path.join(os.path.curdir, "findbugs", "bin", "findbugs"), findbugs_output, file)
            log.info("Cmd line: %s" % cmd)
            ret = os.system(cmd)


            # Read output
            findbugs_xml = open(findbugs_output, "r").read()

            # Convert to JSON
            ## XXX: convert xml to json and store it to mongo
            def __convert_findbugs_xml(findbugs_xml):
                import xmldict, json
                return json.loads(json.dumps(xmldict.parse(findbugs_xml)).replace('"@','"'))

            # Save it
            self.store_to_mongo(__convert_findbugs_xml(findbugs_xml))
            channel.basic_ack(method.delivery_tag)
            self.msgs_acked += 1
        except Exception as e:
            log.exception("Unexpected error, msg: %s", body)
            channel.basic_reject(method.delivery_tag)
            self.msgs_rejected += 1
        finally:
            os.remove(findbugs_output)
            os.remove(file)

    def store_to_mongo(self, json):
        if self.db is None:
            self.get_mongo_db()
            if self.db is None:
                log.error("Cannot connect to MongoDB")

        coll = self.db[self.options.mongo_collection]
        coll.insert(json)

    def get_mongo_db(self):
        """
        Gets a connection to MongoDB
        """
        conn = pymongo.Connection(host=self.options.mongo_host,
                                  max_pool_size=10,
                                  network_timeout=1)
        mongo_db = conn[self.options.mongo_db]
        mongo_db.authenticate(self.options.mongo_uname,
                              self.options.mongo_passwd)
        self.db = mongo_db

    def stats(self):
        """
        Prints msg consumption statistics
        """
        log.info("Msgs acked: %d" % self.msgs_acked)
        log.info("Msgs rejected: %d" % self.msgs_rejected)

def _exit_handler(signum, frame):
    """"Catch exit signal in children processes"""
    global log
    log.info("Caught signal %d, will raise SystemExit", signum)
    raise SystemExit


def _usr1_handler(signum, frame):
    global log
    log.info("Caught signal %d, will print statistics to log", signum)
    raise StatsException("stats")

def _parent_handler(signum):
    """"Catch exit signal in parent process and forward it to children."""
    global children

    log.info("Caught signal %d, sending SIGTERM to children %s", signum, children)
    [os.kill(pid, SIGTERM) for pid in children]

class StatsException():
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def parse_arguments(args):
    from argparse import ArgumentParser

    default_pid_file = os.path.join("var", "run", "process", "process.pid")

    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                      dest="debug", help="Enable debug mode")
    parser.add_argument("-p", "--pid-file", dest="pid_file",
                      default=default_pid_file,
                      help="Save PID to file (default: %s)" % default_pid_file)

    # Queue connection info
    parser.add_argument("-a", "--queue-username", required=True,
                      default="", dest="queue_uname",
                      help="Username to connect to the queue")
    parser.add_argument("-b", "--queue-password", required=True,
                      default="", dest="queue_passwd",
                      help="Password to connect to the queue")
    parser.add_argument("-c", "--queue-hosts", required=True,
                      default="127.0.0.1", dest="queue_hosts",
                      help="Comma separated list of hosts running AMQP")
    parser.add_argument("-e", "--queue-exchange", required=True,
                      default="", dest="queue_exchange",
                      help="Exchange name to bind to")

    # MongoDB connection info
    parser.add_argument("-u", "--mongo-username", required=True,
                      default="", dest="mongo_uname",
                      help="Username to connect to MongoDB")
    parser.add_argument("-w", "--mongo-passwd", required=True,
                      default="", dest="mongo_passwd",
                      help="Password to connect to MongoDB")
    parser.add_argument("-x", "--mongo-host", required=True,
                      default="127.0.0.1", dest="mongo_host",
                      help="Host running MongoDB")
    parser.add_argument("-y", "--mongo-database", required=True,
                      default="", dest="mongo_db",
                      help="Database to use for storing messages")
    parser.add_argument("-z", "--mongo-collection", required=True,
                      default="", dest="mongo_collection",
                      help="Collection to use for storing messages")

    return parser.parse_args(args)


def debug(opts):
    signal(SIGINT, _exit_handler)
    signal(SIGUSR1, _usr1_handler)
    signal(SIGTERM, _exit_handler)
    RunFindbugs(opts)

def daemon_mode(opts):
    global children

    # Create pidfile,
    # take care of differences between python-daemon versions
    try:
        pidf = pidfile.TimeoutPIDLockFile(opts.pid_file, 10)
    except:
        pidf = pidlockfile.TimeoutPIDLockFile(opts.pid_file, 10)

    pidf.acquire()

    log.info("Became a daemon")
    # Fork workers
    children = []
    i = 0

    while i < opts.workers:
        newpid = os.fork()
    if newpid == 0:
        signal(SIGINT, _exit_handler)
        signal(SIGTERM, _exit_handler)
        RunFindbugs(opts)
        sys.exit(1)
    else:
        log.debug("%d, forked child: %d", os.getpid(), newpid)
        children.append(newpid)
        i += 1

    # Catch signals to ensure graceful shutdown
    signal(SIGINT, _parent_handler)
    signal(SIGTERM, _parent_handler)

    # Wait for all children processes to die, one by one
    try:
        for pid in children:
            try:
                os.waitpid(pid, 0)
            except Exception:
                pass
    finally:
        pidf.release()


def main():
    opts = parse_arguments(sys.argv[1:])

    # Debug mode, process messages without going to the background
    if opts.debug:
        debug(opts)
        return

    files_preserve = []
    for handler in log.handlers:
        stream = getattr(handler, 'stream')
        if stream and hasattr(stream, 'fileno'):
            files_preserve.append(handler.stream)

    daemon_context = daemon.DaemonContext(
        files_preserve=files_preserve,
        umask=022)

    daemon_context.open()

    # Catch every exception, make sure it gets logged properly
    try:
        daemon_mode(opts)
    except Exception:
        log.exception("Unknown error")
    raise


if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
