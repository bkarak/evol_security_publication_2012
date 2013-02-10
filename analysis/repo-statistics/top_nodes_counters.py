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
                (a,b,c) = row[0].split("||")
                print "%s %s %s" % (a,b,c)
            except:
                pass
            if counter == 50:
                break

if __name__== "__main__":
 main()
