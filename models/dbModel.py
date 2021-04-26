import config
from views.prints import *

def update_grader_info(web_controller, db_controller):
    grader_id = web_controller.get_grader_id()
    # update the project id
    project_link = web_controller.get_motherTag_url()
    project_id = web_controller.get_project_id_from_url(project_link)
    # update the db login info
    login, pw = db_controller.grader_id_to_login_info(grader_id)
    db_controller.update_db_config(login=login, pw=pw)
    return grader_id, project_id, project_link

def insert_db_query(project_type, web_controller, db_controller, tg, project_id, query_text, grader_id, current_url):
    answer_id = None

    if project_type in config.UPDATE_DB_PROJS:
        # insert query and answer
        try:
            result_links = web_controller.get_links()
        except:
            result_links = []

        query_id = db_controller.query_insert(project_id, query_text, result_links)

        # insert upper part of answer
        if query_id is not None:
            answer_id = db_controller.grader_answer_insert(grader_id, query_id, query_link=current_url)
        else:
            print_at("Error: query insert unsuccessfully.", tg)
    return answer_id

def update_db_ans(project_type, db_controller, grader_id, answer_id, ans, tg):
    if project_type in config.UPDATE_DB_PROJS:
        # update grader answer
        if answer_id is not None:
            db_controller.grader_answer_update(grader_id, answer_id, answer=ans)
        else:
            print_at("Error: answer insert unsuccessfully", tg)

