import pymongo
import datetime
import time
from config import *
import re
import dns
import config

db_name = "cmk_testing"

def print_S(string, allowed=True):
    if allowed:
        print(string)


class Database:
    def __init__(self):
        self.URI = None
        self.login = None
        self.pw = None
        self.update_db_config()

    def update_db_config(self, login="common_user", pw="!23456Qwerty"):
        self.login = login
        self.pw = pw
        self.URI = "mongodb+srv://%s:%s@aiditesting.3bzv1.mongodb.net/%s?retryWrites=true&w=majority" % (self.login, self.pw, db_name)
        self.client = pymongo.MongoClient(self.URI)
        self.db = self.client[db_name]

    def grader_id_to_login_info(self, id):
        db_filter = {
            "_id": id
        }
        return self.db["graders"].find_one(db_filter)["login"], self.db["graders"].find_one(db_filter)["pw"]

    def filter_gen(self, project_id, text):
        db_filter = {
            "project": project_id,
            "text": text
        }
        return db_filter

    def query_insert(self, project_id, text, result_links=None):
        db_filter = self.filter_gen(project_id, text)
        if db_filter is None:
            print("project documents is not updated OR something wrong.")
            return None
        count = self.db["querys"].count_documents(db_filter)
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
            query_id = self.db["querys"].find_one(db_filter)["_id"]
            return query_id
        else:
            return None

    def grader_answer_insert(self, grader_id, query_id, query_link):

        # find the webpage page id
        # regex = re.compile(r"/s/\S+/r/")
        # matches = regex.finditer(query_link)
        # ans_id = None
        # for match in matches:
        #     ans_id = query_link[match.span()[0] + 3:match.span()[1] - 3]
        # if ans_id is None:
        #     print("invalid query link / Cannot catch the webpage ID")

        # find the answer if it is exist
        db_filter = {
            "grader": grader_id,
            "query_id": query_id
            #"_id": ans_id
        }
        count = self.db["answers"].count_documents(db_filter)
        if count is 0:
            my_dict = {
                #"_id": ans_id,
                "grader": grader_id,
                "query_id": query_id,
                "query_link": query_link
            }
            answer_id = self.db["answers"].insert_one(my_dict).inserted_id
            return answer_id
        elif count > 0:
            answer_id = self.db["answers"].find_one(db_filter)["_id"]
            return answer_id
        else:
            return None

    def grader_answer_update(self, grader_id, answer_id, answer="na"):
        target = {
            "_id": answer_id
        }
        new_dict = {"$set": {
            "grader": grader_id,
            "grader_answer": answer,
            "time": datetime.datetime.fromtimestamp(time.time())
        }}
        self.db["answers"].update_one(target, new_dict)

    def project_info_update(self):
        self.db["projects"].drop()
        self.db["projects"].insert_many(projects_info_admin)
        print("Renew projects info done.")

    def graders_id_update(self):
        self.db["graders"].drop()
        self.db["graders"].insert_many(graders_info_admin)
        print("Renew graders info done.")

    def find_one_ans(self, project_id, text, print_allowed=True):
        db_filter = {
            "project": project_id,
            "text": text
        }
        query = self.db["querys"].find_one(db_filter)
        if (query):
            query_id = query["_id"]
        else:
            print_S("No such query.", print_allowed)
            return None, None
        db_filter = {
            "query_id": query_id
        }
        ans_info = self.db["answers"].find_one(db_filter)
        if (ans_info):
            try:
                ans = ans_info["grader_answer"]
            except KeyError:
                print_S("Have answer query but have no grader answer yet.", print_allowed)
                return None, None
            grader_id = ans_info["grader"]
            grader = self.db["graders"].find_one({"_id": grader_id})
            if (grader):
                grader_name = grader["name"]
            else:
                grader_name = "Unknown"
            return ans, grader_name
        else:
            print_S("Have query but not have answer yet. ", print_allowed)
            return None, None

    def update_local_config_from_db(self):
        # clean the data
        config.graders_info = []
        config.projects_info = []

        # get from database both graders and projects
        for grader in self.db["graders"].find({}):
            config.graders_info.append(grader)

        for project in self.db["projects"].find({}):
            config.projects_info.append(project)