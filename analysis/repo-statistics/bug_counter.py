from helpers.mongo_helper import MongoDocumentIterator

__author__ = 'Vassilios Karakoidas (vassilios.karakoidas@gmail.com)'


def main():
    miter = MongoDocumentIterator(fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version','BugCollection.BugInstance.category', 'BugCollection.BugInstance.type', 'BugCollection.BugInstance.type'])

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        print d

if __name__ == "__main__":
    main()
