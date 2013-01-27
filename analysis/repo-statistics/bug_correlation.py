import json

from helpers.data_helper import ArrayCount, save_to_file
from helpers.mongo_helper import MongoDocumentIterator



def main():

miter = MongoDocumentIterator(query={''},fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.version_order', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type', 'BugCollection.BugInstance.Class.classname','BugCollection.BugInstance.priority'])

    print 'Found %d Documents' % (miter.total(),)
    
    while miter.has_next():

if __name__ == "__main__":
    main()
