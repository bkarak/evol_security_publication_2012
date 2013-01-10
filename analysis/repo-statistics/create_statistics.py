import mongo_helper, json, data_helper


def load_projects():
    fp = open('projects.json', 'r')
    buf = fp.read()
    fp.close()

    return json.loads(buf)

def main():
    mongo_db = mongo_helper.get_mongo_db()
    col = mongo_db[mongo_helper.MONGO_COL]
    arrayCount = data_helper.ArrayCount()
    ga_projects = load_projects()
    ga_project_count = len(ga_projects)
    ga_counter = 0
    ga_valid = 0

    for ga in ga_projects:
        group_id = ga['group_id']
        artifact_id = ga['artifact_id']
        versions = mongo_helper.get_project_versions(col, group_id, artifact_id)
        no_versions = len(versions)
        ga_counter += 1

        if no_versions > 0:
            ga_valid += 1
            print '[%d:%d:%d] -> group_id: %s, artifact_id: %s, versions: %d' % (ga_counter, ga_valid, ga_project_count, group_id, artifact_id, no_versions)
            arrayCount.incr(no_versions)

    data = arrayCount.get_series()
    data_helper.save_to_file('version_count.json', json.dumps(data))

if __name__ == "__main__":
    main()
