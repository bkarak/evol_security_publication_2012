import pymongo

MONGO_HOST   = '83.212.106.194'
MONGO_DB     = 'findbugs'
MONGO_COL    = 'findbugs'
MONGO_UNAME  = 'findbugs'
MONGO_PASSWD = 'findbags'

__author__ = "Vassilios Karakoidas (vassilios.karakoidas@gmail.com)"


class MongoDocumentIterator(object):
    def __init__(self, query=None, fields=None):
        super(MongoDocumentIterator, self).__init__()
        self.__doc_count = 0
        self.__total_count = 0
        self.__connection = get_mongo_connection()
        self.__collection = self.__connection[MONGO_COL]

        if fields is None:
            self.__fields = []
        else:
            self.__fields = fields

        if query is None:
            self.__query = {}
        else:
            self.__query = query

        self.__count_documents()

    def __count_documents(self):
        try:
            self.__total_count = self.__collection.find(self.__query, timeout=False).count()
        except pymongo.errors.AutoReconnect, ar:
            print '__count_documents() - %s (reconnecting)' % (ar,)

    def reset(self):
        self.__doc_count = 0


    def has_next(self):
        return self.__doc_count < self.__total_count

    def next(self):
        try:
            d = None

            for c in self.__collection.find(self.__query, skip=self.__doc_count, limit=1, fields=self.__fields):
                d = c

            self.__doc_count += 1

            return d
        except pymongo.errors.AutoReconnect, ar:
            print 'next() - %s (reconnecting)' % (ar,)
            return None

    def total(self):
        return self.__total_count

    def count(self):
        return self.__doc_count


class MongoProjectIterator(MongoDocumentIterator):
    def __init__(self, group_id, artifact_id, query=None, fields=None):
        __q = {'JarMetadata.group_id': group_id,
               'JarMetadata.artifact_id': artifact_id}

        __f = ['JarMetadata.version_order']

        if query is not None:
            __q.update(query)

        if fields is not None:
            __f.extend(fields)

        super(MongoProjectIterator, self).__init__(query=__q,fields=__f)

    def documents_list(self):
        docs = []

        while self.has_next():
            d = self.next()

            if d is not None:
                docs.append(d)

        docs.sort(key=lambda doc: doc['JarMetadata']['version_order'])

        return docs


def get_mongo_connection():
    """
    Gets a connection to MongoDB
    """
    conn = pymongo.Connection(host=MONGO_HOST, max_pool_size=10)
    mongo_db = conn[MONGO_DB]
    mongo_db.authenticate(MONGO_UNAME, MONGO_PASSWD)

    return mongo_db


def get_project_versions(col_obj, group_id, artifact_id):
    try:
        result = []
        q = {'JarMetadata.group_id' : group_id,
             'JarMetadata.artifact_id' : artifact_id}

        for c in col_obj.find(q, timeout=False):
            result.append(c)

        return result
    except pymongo.errors.AutoReconnect, ae:
        print 'Mongo Connection is Down. Reconnecting! (record_exists, %s)' % (ae,)
        return get_project_versions(col_obj, group_id, artifact_id)


def get_version(col_obj, group_id, artifact_id, version):
    try:
        result = []

        q = {'JarMetadata.group_id': group_id,
             'JarMetadata.artifact_id': artifact_id,
             'JarMetadata.version': version}

        for c in col_obj.find(q, fields=[], timeout=False):
            result.append(c)

        return result
    except pymongo.errors.AutoReconnect, ae:
        print 'Mongo Connection is Down. Reconnecting! (record_exists, %s)' % (ae,)
        return get_project_versions(col_obj, group_id, artifact_id)

