import csv
import json

def main():
    with open("data/project_counters.json") as data_file:
        data = json.load(data_file)

    with open('data/graph-results.csv', 'rb') as f:
        reader = csv.reader(f)
        counter = 0
        for row in reader:
            counter = counter + 1
            try:
                (agroup_id,artifact,version) = row[0].split("||")
                print "%s %s %s" % (agroup_id,artifact,version)
                print row[1]
                print row[2]
                print row[3]
            except:
                pass
            if counter == 50:
                break

if __name__== "__main__":
 main()
