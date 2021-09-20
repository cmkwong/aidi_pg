from controllers import gradingController, dbController, webController
from models import menuModel

command = False
VERSION = "0.0.10"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
db_controller = dbController.Database()
web_controller = webController.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
graders = gradingController.Graders(web_controller, db_controller, VERSION)

FIRST_TIME = True
MAIN_LOOP_COUNT = 0

while (not (command == "quit")):

    if FIRST_TIME:
        # update the local info from remote database
        db_controller.update_local_config_from_db()
        # ask user choose projects
        project_index = menuModel.menu_choice(graders.prev_project_index)
        graders.open_project(project_index)
        FIRST_TIME = False

    command = graders.run(command)

    MAIN_LOOP_COUNT += 1

web_controller.quite_driver()