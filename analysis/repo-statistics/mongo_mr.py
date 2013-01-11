import mongo_helper

from bson.code import Code


def main():
    mapper = Code("""
                  function() {
                    emit(this.JarMetadata.group_id + "||" + this.JarMetadata.artifact_id, 1);
                  }""")

    reducer = Code("""
                   function(key, values) {
                     var total = 0;

                     for (var i = 0; i < values.length; i++) {
                        total += values[i];
                     }

                     return total;
                   }
                   """)

    print "Connecting ... to %s" % (mongo_helper.MONGO_DB,)
    db = mongo_helper.get_mongo_db()
    result = db[mongo_helper.MONGO_COL].map_reduce(mapper, reducer, "myresults")
    print result


if __name__ == "__main__":
    main()
