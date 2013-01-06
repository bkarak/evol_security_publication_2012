name := "Maven Dependency graphs"

version := "0.1.0-SNAPSHOT"

scalaVersion := "2.9.2"

scalacOptions ++= Seq(
  "-deprecation",
   "-unchecked"
)

libraryDependencies ++= Seq(
  "org.mongodb" %% "casbah" % "2.4.1"
)

mainClass := Some("gr.aueb.MavenDependencyGraphs")

javaOptions ++=Seq(
"-XX:+UseParallelGC",
"-Xms2048m",
"-Xmx4096m"
)

resolvers += "typesafe" at "http://repo.typesafe.com/typesafe/releases/"

