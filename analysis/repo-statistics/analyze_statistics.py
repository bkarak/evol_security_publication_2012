import json

def main():
    fp = open('version_count.json', 'r')
    json_data = json.load(fp)
    fp.close()

    project_count = 0

    for (k, v) in json_data.iteritems():
        project_count += (int(k)*v)

    print project_count

if __name__ == "__main__":
    main()
