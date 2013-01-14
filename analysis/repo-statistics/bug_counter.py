from helpers.mongo_helper import MongoDocumentIterator

__author__ = 'Vassilios Karakoidas (vassilios.karakoidas@gmail.com)'


def main():
    miter = MongoDocumentIterator(query={'$or: {'BugCollection.BugInstance.category':'MALICIOUS_CODE'}, {'BugCollection.BugInstance.category':'SECURITY'}'}, fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version','BugCollection.BugInstance.category', 'BugCollection.BugInstance.type'])

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        sec_bug_counter = 0
        mal_bug_counter = 0
        total_counter = 0

        for bi in d.get('BugCollection', {}).get('BugInstance', []):
            total_counter += 1

            if not isinstance(bi, dict):
                print bi
                continue

            if bi.get('category', '') == 'SECURITY':
                bug_counter += 1
                
            if bi.get('category', '') == 'MALICIOUS_CODE':
                bug_counter += 1

        print '%s/%s-%s.jar: sec: %d mal: %d (total:%d)' % (d['JarMetadata']['group_id'], d['JarMetadata']['artifact_id'], d['JarMetadata']['version'], sec_bug_counter, mal_bug_counter, total_counter)

if __name__ == "__main__":
    main()
