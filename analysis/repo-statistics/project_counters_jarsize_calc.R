library(lattice)
jarsize.counts <- read.csv('data/project_counters_jarsize.csv')

forplot <- make.groups(
             security.high = data.frame(value = jarsize.counts$SECURITY_HIGH,
               jarsize = jarsize.counts$jarsize),
             security.low = data.frame(value = jarsize.counts$SECURITY_LOW,
               jarsize = jarsize.counts$jarsize),
             style =  data.frame(value = jarsize.counts$STYLE,
               jarsize = jarsize.counts$jarsize), 
             malicious.code = data.frame(value = jarsize.counts$MALICIOUS_CODE,
               jarsize = jarsize.counts$jarsize), 
             correctness = data.frame(value = jarsize.counts$CORRECTNESS,
               jarsize = jarsize.counts$jarsize), 
             bad.practice = data.frame(value = jarsize.counts$BAD_PRACTICE,
               jarsize = jarsize.counts$jarsize), 
             mt.correctness = data.frame(value = jarsize.counts$MT_CORRECTNESS,
               jarsize = jarsize.counts$jarsize), 
             i18n = data.frame(value = jarsize.counts$I18N,
               jarsize = jarsize.counts$jarsize), 
             performance = data.frame(value = jarsize.counts$PERFORMANCE,
               jarsize = jarsize.counts$jarsize), 
             experimental = data.frame(value = jarsize.counts$EXPERIMENTAL,
               jarsize = jarsize.counts$jarsize))

for (i in names(jarsize.counts)[4:length(colnames(jarsize.counts))]) {
  cor.result = cor.test(jarsize.counts$jarsize, jarsize.counts[[i]])
  cor.result$data.name = paste("jarsize", "and", i)
  print(cor.result)
}

dev.new()
pdf(file='data/project_counters_jarsize.pdf', width=7, height=7)
print(xyplot(jarsize~value|which, data=forplot,
             type = c("p", "r"),
             scales = list(relation="free"),
             pch=19,
             cex=.2,
             strip = strip.custom(strip.levels=TRUE,
               horizontal=TRUE,
               par.strip.text=list(cex=.8))))
dev.off()
