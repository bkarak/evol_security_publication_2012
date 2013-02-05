# Extracts the bug counters data from the JSON representation
# and outputs them in CSV format so that it can be read by R.

import ijson
import json
import sys
import csv

bug_types = set()

def get_bug_type(prefix):
    return prefix[prefix.rfind(".") + 1:]

with open("data/project_counters.json", "r") as json_file:
    json_input = json.load(json_file)
    for project, data in json_input.iteritems():
        for version in data['versions']:
            counters = version['Counters']
            for counter in counters:
                bug_types.add(counter)
 
    with open("data/project_counters_jarsize.csv", "w") as csv_output:
        csvwriter = csv.writer(csv_output)        
        project_counts = {}
        project_key = ""
        row = ['project', 'version', 'jarsize']
        for bug_type in bug_types:
            row.append(bug_type)
        csvwriter.writerow(row)
        for project, data in json_input.iteritems():
            for version in data['versions']:
                meta_data = version['JarMetadata']                    
                row = [project, meta_data['version_order'],
                       meta_data['jar_size']]
                counters = version['Counters']
                for bug_type in bug_types:
                    bug_count = counters[bug_type] \
                        if bug_type in counters else 'NA'
                    row.append(bug_count)
                csvwriter.writerow(row)
            
