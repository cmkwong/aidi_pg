import requests
import collections
from views.prints import *
from models import dbModel, authModel
import config

def print_S(string, allowed=True):
    if allowed:
        print(string)

class Database:
    def __init__(self):
        self.db_name = "cmk_testing"
        # self.update_db_config()
        self.mainUrl = "https://aidi-work-helper.herokuapp.com/"
        self.api_urls()

    # def update_db_config(self, login="reader", pw="s23456s"):
    #     URI = "mongodb+srv://%s:%s@aiditesting.3bzv1.mongodb.net/%s?retryWrites=true&w=majority" % (login, pw, self.db_name)
    #     self.client = pymongo.MongoClient(URI)
    #     self.db = self.client[self.db_name]

    def api_urls(self):
        self.prj_finish_url = self.mainUrl + "api/v1/project/status"
        self.find_many_ans_url = self.mainUrl + "api/v1/query/manyAnswer?project_id={}&locale={}&query_code={}"
        self.find_many_queries_from_project_id_url = self.mainUrl + "api/v1/query?project_id={}&max={}"
        self.find_many_ans_from_many_queryId_url = self.mainUrl + "api/v1/query/manyAnswerManyQueryId"
        self.get_graders_info_url = self.mainUrl + "api/v1/user?locale=hk"
        self.get_project_list_url = self.mainUrl + "api/v1/project/list"
        self.get_ghost_project_list_url = self.mainUrl + "api/v1/project/ghostList"
        self.get_version_url = self.mainUrl + "api/v1/system/version"
        self.get_expired_date_url = self.mainUrl + "api/v1/user/expired?grader={}"
        self.check_health_url = self.mainUrl + "api/v1/system/clientsHealthStatus"
        self.update_query_answer_url = self.mainUrl + "api/v1/query?insertAns=true"

    # def grader_id_to_login_info(self, grader_id):
    #     role_filter = {
    #         "_id": grader_id
    #     }
    #     login_filter = {
    #         "role": self.db["graders"].find_one(role_filter)["role"]
    #     }
    #     return self.db["db_login"].find_one(login_filter)["login"], self.db["db_login"].find_one(login_filter)["pw"]

    # def query_insert(self, project_type, project_id, project_locale, text, web_controller):
    #
    #     # try get the results links
    #     try:
    #         result_links = web_controller.get_result_links(project_type)
    #     except:
    #         result_links = []
    #
    #     # insert query and answer
    #     db_filter = {
    #         "project": project_id,
    #         "locale": project_locale,
    #         "type": project_type,
    #         "text": text
    #     }
    #     count = self.db["querys"].count_documents(db_filter)
    #     # insert one query
    #     if count is 0:  # meaning no query duplicated
    #         my_dict = {
    #             "project": project_id,
    #             "locale": project_locale,
    #             "type": project_type,
    #             "text": text,
    #             "results": result_links
    #         }
    #         query_id = self.db["querys"].insert_one(my_dict).inserted_id
    #         return query_id
    #     elif count > 0:
    #         query_id = self.db["querys"].find_one(db_filter)["_id"]
    #         return query_id

    # def answer_insert(self, answer, grader_id, query_id, query_link):
    #
    #     # find the answer if it is exist
    #     db_filter = {
    #         "grader": grader_id,
    #         "query_id": query_id
    #     }
    #     count = self.db["answers"].count_documents(db_filter)
    #     if count is 0:
    #         my_dict = {
    #             # "_id": ans_id,
    #             "grader": grader_id,
    #             "query_id": query_id,
    #             "query_link": query_link,
    #             "grader_answer": answer,
    #             "time": datetime.fromtimestamp(time.time())
    #         }
    #         answer_id = self.db["answers"].insert_one(my_dict).inserted_id
    #         return answer_id
    #     elif count > 0:
    #         answer_id = self.db["answers"].find_one(db_filter)["_id"]
    #         self.grader_answer_update(answer_id, answer)
    #         return answer_id

    # def grader_answer_update(self, answer_id, answer):
    #     target = {
    #         "_id": answer_id
    #     }
    #     new_dict = {"$set": {
    #         "grader_answer": answer,
    #         "time": datetime.fromtimestamp(time.time())
    #     }}
    #     self.db["answers"].update_one(target, new_dict)

    def project_finish_update(self, project_id, locale, grader_name, tg):
        data = {
            "project_id": project_id,
            "locale": locale,
            "grader": grader_name,
        }
        res = requests.post(self.prj_finish_url, data)
        if res.status_code == 200:
            print_at(config.MESSAGE_ERROR_PAGE_SENT.format(project_id, locale), tg)
        else:
            print_at(config.MESSAGE_NO_FINISHED_POP, tg)

    def create_grader_table_by_id(self):
        grader_by_id = {}
        for dic in config.graders_info:
            # defined the sub-dictionary first with _id
            grader_id = dic['grader_id']
            grader_by_id[grader_id] = {}
            # then assign the key and value into sub-dictionary
            for key, value in dic.items():
                if key != 'grader_id':
                    grader_by_id[grader_id][key] = value
        return grader_by_id

    def _find_most_reliable(self, ans_infos):
        reliability = 0
        required_ans_info = None
        for i, ans_info in enumerate(ans_infos):
            grader_name = ans_info['grader']
            for grader_info in config.graders_info:
                if grader_info["name"] == grader_name:
                    if grader_info["reliability"] > reliability:
                        reliability = grader_info["reliability"]
                        required_ans_info = ans_info
        return required_ans_info

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
            grader_name = ans_info['grader'] # get the grader name
            try:  # for have query but no answer
                ans, time = ans_info['grader_ans'], ans_info['time']
            except:
                ans, time = '', ''
            Answer.detail[grader_name]['ans'] = ans
            Answer.detail[grader_name]['time'] = time
            Answer.ans_dist = self._ans_dist_update(Answer.ans_dist, ans)

        # find the most popular ans from distribution
        Answer.ans = self._cat_most_popular_ans(Answer.ans_dist)
        return Answer

    # def _find_all_ans_by_query_id(self, query_id):
    #     db_filter = {
    #         "query_id": query_id
    #     }
    #     # check if have answer for this query id
    #     if not self.db["answers"].count_documents(db_filter):
    #         return None
    #     ans_infos = self.db["answers"].find(db_filter)  # find all ans cursor
    #     return ans_infos

    # def _find_ans_infos(self, project_id, project_locale, text, tg, print_allowed=True):
    #     db_filter = {
    #         "project": project_id,
    #         "locale": project_locale,
    #         "text": text
    #     }
    #     query = self.db["querys"].find_one(db_filter)
    #     if (query):
    #         query_id = query["_id"]
    #     else:
    #         print_at("No such query.", tg, print_allowed)
    #         return None
    #     ans_infos = self._find_all_ans_by_query_id(query_id)
    #     return ans_infos

    def find_one_ans(self, project_id, project_locale, query_code):
        Answer = dbModel.format_Answer()
        # Find ans_infos that store all the query related to that project id and text
        res = requests.get(self.find_many_ans_url.format(project_id, project_locale, query_code))
        if res.status_code != 200:
            return None
        try:
            ans_infos = res.json()['data']
            ans_info = self._find_most_reliable(ans_infos)
            Answer.ans = ans_info["grader_ans"]
        except (KeyError, TypeError):
            return None
        Answer.grader_name = ans_info["grader"]
        return Answer

    # def find_one_ans_discard(self, project_id, project_locale, text, tg=None, print_allowed=True):
    #
    #     Answer = dbModel.format_Answer()
    #     # Find ans_infos that store all the query related to that project id and text
    #     ans_infos = self._find_ans_infos(project_id, project_locale, text, tg, print_allowed=print_allowed)
    #     if not ans_infos:
    #         return None
    #     try:
    #         ans_info = self._find_most_reliable(ans_infos)
    #         Answer.ans = ans_info["grader_answer"]
    #     except (KeyError, TypeError):
    #         print_at("Reliable Answer Error.", tg, print_allowed)
    #         return None
    #     grader_id = ans_info["grader"]
    #     grader = self.db["graders"].find_one({"_id": grader_id})
    #     if (grader):
    #         Answer.grader_name = grader["name"]
    #     return Answer

    def find_most_popular(self, project_id, project_locale, query_code):
        # Find ans_infos that store all the query related to that project id and text
        res = requests.get(self.find_many_ans_url.format(project_id, project_locale, query_code))
        if res.status_code != 200:
            return None
        ans_infos = res.json()['data']
        grader_by_id = self.create_grader_table_by_id()
        Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
        return Answer

    # def find_most_popular_discard(self, project_id, project_locale, text, tg=None, print_allowed=True):
    #     # Find ans_infos that store all the query related to that project id and text
    #     ans_infos = self._find_ans_infos(project_id, project_locale, text, tg, print_allowed=print_allowed)
    #     if not ans_infos:
    #         return None
    #     grader_by_id = self.create_grader_table_by_id()
    #     Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
    #     return Answer

    def _get_ans_infos_by_queryId(self, raw_ans_infos, query_ids):
        """
        :param raw_ans_infos: [answer documents]
        :param query_ids: [id]
        :return: {query_id: ans_infos}
        """
        ans_infos_by_queryId = {}
        for query_id in query_ids:
            ans_infos_by_queryId[query_id] = []
            for ans_info in raw_ans_infos:
                if ans_info["query_id"] == query_id:
                    ans_infos_by_queryId[query_id].append(ans_info)
        return ans_infos_by_queryId

    def _get_query_ids_from_query_datas(self, query_datas):
        """
        :param query_datas: [query_datas]
        :return: [query_id]
        """
        query_ids = []
        for query_data in query_datas:
            query_ids.append(query_data['_id'])
        return query_ids

    def find_conflict(self, project_id, grader_name, tg, max_queries=50, print_allowed=True):
        conflict = collections.namedtuple("conflict",
                                          ['total', 'texts', 'anss', 'usr_anss', 'details', 'ans_dists', 'links'])
        conflict.total, conflict.texts, conflict.anss, conflict.usr_anss, conflict.details, conflict.ans_dists, conflict.links = 0, [], [], [], [], [], []

        # find the query_datas
        res = requests.get(self.find_many_queries_from_project_id_url.format(project_id, max_queries))
        if res.status_code != 200:
            print_at(config.MESSAGE_NOT_FOUND, tg, print_allowed)
            return None
        query_datas = res.json()['data']
        query_ids = self._get_query_ids_from_query_datas(query_datas)

        # get many answer from many query ids (raw ans infos)
        raw_ans_infos = requests.post(url=self.find_many_ans_from_many_queryId_url, data={"query_ids": query_ids}).json()['data']
        ans_infos_by_queryId = self._get_ans_infos_by_queryId(raw_ans_infos, query_ids) # reformat the (query_id: ans_info)

        grader_by_id = self.create_grader_table_by_id()
        for query_data in query_datas:
            text = query_data["query_text"]
            ans_infos = ans_infos_by_queryId[query_data['_id']]
            Answer = self._loop_for_most_popular_from_ans_infos(ans_infos, grader_by_id)
            grader_ans = Answer.detail[grader_name]['ans']
            if grader_ans != Answer.ans and grader_ans != '':
                conflict.texts.append(text)
                conflict.anss.append(Answer.ans)
                conflict.usr_anss.append(grader_ans)
                conflict.details.append(Answer.detail)
                conflict.ans_dists.append(Answer.ans_dist)
                conflict.links.append(query_data["query_link"])
                conflict.total += 1
        if conflict.total == 0:
            print_at(config.MESSAGE_NO_CONFLICT, tg, print_allowed)
            return None
        return conflict

    def send_query_answer(self, data):
        requests.post(self.update_query_answer_url, data)

    def check_health_status(self, version, grader_id):
        usr_name = authModel.get_usrName_from_graderId(grader_id)
        data = {
            "user_version": version,
            "grader": usr_name
        }
        res = requests.post(self.check_health_url, data)
        if res.status_code == 409:
            raise Exception("Outdated Version, re-open program.")
        hr_left = res.json()['data']
        return hr_left

    def get_expired_date(self, usr_name):
        expired_date = requests.get(self.get_expired_date_url.format(usr_name)).json()['data']
        return expired_date

    def get_most_updated_version(self):
        version = requests.get(self.get_version_url).json()['data']['clients']
        return version

    def get_graders_info(self):
        graders_info = requests.get(self.get_graders_info_url).json()['data']
        config.graders_info = graders_info

    def get_project_list(self):
        projects_info = requests.get(self.get_project_list_url).json()['data']
        config.projects_info = projects_info

    def get_ghost_project_list(self):
        ghost_projects_info = requests.get(self.get_ghost_project_list_url).json()['data']
        config.ghost_projects_info = ghost_projects_info

    def update_local_config_from_db(self):
        # clean the data
        config.graders_info = []
        config.projects_info = []
        config.ghost_projects_info = []

        # get graders (from hk)
        self.get_graders_info()
        # get project list
        self.get_project_list()
        # get ghost project list
        self.get_ghost_project_list()