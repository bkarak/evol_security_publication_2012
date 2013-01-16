import json

from helpers.data_helper import load_vuln_projects_json, ArrayCount, save_to_file
from helpers.mongo_helper import MongoProjectIterator


def main():
    projects = load_vuln_projects_json()
    results = []
    security_bugs = ['HRS_REQUEST_PARAMETER_TO_COOKIE',
                     'HRS_REQUEST_PARAMETER_TO_HTTP_HEADER',
                     'PT_ABSOLUTE_PATH_TRAVERSAL',
                     'SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE',
                     'SQL_PREPARED_STATEMENT_GENERATED_FROM_NONCONSTANT_STRING',
                     'XSS_REQUEST_PARAMETER_TO_JSP_WRITER',
                     'XSS_REQUEST_PARAMETER_TO_SEND_ERROR',
                     'XSS_REQUEST_PARAMETER_TO_SERVLET_WRITER']

    print 'Found %d Projects' % (len(projects),)

    for p in projects:
        piter = MongoProjectIterator(p.group_id(), p.artifact_id(), fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.jar_size', 'JarMetadata.version_order', 'JarMetadata.jar_last_modification_date', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type', 'BugCollection.BugInstance.Class'])
        doc_list = piter.documents_list()
        print 'Project: %s||%s: %d documents' % (p.group_id(), p.artifact_id(), len(doc_list))

        for d in doc_list:
            doc_results = {'JarMetadata': d['JarMetadata']}
            doc_array_count = ArrayCount()
            sec_instances = []

            for bi in d.get('BugCollection', {}).get('BugInstance', []):
                if not isinstance(bi, dict):
                    print bi
                    continue

                bug_category = bi.get('category', '')

                # method
                if bug_category == 'SECURITY' or bug_category == 'MALICIOUS_CODE':
                    sec_dict = {'Category' : bug_category,
                                'Type' : bi.get('type', ''),
                                'Class' : bi.get('Class', {})}
                    sec_instances.append(sec_dict)

                # counters
                if bug_category == 'SECURITY':
                    bug_type = bi.get('type', None)

                    if bug_type is None:
                        print 'Invalid Type!'
                        continue

                    if bug_type in security_bugs:
                        doc_array_count.incr('SECURITY_HIGH')
                    else:
                        doc_array_count.incr('SECURITY_LOW')
                else:
                    doc_array_count.incr(bug_category)

            doc_results['Counters'] = doc_array_count.get_series()
            doc_results['SecurityBugs'] = sec_instances

            print doc_results
            results.append(doc_results)

    save_to_file('project_counters.json', json.dumps(results))


if __name__ == "__main__":
    main()
