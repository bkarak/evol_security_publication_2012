import json

from helpers.data_helper import load_vuln_projects_json, ArrayCount, save_to_file
from helpers.mongo_helper import MongoProjectIterator


def main():
    projects = load_vuln_projects_json()
    results = {}

    total_projects = len(projects)
    count = 0
    print 'Found %d Projects' % (total_projects,)

    for p in projects:
        piter = MongoProjectIterator(p.group_id(), p.artifact_id(), fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.jar_size', 'JarMetadata.version_order', 'JarMetadata.jar_last_modification_date', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type', 'BugCollection.BugInstance.priority'])
        doc_list = piter.documents_list()
        documents = []
        count += 1

        print '[%d:%d] %s||%s: %d versions' % (count, total_projects, p.group_id(), p.artifact_id(), len(doc_list))

        for d in doc_list:
            doc_results = {'JarMetadata': d['JarMetadata']}
            doc_array_count = ArrayCount()

            for bi in d.get('BugCollection', {}).get('BugInstance', []):
                if not isinstance(bi, dict):
                    print bi
                    continue

                bug_category = bi.get('category', None)

                if bug_category is not None:
                    if bug_category == 'SECURITY' or bug_category == 'MALICIOUS_CODE':
                        doc_array_count.incr('SECURITY')
                    else:
                        doc_array_count.incr(bug_category)

            doc_results['Counters'] = doc_array_count.get_series()
            documents.append(doc_results)

        key = '%s||%s' % (p.group_id(), p.artifact_id())
        results[key] = {'group_id' : p.group_id(),
                        'artifact_id' : p.artifact_id(),
                        'version_count' : len(doc_list),
                        'versions' : documents}

        # TODO: uncomment this to print out each entry
        #print results

    save_to_file('project_counters_2.json', json.dumps(results))


if __name__ == "__main__":
    main()
