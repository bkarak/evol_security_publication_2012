import json


def main():
    fp_two = open('data/project_versions.json', 'r')
    project_json = json.load(fp_two)
    fp = open('data/bugless_projects.json', 'r')

    total_projects = 0
    version_count = 0

    for l in fp:
        version_count += project_json.get(l.strip(), 0)
        total_projects += 1

    fp.close()
    fp_two.close()

    print 'Total Projects: %d, Version: %d' % (total_projects, version_count)


if __name__ == "__main__":
    main()
