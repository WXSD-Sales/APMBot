import copy
import ssl
import traceback

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError

from datetime import datetime, timedelta

try:
    from lib.settings import Settings
except Exception as e:
    from settings import Settings


class MongoController(object):
    def __init__(self):
        self.client = MongoClient(Settings.mongo_db)
        self.db = self.client[Settings.db_name]
        self.issues = self.db["issues"]
        self.comments = self.db["comments"]

    def sanitize(self, mystr):
        return mystr.replace("~", "~e").replace(".", "~p").replace("$", "~d")

    def desanitize(self, mystr):
        return mystr.replace("~d", "$").replace("~p", ".").replace("~e", "~")

    def insert(self, id, server_status=None, comment={}):
        now = datetime.utcnow()
        result = None
        try:
            document = {
                        "id":id,
                        "timestamp" : now,
            }
            if server_status is not None:
                document.update({ "server_status" : server_status })
            update = { "$set" : document }
            inserted = self.issues.update_one({"id":id}, update, upsert=True)
            if inserted.acknowledged:
                print('update ack, issue: {0}'.format(id))
            comment["author"] += " @ {0}".format(now.strftime("%H:%M:%S"))
            document.update({ "timestamp_float": now.timestamp(), "comment": comment })
            inserted = self.comments.insert_one(document)
            if inserted.acknowledged:
                print('insert ack, comment:{0}'.format(comment))
                result = document
        except Exception as e:
            traceback.print_exc()
        return result

    def get_comments(self, id, timestamp_float=None):
        projection = {"_id":0, "comment":1, "timestamp_float":1}
        if timestamp_float == None:
            app = self.issues.find_one({"id":id})
            if app != None:
                app.pop("_id")
                app.pop("timestamp")
            else:
                app = {}
            comments = list(self.comments.find({"id":id}, projection))
            app.update({"comments":comments})
            return app
        else:
            comments = list(self.comments.find({"id":id, "timestamp_float" : {"$gt":timestamp_float} }, projection))
            return comments


if __name__ == "__main__":
    db = MongoController()
    #db.issues.create_index([("timestamp", 1)], expireAfterSeconds=90)
    #db.insert("1234", True, {"author":"Taylor", "message":"hey"})
    #db.insert("1234", False, {"author":"Taylor", "message":"bye"})
    """
    x = db.issues.aggregate([
      { "$match": {"id": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9lNjAwY2ZlYS01NTczLTQwMDYtOTk1MC0yM2YzODY2Mjc1OGU"} },
      { "$unwind": "$comments" },
      { "$match": { "comments.timestamp": { "$gt" : 1619739812 } } },
      { "$sort": { "comments.timestamp": 1 } }
    ])
    for i in x:
        print(i)
    x = db.issues.aggregate([
      { "$match": {"id": "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9lNjAwY2ZlYS01NTczLTQwMDYtOTk1MC0yM2YzODY2Mjc1OGU"} },
      { "$unwind": "$comments" },
      { "$match": { "comments.timestamp": { "$gt" : 1619739901.220879 } } },
      { "$sort": { "comments.timestamp": 1 } }
    ])
    print(x)
    for i in x:
        print(i)
    """
