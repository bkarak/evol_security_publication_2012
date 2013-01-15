import os, json

__author__ = "Vassilios Karakoidas (vassilios.karakoidas@gmail.com)"

class ArrayCount(object):
    def __init__(self):
        super(ArrayCount, self).__init__()
        self.__arrayDict = {}

    def incr(self, item):
        self.__arrayDict[item] = self.__arrayDict.get(item, 0) + 1

    def get_series(self):
        return self.__arrayDict

    def item_count(self):
        return len(self.__arrayDict)

    def value_count(self):
        return sum(self.__arrayDict.values())


def save_to_file(filename, data):
    fp = open(filename, 'w')
    fp.write(data)
    fp.close()


def load_projects_json():
    from models.project import Project

    if not os.path.exists('data/project_versions.json'):
        print '[ERROR]: data/projects.json does not exist!'
        return []

    project_list = []
    fp = open('data/projects.json', 'r')
    prj_json = json.load(fp)
    fp.close()

    for (k, v) in prj_json.iteritems():
        project_list.append(Project.parse_project(k, v))

    return project_list

