package gr.aueb

import com.mongodb.casbah._
import com.mongodb.casbah.Implicits._
import com.mongodb.casbah.commons.MongoDBObject
import com.mongodb.casbah.commons.MongoDBList
import com.mongodb.DBObject
import com.mongodb.BasicDBObject
import com.mongodb.BasicDBList

object Mavenrepograph extends App {

  val coll = MongoConnection("83.212.106.194")("findbugs")("findbugs")

  println("Building adjacency matrix....")

  coll.find(MongoDBObject.empty, MongoDBObject("JarMetadata" -> 1)).limit(500).foldLeft(List[(String, String)]()) {
    (acc, x) =>
      val group_id = x.expand[String]("JarMetadata.group_id").get
      val artifact_id = x.expand[String]("JarMetadata.artifact_id").get
      val version = x.expand[String]("JarMetadata.version").get
      
      val name = new StringBuilder(group_id).append(".").append(artifact_id).append("-").append(version)
      
      val b = x.get("JarMetadata").asInstanceOf[DBObject].get("dependencies")
      val dependencies = x.get("JarMetadata").asInstanceOf[DBObject].get("dependencies") match {
        case l : BasicDBObject => List(l)
        case l : BasicDBList => l.toList.asInstanceOf[List[BasicDBObject]]
      }
      dependencies.filter(a => a.expand[String]("scope") != "test").foldLeft(List[(String, String)]()){
        (acc1, y) =>
          
      }

      acc ::: List()
  }

}
