from controllers import gradingController, dbController, webController, authController
from models import menuModel

command = ''
VERSION = "0.0.8"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
db_controller = dbController.Database()
web_controller = webController.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
graders = gradingController.Graders(web_controller, db_controller)

FIRST_TIME = True
MAIN_LOOP_COUNT = 0

while (not (command == "quit")):

    # check user version and paid status
    if MAIN_LOOP_COUNT % 30 == 0:
        # check user version
        if VERSION != graders.db_controller.get_most_updated_version():
            raise Exception("Outdated Version, re-open program.")
        # check payment
        if not authController.paid(graders):
            raise Exception("Please try again later.")

    if FIRST_TIME:
        # update the local info from remote database
        db_controller.update_local_config_from_db()
        # ask user choose projects
        project_index = menuModel.menu_choice()
        graders.setup_project(project_index)
        FIRST_TIME = False

    command = graders.run()

    MAIN_LOOP_COUNT += 1

web_controller.quite_driver()