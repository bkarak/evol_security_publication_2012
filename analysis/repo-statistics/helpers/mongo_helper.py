import pymongo

MONGO_HOST   = '83.212.106.194'
MONGO_DB     = 'findbugs'
MONGO_COL    = 'findbugs'
MONGO_UNAME  = 'findbugs'
MONGO_PASSWD = 'findbags'


class MongoDocumentIterator(object):
    def __init__(self):
        super(MongoDocumentIterator, self).__init__()
        self.__doc_count = 0
        self.__total_count = 0
        self.__connection = get_mongo_connection()
        self.__collection = self.__connection[MONGO_COL]
        self.__count_documents()

    def __count_documents(self):
        try:
            self.__total_count = self.__collection.find(timeout=False).count()
        except pymongo.errors.AutoReconnect, ar:
            print '__count_documents() - %s (reconnecting)' % (ar,)

    def reset(self):
        self.__doc_count = 0

    def has_next(self):
        return self.__doc_count < self.__total_count

    def next(self):
        try:
            d = None

            for c in self.__collection.find(skip=self.__doc_count, limit=1, fields=['JarMetadata.group_id', 'JarMetadata.artifact_id']):
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


def get_mongo_connection():
    """
    Gets a connection to MongoDB
    """
    conn = pymongo.Connection(host=MONGO_HOST, max_pool_size=10)
    mongo_db = conn[MONGO_DB]
    mongo_db.authenticate(MONGO_UNAME, MONGO_PASSWD)

    return mongo_db


#def get_mongo_client():
#    pymongo.MongoClient(host=MONGO_HOST, )


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
