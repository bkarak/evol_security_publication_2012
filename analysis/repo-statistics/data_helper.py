

class ArrayCount(object):
    def __init__(self):
        super(ArrayCount, self).__init__()
        self.__arrayDict = {}

    def incr(self, counter):
        self.__arrayDict[counter] = self.__arrayDict.get(counter, 0) + 1

    def get_series(self):
        return self.__arrayDict


def save_to_file(filename, data):
    fp = open(filename, 'w')
    fp.write(data)
    fp.close()
