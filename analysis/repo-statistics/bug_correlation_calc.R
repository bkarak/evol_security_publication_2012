# Calculates pairwise correlations from the data in
# data/bug_correlation_counters.csv, which is produced
# by bug_correlation_tab.py

bug.counts <- read.csv("data/bug_correlation_counters.csv")

for (i in (2:(ncol(bug.counts) - 1))) {
  for (j in ((i + 1):(ncol(bug.counts) - 1))) {
    print(paste(colnames(bug.counts)[i], ":", colnames(bug.counts[j])))
    print(cor.test(bug.counts[, i], bug.counts[, j]))
  }
}
