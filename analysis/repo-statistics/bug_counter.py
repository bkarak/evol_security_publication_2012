from helpers.mongo_helper import MongoDocumentIterator

__author__ = 'Vassilios Karakoidas (vassilios.karakoidas@gmail.com)'


def main():
    miter = MongoDocumentIterator(query={'BugCollection.BugInstance.category':'SECURITY'}, fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version','BugCollection.BugInstance.category', 'BugCollection.BugInstance.type'])

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        bug_counter = 0

        for bi in d.get('BugCollection', {}).get('BugInstance', []):
            if not isinstance(bi, dict):
                print d
                continue

            if bi.get('category', '') == 'SECURITY':
                bug_counter += 1

        print '%s/%s-%s.jar: %d' % (d['JarMetadata']['group_id'], d['JarMetadata']['artifact_id'], d['JarMetadata']['version'], bug_counter)

if __name__ == "__main__":
    main()
