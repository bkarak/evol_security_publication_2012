# initial script to test findbugs time.
# change the path of the repository accordingly.

# configuration variables
MAVEN_REPOSITORY=/Users/dimitro/Software/uk.maven.org/maven2
MAVEN_FULL_JARS=maven-full-jars.text
MAVEN_BINARIES=maven-binaries-jars.text

WORK_DIR=Software

# main script

find $MAVEN_REPOSITORY -type f -name *.jar > $MAVEN_FULL_JARS
cat $MAVEN_FULL_JARS | grep -v sources | grep -v javadoc > $MAVEN_BINARIES

for jfile in `cat $MAVEN_BINARIES`
do
	cd $WORK_DIR
	echo 'Extracting '.$jfile
	jar xvf $jfile	
	cd ..
	echo 'Calculating FindBugs'
	/Users/dimitro/Software/FindBugs/trunk/findbugs/bin/findbugs -textui -xml -output /Users/dimitro/Software/results/`basename $jfile`-findbugs.xml -include /Users/dimitro/Software/security_only_search.xml $jfile
	rm -rf work/*
done
