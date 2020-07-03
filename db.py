import pymongo
import dns

name = "chris"
pw = "!23456Qwerty"
db_name = "cmk_testing"
URI = "mongodb+srv://%s:%s@aiditesting.3bzv1.mongodb.net/%s?retryWrites=true&w=majority" %(name, pw, db_name)

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(URI)
        self.db = self.client[db_name]
        self.querys_collection = self.db["querys"]
        self.answers_collection = self.db["answers"]
        self.projects_cursor = self.db["projects"].find({})

    def filter_gen(self, project_id, text):
        for x in self.projects_cursor:
            if (x["project_type"] == "spot12" or x["project_type"] == "saf"):
                filter = {
                    "project": project_id,
                    "text": text
                }
                return filter

    def query_insert(self, project_id, text, result_links=None):
        query_id = None
        filter = self.filter_gen(project_id, text)
        count = self.querys_collection.count_documents(filter)
        # insert one query
        if count is 0:
            my_dict = {
                "project": project_id,
                "text": text,
                "results": result_links
            }
            query_id = self.querys_collection.insert_one(my_dict).inserted_id
            return query_id
        else:
            return query_id

    def grader_answer_insert(self, grader_id, query_id, query_link):
        my_dict = {
            "grader": grader_id,
            "query_id": query_id,
            "query_link": query_link
        }
        answer_id = self.answers_collection.insert_one(my_dict).inserted_id
        return answer_id

    def grader_answer_update(self, answer_id, answer="na"):
        target = {
            "_id": answer_id
        }
        new_dict = {"$set": {
            "grader_answer": answer,

        }}
        self.answers_collection.update_one(target, new_dict)