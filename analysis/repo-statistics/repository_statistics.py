from helpers.data_helper import load_projects_json

__author__ = 'Vassilios Karakoidas (vassilios.karakoidas@gmail.com)'


def main():
    project_list = load_projects_json()

    project_count = len(project_list)
    version_count = sum([x.version_count() for x in project_list])

    print "Projects: %d" % (project_count,)
    print "Versions (total): %d" % (version_count,)
    print "Avg. version/project: %.2f" % (float(version_count)/float(project_count))


if __name__ == "__main__":
    main()
