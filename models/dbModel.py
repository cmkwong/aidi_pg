import config
from views.prints import *
import collections

def update_grader_info(web_controller, db_controller):
    grader_id = web_controller.get_grader_id()
    # update the db login info
    login, pw = db_controller.grader_id_to_login_info(grader_id)
    db_controller.update_db_config(login=login, pw=pw)
    return grader_id

# def insert_db_query(web_controller, db_controller, project_id, query_text):
#
#     # insert query and answer
#     try:
#         result_links = web_controller.get_result_links()
#     except:
#         result_links = []
#
#     query_id = db_controller.query_insert(project_id, query_text, result_links)
#
#     return query_id

# def insert_db_ans(ans, db_controller, grader_id, query_id, query_link):
#     # insert upper part of answer
#     answer_id = db_controller.answer_insert(ans, grader_id, query_id, query_link)


def format_Answer():
    Answer = collections.namedtuple("Answer", ['find_ok', 'ans', 'find_time_used',
                                               'grader_name', 'ans_dist', 'detail', 'link'])
    Answer.find_ok, Answer.ans, Answer.find_time_used, \
    Answer.grader_name, Answer.ans_dist, Answer.detail, Answer.link \
        = False, None, 0, "Unknown", None, None, None
    return Answer