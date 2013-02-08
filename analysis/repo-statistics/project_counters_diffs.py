import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math

bug_types_diffs = {
    'SECURITY_HIGH': [],
    'SECURITY_LOW': [],
    'MALICIOUS_CODE': [],
    'STYLE': [],
    'CORRECTNESS': [],
    'BAD_PRACTICE': [],
    'MT_CORRECTNESS': [],
    'I18N': [],
    'PERFORMANCE': [],
    'EXPERIMENTAL': []
    }


with open("data/project_counters.json", "r") as json_file:
    json_input = json.load(json_file)
    diffs = {}
    for project, data in json_input.iteritems():
        project_count = []
        diffs[project] = {}
        bad_project = False
        for version in data['versions']:
            if bad_project == True:
                diffs[project] = {}
                break
            version_order = version['JarMetadata']['version_order']
            if version_order == 0:
                bad_project = True
                continue
            project_count.append({})
            counters = version['Counters']
            for counter, value in counters.iteritems():
                cur =  version_order - 1
                if version_order != len(project_count):
                    bad_project = True
                    break
                else:
                    project_count[cur][counter] = value
            if version_order > 1:
                counters_to_check = set()
                last_couple = project_count[cur-1:cur+1]
                counters_to_check = reduce(lambda x, y: x.union(y.keys()),
                                           last_couple,
                                           set())
                for counter_to_check in counters_to_check:
                    prev_counts = project_count[cur - 1] 
                    prev_value = prev_counts.get(counter_to_check, 0)
                    cur_counts = project_count[cur]
                    cur_value = cur_counts.get(counter_to_check, 0)
                    diff = cur_value - prev_value
                    if not (diff == 0 and cur_value == 0):
                        d = diffs[project].setdefault(counter_to_check, [])
                        d.append(diff)
                    # if counter_to_check not in diffs[project]:
                    #     diffs[project][counter_to_check] = [diff]
                    # else:
                    #     diffs[project][counter_to_check].append(diff)

for project, project_diffs in diffs.iteritems():
    for counter, counter_diffs in project_diffs.iteritems():
        bug_types_diffs[counter].extend(counter_diffs)

for bug_type, bug_type_diffs in bug_types_diffs.iteritems():
    cd_arr = np.array(bug_type_diffs)
    hist = np.histogram(cd_arr)
    percentiles = [st.scoreatpercentile(cd_arr, p) for p in [1, 25, 50, 75, 99]]
    print bug_type, st.describe(cd_arr), percentiles, hist
    nz_cd_arr = cd_arr[np.nonzero(cd_arr)]
    hist = np.histogram(nz_cd_arr)
    percentiles = [st.scoreatpercentile(nz_cd_arr, p)
                   for p in [1, 25, 50, 75, 99]]
    print bug_type, st.describe(nz_cd_arr), percentiles, hist


plt.figure(1, figsize=(16, 12))

num_plots = len(bug_types_diffs.keys()) * 2
num_cols = 4
num_rows = num_plots / num_cols
if num_rows % num_cols != 0:
    num_rows += 1
num_plot = 1
for bug_type, bug_type_diffs in bug_types_diffs.iteritems():
    cd_arr = np.array(bug_type_diffs)
    plt.subplot(num_rows, num_cols, num_plot)
    plt.hist(cd_arr, 30, log=True)
    plt.title(bug_type)

    num_plot += 1
    nz_cd_arr = cd_arr[np.nonzero(cd_arr)]
    plt.subplot(num_rows, num_cols, num_plot)
    plt.hist(nz_cd_arr, 30, log=True, alpha=0.5)
    # plt.boxplot(diffs)
    plt.title(bug_type)
    num_plot += 1

plt.tight_layout()    
plt.show()
