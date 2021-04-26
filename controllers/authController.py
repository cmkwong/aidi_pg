from .. import config

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