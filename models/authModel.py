import config
from datetime import datetime

def get_usrName_from_graderId(usr_id):
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["name"]

def get_grader_access_level_from_cc(graders): # checking command is permission to use
    try:
        usr_id = graders.web_controller.get_grader_id_from_cc()
    except:
        return 0
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return int(info["level"])
    return 0

def get_grader_tgToken_from_cc(graders):
    usr_id = graders.web_controller.get_grader_id_from_cc()
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["token"]
    return None

def paid_user(grader_id, db_controller):
    try:
        usr_name = get_usrName_from_graderId(grader_id)
        expired_date = db_controller.get_expired_date(usr_name)
        # compare the expired date and current time
        if (datetime.strptime(expired_date, "%Y-%m-%d %H:%M").timestamp() - datetime.now().timestamp() < 0):
            return False
        return True
    except:
        return False