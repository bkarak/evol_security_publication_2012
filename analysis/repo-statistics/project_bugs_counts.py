import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import math

bugs_per_version = {
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
    for project, data in json_input.iteritems():
        if len(data['versions']) > 100:
            continue
        for version in data['versions']:
            version_order = version['JarMetadata']['version_order']
            if version_order == 0:
                continue
            counters = version['Counters']
            for counter in bugs_per_version.keys():
                value = counters.get(counter, 0)
                if value > 1000:
                    print project, version_order, counter, value
                bugs_per_version[counter].append((version_order, value))


for counter, counter_list in bugs_per_version.iteritems():
    bugs_per_version_arr = np.array(counter_list).transpose()            
    (rho, p_value) = st.spearmanr(bugs_per_version_arr[0],
                                  bugs_per_version_arr[1])
    print counter, rho, p_value

plt.figure(1, figsize=(16, 10))
num_plots = len(bugs_per_version.keys())
num_cols = 4
num_rows = num_plots / num_cols
if num_rows % num_cols != 0:
    num_rows += 1
num_plot = 1
for counter, counter_list in bugs_per_version.iteritems():
    bugs_per_version_arr = np.array(counter_list).transpose()
    plt.subplot(num_rows, num_cols, num_plot)
    plt.xlim((0, 100))
    ymax = math.ceil(1.1 * bugs_per_version_arr[1].max())
    plt.ylim((0, ymax))
    plt.scatter(bugs_per_version_arr[0], bugs_per_version_arr[1])
    plt.title(counter)
    num_plot += 1

plt.show()

    
