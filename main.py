import config
from controllers import gradingController, dbController, webController, authController
from models import gradingModel, menuModel, answerModel
from views.prints import *
from appscript import *

command_string = "command_not_checked"
user_command = None
VERSION = "0.0.7"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
db_controller = dbController.Database()
web_controller = webController.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
graders = gradingController.Graders(web_controller, db_controller)

terminal = app('Terminal')
FIRST_TIME = True
graders.auto_available = True
MAIN_LOOP_COUNT = 0

while (not (command_string == "quit")):

    # check user version and paid status
    if MAIN_LOOP_COUNT % 30 == 0:
        if VERSION != graders.db_controller.get_most_updated_version():
            raise Exception("Outdated Version, re-open program.")
        if not authController.paid(graders):
            raise Exception("Please try again later.")

    if FIRST_TIME:
        # update the local info from remote database
        db_controller.update_local_config_from_db()
        # ask user choose projects
        project_index = menuModel.menu_choice()
        graders.setup_project(project_index)
        FIRST_TIME = False

    if graders.auto_mode == False:

        # extra print needed
        if graders.print_extra_info == True:
            if graders.grader.project_type == "classify":
                print_list(graders.grader, config.classify_extra_info_list)

        user_input, command_string = answerModel.enter('Answer Input: ', graders, terminal)
        if command_string == "command_not_checked":
            gradingFinish = graders.decode(user_input)

    elif graders.auto_mode == True:

        if graders.auto_available == True:
            graders.auto_available = graders.decode()
        if graders.auto_available == False:

            # extra print needed
            if graders.print_extra_info == True:
                if graders.grader.project_type == "classify":
                    print_list(graders.grader, config.classify_extra_info_list)

            user_input, command_string = answerModel.enter('Answer Input-a: ', graders, terminal)
            if command_string == "command_not_checked":
                graders.auto_mode = False
                graders.auto_available = graders.decode(user_input)
                graders.auto_mode = True

    if (graders.grader.new_query):
        print_status(graders.grader)
        limit_reached = gradingModel.check_limit_reached(graders.grader)
        if limit_reached:  # check for limit reach, if do, assign auto_available=false
            graders.auto_available = False
        graders.grader.new_query = False

    MAIN_LOOP_COUNT += 1

web_controller.quite_driver()