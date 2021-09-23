import pymongo
import config

db_name = "cmk_testing"

class Database:
    def __init__(self):
        self.URI = None
        self.login = None
        self.pw = None
        self.update_db_config()

    def update_db_config(self, login="common_user", pw="!23456Qwerty"):
        self.login = login
        self.pw = pw
        self.URI = "mongodb+srv://%s:%s@aiditesting.3bzv1.mongodb.net/%s?retryWrites=true&w=majority" % (
        self.login, self.pw, db_name)
        self.client = pymongo.MongoClient(self.URI)
        self.db = self.client[db_name]

    def get_project_status(self, project_id, locale):
        filter = {
            "project_id": project_id,
            "locale": locale
        }
        if not self.db["project_status"].count_documents(filter):
            return False
        return self.db["project_status"].find_one(filter)['status']

    def project_info_update(self, info):
        self.db["projects"].drop()
        self.db["projects"].insert_many(info)
        print("\u001b[32;1mRenew projects info done.\u001b[0m")

    def get_most_updated_version(self):
        return self.db["versions_control"].find_one()['checker']

    def update_local_config_from_db(self):
        # clean the data
        config.graders_info = []
        config.projects_info = []

        # get from database both graders and projects
        for grader in self.db["graders"].find({}):
            config.graders_info.append(grader)

        for project in self.db["projects"].find({}):
            config.projects_info.append(project)