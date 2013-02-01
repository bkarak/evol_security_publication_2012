# Calculates pairwise correlations from the data in
# data/bug_correlation_counters.json


import json
import pandas as pd
import numpy as np
import scipy.stats as st
from itertools import izip
import sys

with open("data/bug_correlation_counters.json") as infile:
    json_input = json.load(infile)

data = pd.DataFrame(json_input).T

for i in xrange(len(data.columns) - 1):
    for j in xrange(i + 1, (len(data.columns) - 1)):
        frm = data.ix[:, [i, j]].dropna()
        (corr, pvalue) = st.pearsonr(frm.ix[:, 0], frm.ix[:, 1])
        print data.columns[i], data.columns[j], corr, pvalue

