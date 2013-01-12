

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
