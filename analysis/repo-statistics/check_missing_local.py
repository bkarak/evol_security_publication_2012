import os
import xmldict

from helpers.mongo_helper import get_version, get_mongo_connection, MONGO_COL

def main():
    base_url = '/Users/bkarak/devel/repositories/maven/maven/'
    col_obj = get_mongo_connection()[MONGO_COL]
    fp = open('data/missing_versions.txt', 'r')

    total_jars = 0
    missing = 0
    really_missing = 0

    for line in fp:
        (group_id, artifact_id) = line.strip().split('||')
        maven_base_url = '%s%s/%s/' % (base_url, group_id.replace('.', '/'), artifact_id)
        maven_metadata_name = '%smaven-metadata.xml' % (maven_base_url,)

        if not os.path.exists(maven_metadata_name):
            continue

        json_xml = xmldict.parse(open(maven_metadata_name, 'r').read())
        versions = json_xml.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version')
        version_list = []

        if isinstance(versions, list):
            version_list.extend(versions)
        else:
            version_list.append(versions)

        for v in version_list:
            docs = get_version(col_obj, group_id, artifact_id, v)
            total_jars += 1

            if len(docs) == 0:
                missing += 1
                #print '[%d]: Missing %s||%s||%s' % (total_jars, group_id, artifact_id, v)
                local_jar_path = '%s%s/%s-%s.jar' % (maven_base_url, v, artifact_id, v)

                if not os.path.exists(local_jar_path):
                    really_missing += 1
                else:
                    print "findbugs -textui -xml -output `basename %s`-findbugs.xml %s" % (local_jar_path, local_jar_path)

    fp.close()

    #print 'Total: %d, Missing: %d (%d)' % (total_jars, missing - really_missing, missing)


if __name__ == "__main__":
    main()
