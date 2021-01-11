import web
import common
import db
import config
from appscript import *

command_string = "command_not_checked"
user_command = None
VERSION = "0.0.3"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
web_controller = web.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
db_controller = db.Database()
graders = common.Graders(web_controller, db_controller)

terminal = app('Terminal')
FIRST_TIME = True
graders.auto_available = True
MAIN_LOOP_COUNT = 0

while (not (command_string == "quit")):

    # need the user re-open the program
    if MAIN_LOOP_COUNT % 50 == 0:
        if VERSION != graders.db_controller.get_most_updated_version():
            raise Exception("Outdated Version")

    if FIRST_TIME:
        # update the local info from remote database
        db_controller.update_local_config_from_db()
        # ask user choose projects
        project_index = common.menu_choice()
        graders.setup_project(project_index)
        FIRST_TIME = False

    if graders.auto_mode == False:

        # extra print needed
        if graders.print_extra_info == True:
            if graders.grader.project_type == "classify":
                graders.print_list(config.classify_extra_info_list)

        print("Answer Input: ")
        terminal.activate()  # back to terminal shell for input
        user_command = input()
        command_string = common.control_command_check(graders, user_command)
        if command_string == "command_not_checked":
            gradingFinish = graders.decode(user_command)

    elif graders.auto_mode == True:

        if graders.auto_available == True:
            graders.auto_available = graders.decode()
        if graders.auto_available == False:

            # extra print needed
            if graders.print_extra_info == True:
                if graders.grader.project_type == "classify":
                    graders.print_list(config.classify_extra_info_list)

            print("Answer Input-a: ")
            terminal.activate()  # back to terminal shell for input
            user_command = input()
            command_string = common.control_command_check(graders, user_command)
            if command_string == "command_not_checked":
                graders.auto_mode = False
                graders.auto_available = graders.decode(user_command)
                graders.auto_mode = True

    if (graders.grader.new_query):
        graders.print_status()
        limit_reached = graders.grader.check_limit_reached()
        if limit_reached:  # check for limit reach, if do, assign auto_available=false
            graders.auto_available = False
        graders.grader.new_query = False

    MAIN_LOOP_COUNT += 1

web_controller.quite_driver()