import pymongo
from datetime import datetime
import pytz
import time
import collections
from views.prints import *
from models import dbModel
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
        self.URI = "mongodb+srv://%s:%s@aiditesting.3bzv1.mongodb.net/%s?retryWrites=true&w=majority" % (
        self.login, self.pw, db_name)
        self.client = pymongo.MongoClient(self.URI)
        self.db = self.client[db_name]

    def grader_id_to_login_info(self, grader_id):
        db_filter = {
            "_id": grader_id
        }
        return self.db["graders"].find_one(db_filter)["login"], self.db["graders"].find_one(db_filter)["pw"]

    def query_insert(self, project_type, project_id, project_locale, text, web_controller):

        # try get the results links
        try:
            result_links = web_controller.get_result_links(project_type)
        except:
            result_links = []

        # insert query and answer
        db_filter = {
            "project": project_id,
            "locale": project_locale,
            "type": project_type,
            "text": text
        }
        count = self.db["querys"].count_documents(db_filter)
        # insert one query
        if count is 0:  # meaning no query duplicated
            my_dict = {
                "project": project_id,
                "locale": project_locale,
                "type": project_type,
                "text": text,
                "results": result_links
            }
            query_id = self.db["querys"].insert_one(my_dict).inserted_id
            return query_id
        elif count > 0:
            query_id = self.db["querys"].find_one(db_filter)["_id"]
            return query_id

    def answer_insert(self, answer, grader_id, query_id, query_link):

        # find the answer if it is exist
        db_filter = {
            "grader": grader_id,
            "query_id": query_id
        }
        count = self.db["answers"].count_documents(db_filter)
        if count is 0:
            my_dict = {
                # "_id": ans_id,
                "grader": grader_id,
                "query_id": query_id,
                "query_link": query_link,
                "grader_answer": answer,
                "time": datetime.fromtimestamp(time.time())
            }
            answer_id = self.db["answers"].insert_one(my_dict).inserted_id
            return answer_id
        elif count > 0:
            answer_id = self.db["answers"].find_one(db_filter)["_id"]
            self.grader_answer_update(answer_id, answer)
            return answer_id

    def grader_answer_update(self, answer_id, answer):
        target = {
            "_id": answer_id
        }
        new_dict = {"$set": {
            "grader_answer": answer,
            "time": datetime.fromtimestamp(time.time())
        }}
        self.db["answers"].update_one(target, new_dict)

    def project_finish_update(self, project_id, locale, grader_name):
        target_id = "{}({})".format(project_id, locale)
        target = {
            "_id": target_id
        }
        count = self.db["project_status"].count_documents(target)
        # if no such project_id, create new one
        if count is 0:
            my_dict = {
                '_id': target_id,
                'status': {
                    grader_name: datetime.utcnow().timestamp()
                }
            }
            self.db["project_status"].insert_one(my_dict)
        # if existed, update the timestamp
        elif count > 0:
            new_dict = {"$set": {
                'status.{}'.format(grader_name): datetime.utcnow().timestamp()
            }}
            self.db["project_status"].update_one(target, new_dict)

    def create_grader_table_by_id(self):
        grader_by_id = {}
        graders = self.db["graders"].find({})
        for grader in graders:
            grader_by_id[grader['_id']] = {}
            for key, value in grader.items():
                if key != '_id':
                    grader_by_id[grader['_id']][key] = value
        return grader_by_id

    def _find_most_reliable(self, ans_infos):
        reliability = 0
        required_ans = None
        for i, ans_info in enumerate(ans_infos):
            grader_number = ans_info['grader']
            for grader_info in config.graders_info:
                if grader_info["_id"] == grader_number:
                    if grader_info["reliability"] > reliability:
                        reliability = grader_info["reliability"]
                        required_ans = ans_info
        return required_ans

    def _ans_dist_update(self, ans_dict, ans):
        for i, a in enumerate(ans):
            i += 1
            if not ans_dict.get(i):
                ans_dict[i] = {}

            if ans_dict[i].get(a):
                ans_dict[i][a] += 1
            else:
                ans_dict[i][a] = 1
            # in reverse order
            ans_dict[i] = {k: v for k, v in sorted(ans_dict[i].items(), key=lambda item: item[1], reverse=True)}
        return ans_dict

    def _renew_grader_list(self, grader_by_id):
        grader_list = {}
        for target_grader_id in range(1, len(grader_by_id) + 1):
            grader_name = grader_by_id[target_grader_id]["name"]
            grader_list[grader_name] = {'ans': '', 'time': ''}
        return grader_list

    def _cat_most_popular_ans(self, ans_dist):
        required_ans = ''
        # loop for each result
        for number, value in ans_dist.items():
            top_ans_freq = 0
            top_ans = ''
            # loop for highest freq ans
            for ans, freq in value.items():
                if freq > top_ans_freq:
                    top_ans_freq = freq
                    top_ans = ans
            required_ans += top_ans
        return required_ans

    def _loop_for_most_popular_from_ans_infos(self, ans_infos, grader_by_id):
        """
        :param ans_infos: [(_id, grader, query_id, query_link, grader_answer, time), ... ]
        :param grader_by_id: {1 : {'name': 'Chris', 'login': 'chris', ... }}
        :return: Answer
        """
        Answer = dbModel.format_Answer()
        # loop for each graders and update the ans_dist
        Answer.detail = self._renew_grader_list(grader_by_id)
        Answer.ans_dist = {}
        for ans_info in ans_infos:
            grader_name = grader_by_id[ans_info['grader']]["name"]
            try:  # for have query but no answer
                ans, time = ans_info['grader_answer'], ans_info['time']
            except:
                ans, time = '', ''
            Answer.detail[grader_name]['ans'] = ans
            Answer.detail[grader_name]['time'] = time
            Answer.ans_dist = self._ans_dist_update(Answer.ans_dist, ans)
            if not Answer.link: Answer.link = ans_info["query_link"]

        # find the most popular ans from distribution
        Answer.ans = self._cat_most_popular_ans(Answer.ans_dist)
        return Answer

    def _find_all_ans_by_query_id(self, query_id):
        db_filter = {
            "query_id": query_id
        }
        # check if have answer for this query id
        if not self.db["answers"].count_documents(db_filter):
            return None
        ans_infos = self.db["answers"].find(db_filter)  # find all ans cursor
        return ans_infos

    def _find_ans_infos(self, project_id, project_locale, text, tg, print_allowed=True):
        db_filter = {
            "project": project_id,
            "locale": project_locale,
            "text": text
        }
        query = self.db["querys"].find_one(db_filter)
        if (query):
            query_id = query["_id"]
        else:
            print_at("No such query.", tg, print_allowed)
            return None
        ans_infos = self._find_all_ans_by_query_id(query_id)
        return ans_infos

    def find_one_ans(self, project_id, project_locale, text, tg=None, print_allowed=True):

        Answer = dbModel.format_Answer()
        # Find ans_infos that store all the query related to that project id and text
        ans_infos = self._find_ans_infos(project_id, project_locale, text, tg, print_allowed=print_allowed)
        if not ans_infos:
            return None
        try:
            ans_info = self._find_most_reliable(ans_infos)
            Answer.ans = ans_info["grader_answer"]
        except (KeyError, TypeError):
            print_at("Reliable Answer Error.", tg, print_allowed)
            return None
        grader_id = ans_info["grader"]
        grader = self.db["graders"].find_one({"_id": grader_id})
        if (grader):
            Answer.grader_name = grader["name"]
        return Answer

    def find_most_popular(self, project_id, project_locale, text, tg=None, print_allowed=True):
        # Find ans_infos that store all the query related to that project id and text
        ans_infos = self._find_ans_infos(project_id, project_locale, text, tg, print_allowed=print_allowed)
        if not ans_infos:
            return None
        grader_by_id = self.create_grader_table_by_id()
        Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
        return Answer

    def find_conflict(self, project_id, usr_id, tg, print_allowed=True):
        conflict = collections.namedtuple("conflict",
                                          ['total', 'texts', 'anss', 'usr_anss', 'details', 'ans_dists', 'links'])
        conflict.total, conflict.texts, conflict.anss, conflict.usr_anss, conflict.details, conflict.ans_dists, conflict.links = 0, [], [], [], [], [], []

        query_filter = {"project": project_id}
        query_datas = self.db["querys"].find(query_filter)
        grader_by_id = self.create_grader_table_by_id()
        if query_datas.count() == 0:
            print_at("No Such project", tg, print_allowed)
            return None
        else:
            for query_data in query_datas:
                text = query_data["text"]
                ans_infos = self._find_all_ans_by_query_id(query_data['_id'])
                Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
                grader_name = self.db["graders"].find_one({"_id": usr_id})["name"]
                grader_ans = Answer.detail[grader_name]['ans']
                if grader_ans != Answer.ans and grader_ans != '':
                    conflict.texts.append(text)
                    conflict.anss.append(Answer.ans)
                    conflict.usr_anss.append(grader_ans)
                    conflict.details.append(Answer.detail)
                    conflict.ans_dists.append(Answer.ans_dist)
                    conflict.links.append(Answer.link)
                    conflict.total += 1
            if conflict.total == 0:
                print_at("No Conflict Detected", tg, print_allowed)
                return None
            return conflict

    def get_expired_date(self, usr_name):
        db_filter = {
            "name": usr_name
        }
        return self.db["payment"].find_one(db_filter)["expired"]

    def get_most_updated_version(self):
        return self.db["versions_control"].find_one()['version']

    def update_local_config_from_db(self):
        # clean the data
        config.graders_info = []
        config.projects_info = []
        config.ghost_projects_info = []

        # get from database both graders and projects
        for grader in self.db["graders"].find({}):
            config.graders_info.append(grader)

        for project in self.db["projects"].find({}):
            config.projects_info.append(project)

        for project in self.db["ghost_projects"].find({}):
            config.ghost_projects_info.append(project)