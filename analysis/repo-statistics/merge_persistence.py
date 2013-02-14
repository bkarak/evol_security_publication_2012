import json
from helpers.data_helper import save_to_file


def main():
    json_graph = json.load(open('data/project_counters_31.json', 'r'))
    json_persistence = json.load(open('data/bug_persistence.json', 'r'))

    for (k, v) in json_graph.iteritems():
        #print 'Processing %s' % (k,)
        for vv in v['versions']:
            metadata = vv.get('JarMetadata', None)
            key = '%s||%s||%s' % (metadata['group_id'], metadata['artifact_id'], metadata['version'])
            version_order = metadata['version_order']
            #print '%s:%s' % (key, version_order)

            if key in json_persistence:
                json_persistence[key]['version_order'] = version_order
                print 'Found %s' % (key,)
            else:
                print '%s not found!' % (key,)

    save_to_file('bug_persistence_altered.json', json.dumps(json_persistence))


if __name__ == "__main__":
    main()
