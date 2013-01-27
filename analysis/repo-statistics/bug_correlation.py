import json

from helpers.data_helper import ArrayCount, save_to_file, load_projects_json
from helpers.mongo_helper import MongoProjectIterator


def main():
    projects = load_projects_json()
    results = {}
    total_projects = len(projects)
    count = 0

    print 'Found %d Projects' % (total_projects,)

    for p in projects:
        piter = MongoProjectIterator(p.group_id(), p.artifact_id(), fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.version_order', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type', 'BugCollection.BugInstance.Class.classname','BugCollection.BugInstance.priority'])
        doc_list = piter.documents_list()
        proj_array_count = ArrayCount()
        bug_list = []
        count += 1

        print '[%d:%d] %s||%s: %d versions' % (count, total_projects, p.group_id(), p.artifact_id(), len(doc_list))

        for d in doc_list:
            for bi in d.get('BugCollection', {}).get('BugInstance', []):
                if not isinstance(bi, dict):
                    print 'Invalid BugInstance (%s)' % (bi,)
                    continue

                bug_category = bi.get('category', '')

                # get class names
                classnames = bi['Class']
                classresults = []

                if isinstance(classnames, list):
                    for c in classnames:
                        classresults.append(c.get('classname', 'NotSet'))
                elif isinstance(classnames, dict):
                    classresults.append(classnames.get('classname', 'NotSet'))

                type = bi['type']
                signatures = ['%s||%s||%s' % (bug_category, type, c) for c in classresults]

                # method
                for s in signatures:
                    if s not in bug_list:
                        bug_list.append(s)

                        if bug_category == 'SECURITY' or bug_category == 'MALICIOUS_CODE':
                            proj_array_count.incr('SECURITY')
                        else:
                            proj_array_count.incr(bug_category)

        results['%s||%s' % (p.group_id(), p.artifact_id())] = proj_array_count.get_series()

    save_to_file('bug_correlation_counters.json', json.dumps(results))


if __name__ == "__main__":
    main()
