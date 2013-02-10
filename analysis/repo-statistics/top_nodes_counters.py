import csv

from helpers.data_helper import load_vuln_projects_json, ArrayCount, save_to_file
from helpers.mongo_helper import MongoProjectIterator

def main():
    projects = load_vuln_projects_json()
    results = {}

    with open('data/graph-results.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            for field in row[0].split("||"):
                print field
