import pymongo
import datetime
import time
import collections
import common
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
        # Init collection nametuple
        Answer = collections.namedtuple("Answer", ["grader_name", "ans", "ans_dist", "detail", "link"])
        Answer.grader_name, Answer.link = None, None

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
        ans_infos = self.db["answers"].find(db_filter)
        return ans_infos

    def _find_ans_infos(self, project_id, text, tg, print_allowed=True):
        db_filter = {
            "project": project_id,
            "text": text
        }
        query = self.db["querys"].find_one(db_filter)
        if (query):
            query_id = query["_id"]
        else:
            common.print_at("No such query.", tg, not tg and print_allowed)
            return None
        ans_infos = self._find_all_ans_by_query_id(query_id)
        return ans_infos
    
    def find_one_ans(self, project_id, text, tg=None, print_allowed=True):
        # Init collection nametuple
        Answer = collections.namedtuple("Answer", ["grader_name", "ans", "ans_dist", "detail", "link"])
        Answer.grader_name = "Unknown"

        # Find ans_infos that store all the query related to that project id and text
        ans_infos = self._find_ans_infos(project_id=project_id, text=text, tg=tg, print_allowed=print_allowed)
        if not ans_infos:
            common.print_at("Have query but not have answer yet. ", print_allowed)
            return None
        try:
            ans_info = self._find_most_reliable(ans_infos)
            Answer.ans = ans_info["grader_answer"]
        except (KeyError, TypeError):
            common.print_at("Have answer query but have no grader answer yet.", tg, print_allowed)
            return None
        grader_id = ans_info["grader"]
        grader = self.db["graders"].find_one({"_id": grader_id})
        if (grader):
            Answer.grader_name = grader["name"]
        return Answer

    def find_most_popular(self, project_id, text, tg=None, print_allowed=True):
        # Find ans_infos that store all the query related to that project id and text
        ans_infos = self._find_ans_infos(project_id=project_id, text=text, tg=tg, print_allowed=print_allowed)
        if not ans_infos:
            return None
        grader_by_id = self.create_grader_table_by_id()
        Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
        return Answer

    def find_conflict(self, project_id, usr_id, tg, print_allowed=True):
        conflict = collections.namedtuple("conflict", ['total', 'texts', 'anss', 'usr_anss', 'details', 'ans_dists', 'links'])
        conflict.total, conflict.texts, conflict.anss, conflict.usr_anss, conflict.details, conflict.ans_dists, conflict.links = 0,[], [],[],[],[],[]

        query_filter = {"project": project_id}
        query_datas = self.db["querys"].find(query_filter)
        grader_by_id = self.create_grader_table_by_id()
        if query_datas.count() == 0:
            common.print_at("No Such project", tg, print_allowed)
            return None
        else:
            for query_data in query_datas:
                text = query_data["text"]
                ans_infos = self._find_all_ans_by_query_id(query_data['_id'])
                Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
                grader_name = self.db["graders"].find_one({"_id": usr_id})["name"]
                grader_ans = Answer.detail[grader_name]['ans']
                if grader_ans != Answer.ans:
                    conflict.texts.append(text)
                    conflict.anss.append(Answer.ans)
                    conflict.usr_anss.append(grader_ans)
                    conflict.details.append(Answer.detail)
                    conflict.ans_dists.append(Answer.ans_dist)
                    conflict.links.append(Answer.link)
                    conflict.total += 1
            if conflict.total == 0:
                common.print_at("No Conflict Detected", tg, print_allowed)
                return None
            return conflict

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