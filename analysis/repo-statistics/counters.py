from helpers.mongo_helper import MongoDocumentIterator

__author__ = 'Dimitris Mitropoulos (dimitro@aueb.gr)'


def main():
    miter = MongoDocumentIterator(query={'BugCollection.BugInstance.category':'MALICIOUS_CODE'},fields=['JarMetadata.group_id', 'JarMetadata.artifact_id', 'JarMetadata.version', 'JarMetadata.jar_size', 'JarMetadata.version_order', 'JarMetadata.jar_last_modification_date', 'BugCollection.BugInstance.category', 'BugCollection.BugInstance.type'])

    print 'Found %d Documents' % (miter.total(),)
    
    while miter.has_next():
        d = miter.next()
        
        # counter for all bugs
        total_counter = 0
        
        # SECURITY category counters
        sec_high_bug_counter = 0
        sec_low_bug_counter = 0
        sec_total_counter = 0
        both_categories = 0
        
        # MALICIOUS_CODE
        mal_bug_counter = 0
        
        # BAD_PRACTICE
        bad_practice_counter = 0
        
        # PERFORMANCE
        perform_counter = 0
        
        # CORRECTNESS
        correctness_counter = 0
        
        #STYLE
        style_counter = 0
        
        # Internationalization - I18N
        inter_counter = 0
        
        # MT_CORRECTNESS
        multi_counter = 0 

        for bi in d.get('BugCollection', {}).get('BugInstance', []):
            total_counter += 1

            if not isinstance(bi, dict):
                print bi
                continue

            if bi.get('category', '') == 'SECURITY':
                if (bi.get('type', '') == 'HRS_REQUEST_PARAMETER_TO_COOKIE') or (bi.get('type', '') == 'HRS_REQUEST_PARAMETER_TO_HTTP_HEADER') or (bi.get('type', '') == 'PT_ABSOLUTE_PATH_TRAVERSAL') or (bi.get('type', '') == 'SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE') or (bi.get('type', '') == 'SQL_PREPARED_STATEMENT_GENERATED_FROM_NONCONSTANT_STRING') or (bi.get('type', '') == 'XSS_REQUEST_PARAMETER_TO_JSP_WRITER') or (bi.get('type', '') == 'XSS_REQUEST_PARAMETER_TO_SEND_ERROR') or (bi.get('type', '') == 'XSS_REQUEST_PARAMETER_TO_SERVLET_WRITER'):
                    sec_high_bug_counter += 1
                else:
                    sec_low_bug_counter += 1
                
            if bi.get('category', '') == 'MALICIOUS_CODE':
                mal_bug_counter += 1
                
            if bi.get('category', '') == 'BAD_PRACTICE':
                bad_practice_counter += 1
            
            if bi.get('category', '') == 'PERFORMANCE':
                perform_counter += 1
                
            if bi.get('category', '') == 'CORRECTNESS':
                correctness_counter += 1
                
            if bi.get('category', '') == 'STYLE':
                style_counter += 1
                
            if bi.get('category', '') == 'I18N':
                inter_counter += 1
                
            if bi.get('category', '') == 'MT_CORRECTNESS':
                multi_counter += 1
                
        sec_total_counter = sec_high_bug_counter + sec_low_bug_counter
        both_categories = sec_total_counter + mal_bug_counter

        print '%s/%s-%s.jar. Data: size %d order %d and last modification date %d Bugs: sec / high %d sec / high: %d sec / total %d mal: %d from both categories %d (total:%d)' % (d['JarMetadata']['group_id'], d['JarMetadata']['artifact_id'], d['JarMetadata']['version'], d['JarMetadata']['jar_size'], d['JarMetadata']['version_order'], d['JarMetadata']['jar_last_modification_date'], sec_high_bug_counter, sec_low_bug_counter, sec_total_counter, mal_bug_counter, both_categories, total_counter)
        
        print 'bad practice bugs: %d performance bugs: %d correctness bugs: %d style bugs: %d internationalization bugs: %d multithreaded bugs: %d' % (bad_practice_counter, perform_counter, correctness_counter, style_counter, inter_counter, multi_counter)
        
if __name__ == "__main__":
    main()
