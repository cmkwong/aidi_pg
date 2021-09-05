import config
from datetime import datetime

def get_grader_access_level(graders):
    try:
        usr_id = graders.web_controller.get_grader_id()
    except:
        return None
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["level"]
    return None

def get_grader_tg_token(graders):
    usr_id = graders.web_controller.get_grader_id()
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["token"]
    return None

def get_expired_date(graders):
    usr_name = graders.grader.web_controller.get_user_name()
    expired_date = graders.grader.db_controller.get_expired_date(usr_name)
    return expired_date

def paid(graders):
    expired_date = get_expired_date(graders)
    # compare the expired date and current time
    if (datetime.strptime(expired_date, "%Y-%m-%d %H:%M").timestamp() - datetime.now().timestamp() < 0):
        return False
    return True