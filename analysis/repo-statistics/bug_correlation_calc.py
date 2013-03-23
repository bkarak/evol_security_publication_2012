# Calculates pairwise correlations from the data in
# data/bug_correlation_counters.json

import json
import pandas as pd
import numpy as np
import scipy.stats as st
from itertools import izip
import sys
import itertools
from corrplot import corrplot

bug_types = [
    'SECURITY_HIGH',
    'SECURITY_LOW',
    'STYLE',
    'BAD_PRACTICE',
    'CORRECTNESS',
    'MT_CORRECTNESS',
    'PERFORMANCE',
    'I18N',
    'EXPERIMENTAL'
    ]
    
with open("data/bug_correlation_counters.json") as infile:
    json_input = json.load(infile)

data = pd.DataFrame(json_input).T
data['SECURITY_HIGH'] = data['SECURITY_HIGH'] + data['MALICIOUS_CODE']
data['TOTAL_SECURITY_HIGH'] = (data['TOTAL_SECURITY_HIGH']
                               + data['TOTAL_MALICIOUS_CODE'])
data = data.drop(['MALICIOUS_CODE', 'TOTAL_MALICIOUS_CODE'], axis=1)

num_bug_types = len(bug_types)
corrmatrix = np.identity(num_bug_types)
pvalues = np.zeros([num_bug_types, num_bug_types])

for i in xrange(num_bug_types):
    for j in xrange(i + 1, num_bug_types):
        icolumn = bug_types[i]
        jcolumn = bug_types[j]
        data_pair = data[[icolumn, jcolumn]].dropna()
        (corr, pvalue) = st.pearsonr(data_pair[icolumn], data_pair[jcolumn])
        print icolumn, jcolumn, corr, pvalue        
        corrmatrix[i, j] = corrmatrix[j, i] = corr
        pvalues[i, j] = pvalues[j, i] = pvalue


print r"""
\begin{tabular}{ccccccccc}
\hline \\
"""

for row in corrmatrix:
    print ' & '.join(map('{:.2f}'.format, row)), r'\\'

print r"""
\hline \\
\end{tabular}
"""
plot = corrplot(corrmatrix, pvalues, bug_types)

plot.tight_layout()
plot.savefig('corrplot.pdf', format='pdf')
plot.show()
