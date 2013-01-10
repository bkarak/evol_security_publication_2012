import pymongo

MONGO_HOST   = '83.212.106.194'
MONGO_DB     = 'findbugs'
MONGO_COL    = 'findbugs'
MONGO_UNAME  = 'findbugs'
MONGO_PASSWD = 'findbags'


def get_mongo_db():
    """
    Gets a connection to MongoDB
    """
    conn = pymongo.Connection(host=MONGO_HOST, max_pool_size=10, network_timeout=1)
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
