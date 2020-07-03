import pymongo
import datetime
import time
from config import *
import re
import dns

name = "chris"
pw = "!23456Qwerty"
db_name = "cmk_testing"
URI = "mongodb+srv://%s:%s@aiditesting.3bzv1.mongodb.net/%s?retryWrites=true&w=majority" %(name, pw, db_name)

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(URI)
        self.db = self.client[db_name]
        self.project_type = None

    def filter_gen(self, project_id, text):
        filter = {
            "project": project_id,
            "text": text
        }
        return filter

    def query_insert(self, project_id, text, result_links=None):
        filter = self.filter_gen(project_id, text)
        if filter is None:
            print("project documents is not updated OR something wrong.")
            return None
        count = self.db["querys"].count_documents(filter)
        # insert one query
        if count is 0: # meaning no query duplicated
            my_dict = {
                "project": project_id,
                "text": text,
                "results": result_links
            }
            query_id = self.db["querys"].insert_one(my_dict).inserted_id
            return query_id
        elif count > 0:
            query_id = self.db["querys"].find_one(filter)["_id"]
            return query_id
        else:
            return None

    def grader_answer_insert(self, grader_id, query_id, query_link):

        # find the webpage page id
        regex = re.compile(r"/s/\S+/r/")
        matches = regex.finditer(query_link)
        ans_id = None
        for match in matches:
            ans_id = query_link[match.span()[0] + 3:match.span()[1] - 3]
        if ans_id is None:
            print("invalid query link / Cannot catch the webpage ID")

        # find the answer if it is exist
        filter = {
            "_id": ans_id
        }
        count = self.db["answers"].count_documents(filter)
        if count is 0:
            my_dict = {
                "_id": ans_id,
                "grader": grader_id,
                "query_id": query_id,
                "query_link": query_link
            }
            answer_id = self.db["answers"].insert_one(my_dict).inserted_id
            return answer_id
        elif count > 0:
            answer_id = self.db["answers"].find_one(filter)["_id"]
            return answer_id
        else:
            return None

    def grader_answer_update(self, answer_id, answer="na"):
        target = {
            "_id": answer_id
        }
        new_dict = {"$set": {
            "grader_answer": answer,
            "time": datetime.datetime.fromtimestamp(time.time())
        }}
        self.db["answers"].update_one(target, new_dict)

    def project_info_update(self):
        self.db["projects"].drop()
        self.db["projects"].insert_many(projects_info)
        print("Renew projects info done.")

    def graders_id_update(self):
        self.db["graders"].drop()
        self.db["graders"].insert_many(graders_id)
        print("Renew graders info done.")
