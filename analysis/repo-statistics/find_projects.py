import json

def main():
    results = {}
    fp = open('maven_jars_only.text', 'r')

    for l in fp:
        try:
            data_arr = l.split(' maven/')[1].strip().split('/')

            group_id = data_arr[-4]
            artifact_id = data_arr[-3]

            project_key = '%s.%s' % (group_id, artifact_id)

            if project_key not in results:
                results[project_key] = {'group_id':group_id, 'artifact_id':artifact_id}
                print 'Found %d Projects' % (len(results,))
        except (IndexError, ValueError), e:
            print 'ERROR: %s' % (l.strip(),)

    fp.close()

    fp = open('projects.json', 'w')
    fp.write(json.dumps(results.values()))
    fp.close()


if __name__ == "__main__":
    main()
