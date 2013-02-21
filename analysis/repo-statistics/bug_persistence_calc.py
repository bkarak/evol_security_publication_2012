# Extracts the bug counters data from the JSON representation
# and outputs them in CSV format so that it can be read by R.

import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import collections
import itertools

bug_types_closed = {
        'SECURITY': [],
        'MALICIOUS_CODE': [],
        'STYLE': [],
        'CORRECTNESS': [],
        'BAD_PRACTICE': [],
        'MT_CORRECTNESS': [],
        'I18N': [],
        'PERFORMANCE': [],
        'EXPERIMENTAL': []
        }

projects_closed = set()

with open("data/bug_persistence.json", "r") as json_file:
    json_input = json.load(json_file, object_pairs_hook=collections.OrderedDict)
    bugs_opened = {}
    prev_project = ''
    for project_version, data in json_input.iteritems():
        project = project_version.rpartition('||')[0]
        if project != prev_project:
            bugs_opened = {}
            projects_closed.add(prev_project)
            if project in projects_closed:
                print project, "met again!"
            prev_project = project
        version_order = data.get('version_order', 0)
        #print project_version, version_order
        if version_order == 0:
            continue
        bugs = data['Bugs']
        for bug in bugs_opened.keys():
            if bug not in bugs:
                bug_type = bug.partition('||')[0]
                diff = version_order - bugs_opened[bug]
                bug_types_closed[bug_type].append(diff)
                if diff < 1:
                    print (project, bug_type, diff, version_order,
                           bugs_opened[bug])
                del bugs_opened[bug]
        for bug in bugs:
            if bug not in bugs_opened:
                bugs_opened[bug] = version_order

bug_combinations = itertools.combinations(bug_types_closed.keys(), 2)

bug_type_arrays = {}
bug_type_means = {}
bug_type_desc = {}

for bug_type, bugs_closed in bug_types_closed.iteritems():
    bug_type_arrays[bug_type] = np.array(bugs_closed)
    bug_type_desc[bug_type] = st.describe(bugs_closed)

for b1, b2 in bug_combinations:
    z_stat, p_val = st.ranksums(bug_type_arrays[b1],
                                bug_type_arrays[b2])
    print b1, b2, z_stat, p_val, bug_type_desc[b1], bug_type_desc[b2]

