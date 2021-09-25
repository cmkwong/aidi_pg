import collections

def update_grader_info(web_controller, db_controller):
    grader_id = web_controller.get_grader_id_from_cc()
    # update the db login info
    login, pw = db_controller.grader_id_to_login_info(grader_id)
    db_controller.update_db_config(login=login, pw=pw)
    return grader_id

def format_Answer():
    Answer = collections.namedtuple("Answer", ['find_ok', 'ans', 'find_time_used',
                                               'grader_name', 'ans_dist', 'detail', 'link'])
    Answer.find_ok, Answer.ans, Answer.find_time_used, \
    Answer.grader_name, Answer.ans_dist, Answer.detail, Answer.link \
        = False, None, 0, "Unknown", None, None, None
    return Answer