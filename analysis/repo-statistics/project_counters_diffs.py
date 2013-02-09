import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math
from collections import defaultdict

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

diffs = {}
counts = {}

counts_corrs = {}

with open("data/project_counters.json", "r") as json_file:
    json_input = json.load(json_file)
    for project, data in json_input.iteritems():
        counts[project] = []
        diffs[project] = defaultdict(list)
        bad_project = False
        for version in data['versions']:
            if bad_project == True:
                diffs[project] = {}
                break
            version_order = version['JarMetadata']['version_order']
            if version_order == 0:
                bad_project = True
                continue
            counts[project].append({})
            counters = version['Counters']
            for counter, value in counters.iteritems():
                cur =  version_order - 1
                if version_order != len(counts[project]):
                    bad_project = True
                    break
                else:
                    counts[project][cur][counter] = value
            if version_order > 1:
                counters_to_check = set()
                last_couple = counts[project][cur-1:cur+1]
                counters_to_check = reduce(lambda x, y: x.union(y.keys()),
                                           last_couple,
                                           set())
                for counter_to_check in counters_to_check:
                    prev_counts = counts[project][cur - 1] 
                    prev_value = prev_counts.get(counter_to_check, 0)
                    cur_counts = counts[project][cur]
                    cur_value = cur_counts.get(counter_to_check, 0)
                    diff = cur_value - prev_value
                    if not (diff == 0 and cur_value == 0):
                         diffs[project][counter_to_check].append(diff)

for project, project_counts in counts.iteritems():
    counter_evol = defaultdict(list)
    for version_counts in project_counts:
        for counter, counter_count in version_counts.iteritems():
            counter_evol[counter].append(counter_count)
    for counter, counter_counts in counter_evol.iteritems():
        cc_arr = np.array(counter_counts)        
        if len(cc_arr) > 1:
            (rho, p_value) = st.spearmanr(cc_arr, np.arange(1, len(cc_arr)+1))
            if p_value < 0.05:
                counts_corrs.setdefault(counter, []).append(rho)
                #print project, counter, len(cc_arr), cc_arr, rho, p_value
        
for project, project_diffs in diffs.iteritems():
    for counter, counter_diffs in project_diffs.iteritems():
        bug_types_diffs[counter].extend(counter_diffs)

counts_corrs_arr = np.array(counts_corrs)
        
for bug_type, bug_type_diffs in bug_types_diffs.iteritems():
    cd_arr = np.array(bug_type_diffs)
    hist = np.histogram(cd_arr)
    percentiles = [st.scoreatpercentile(cd_arr, p) for p in [1, 25, 50, 75, 99]]
    print bug_type, st.describe(cd_arr), percentiles, hist


fig1 = plt.figure(1, figsize=(16, 10))
fig1.suptitle("Log histograms of bug ticks", fontsize=16, y=0.06)

num_plots = len(bug_types_diffs.keys())
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

fig2 = plt.figure(2, figsize=(16, 10))
fig2.suptitle("Histograms of bug / version corr", fontsize=16, y=0.06)

num_plot = 1
for bug_type, bug_type_corrs in counts_corrs.iteritems():
    cc_arr = np.array(bug_type_corrs)
    plt.subplot(num_rows, num_cols, num_plot)
    plt.hist(cc_arr, 30)
    plt.title(bug_type)
    num_plot += 1

plt.tight_layout()    
plt.show()
