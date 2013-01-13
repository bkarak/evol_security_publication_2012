from helpers.data_helper import load_projects_json

__author__ = 'Vassilios Karakoidas (vassilios.karakoidas@gmail.com)'


def main():
    project_list = load_projects_json()

    project_count = len(project_list)
    version_list = [x.version_count() for x in project_list]
    version_count = sum(version_list)
    max_version = max(version_list)
    min_version = min(version_list)

    print "Projects: %d" % (project_count,)
    print "Versions (total): %d" % (version_count,)
    print "Avg. Version/Project: %.2f" % (float(version_count)/float(project_count))
    print "Max. Version Count: %d" % (max_version,)
    print "Min. Version Count: %d" % (min_version,)


if __name__ == "__main__":
    main()
