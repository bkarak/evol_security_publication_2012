import json, data_helper, mongo_helper



def main():
    results = data_helper.ArrayCount()
    miter = mongo_helper.MongoDocumentIterator()

    print 'Found %d Documents' % (miter.total(),)

    while miter.has_next():
        d = miter.next()

        if d is not None:
            group_id = d['JarMetadata']['group_id']
            artifact_id = d['JarMetadata']['artifact_id']
            ga = '%s||%s' % (group_id, artifact_id)
            results.incr(ga)
            print 'Working %d of %d' % (miter.count(), miter.total(), )

    data_helper.save_to_file('new_projects.json', json.dumps(results.get_series()))


if __name__ == "__main__":
    main()
