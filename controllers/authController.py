import config
from datetime import datetime

def get_usrName_from_graderId(usr_id):
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["name"]

def get_grader_access_level(graders):
    try:
        usr_id = graders.web_controller.get_grader_id()
    except:
        return None
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["level"]
    return None

def get_grader_tgToken(graders):
    usr_id = graders.web_controller.get_grader_id()
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["token"]
    return None

def paid(graders):
    try:
        usr_id = graders.grader.grader_id
        usr_name = get_usrName_from_graderId(usr_id)
        expired_date = graders.grader.db_controller.get_expired_date(usr_name)
        # compare the expired date and current time
        if (datetime.strptime(expired_date, "%Y-%m-%d %H:%M").timestamp() - datetime.now().timestamp() < 0):
            return False
        return True
    except:
        return True