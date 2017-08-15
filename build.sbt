organization := "com.holdenkarau.kafka.python"

name := "cthulhu"

publishMavenStyle := true

version := "0.0.1-SNAPSHOT"

scalaVersion := "2.11.8"

coverageHighlighting := true

javacOptions ++= Seq("-source", "1.8", "-target", "1.8")

parallelExecution in Test := false
fork := true


coverageHighlighting := true
coverageEnabled := true


javaOptions ++= Seq("-Xms1G", "-Xmx3G", "-XX:MaxPermSize=2048M", "-XX:+CMSClassUnloadingEnabled")


libraryDependencies ++= Seq(
  "org.apache.arrow" % "arrow-vector" % "0.6.0",
  "org.apache.kafka" %% "kafka" % "0.11.0.0",
  "org.apache.kafka" % "kafka-streams" % "0.11.0.0",
  "org.apache.kafka" % "kafka-clients" % "0.11.0.0",
  "com.madewithtea" %% "mockedstreams" % "1.3.0" % "test",
  "org.scalatest" %% "scalatest" % "3.0.2" % "test",
  "org.scalatest" %% "scalatest" % "3.0.2" % "test")


scalacOptions ++= Seq("-deprecation", "-unchecked")

pomIncludeRepository := { x => false }

resolvers ++= Seq(
  "sonatype-releases" at "https://oss.sonatype.org/content/repositories/releases/",
  "Typesafe repository" at "http://repo.typesafe.com/typesafe/releases/",
  "Second Typesafe repo" at "http://repo.typesafe.com/typesafe/maven-releases/",
  "Mesosphere Public Repository" at "http://downloads.mesosphere.io/maven",
  Resolver.sonatypeRepo("public")
)

// publish settings
publishTo := {
  val nexus = "https://oss.sonatype.org/"
  if (isSnapshot.value)
    Some("snapshots" at nexus + "content/repositories/snapshots")
  else
    Some("releases"  at nexus + "service/local/staging/deploy/maven2")
}

licenses := Seq("Apache License 2.0" -> url("http://www.apache.org/licenses/LICENSE-2.0.html"))

homepage := Some(url("https://github.com/holdenkarau/kafka-streams-python-cthulhu"))

pomExtra := (
  <scm>
    <url>git@github.com:holdenkarau/kafka-streams-python-cthulhu.git</url>
    <connection>scm:git@github.com:holdenkarau/kafka-streams-python-cthulhu.git</connection>
  </scm>
  <developers>
    <developer>
      <id>holdenk</id>
      <name>Holden Karau</name>
      <url>http://www.holdenkarau.com</url>
      <email>holden@pigscanfly.ca</email>
    </developer>
  </developers>
)

credentials ++= Seq(Credentials(Path.userHome / ".ivy2" / ".sbtcredentials"), Credentials(Path.userHome / ".ivy2" / ".sparkcredentials"))

useGpg := true

testOptions += Tests.Argument(TestFrameworks.JUnit, "-v", "-a")
