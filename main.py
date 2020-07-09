import web
import common
import db
from appscript import *

command_string = "command_not_checked"
user_command = None

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
web_controller = web.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
db_controller = db.Database()
graders = common.Graders(web_controller, db_controller)

terminal = app('Terminal')
first_time = True
auto_available = True

while (not (command_string == "quit")):

    if first_time:
        project_index = common.menu_choice()
        graders.setup_project(project_index)
        first_time = False

    # try: # bigger exception, avoid accidently close down

    if graders.auto_mode == False:
        print("Answer Input: ")
        terminal.activate()  # back to terminal shell for input
        user_command = input()
        command_string = common.control_command_check(graders, user_command)
        if command_string == "command_not_checked":
            gradingFinish = graders.decode(user_command)

    if graders.auto_mode == True:
        _ = ""
        if auto_available == True:
            auto_available = graders.decode(_)
        if auto_available == False:
            print("Answer Input-a: ")
            terminal.activate()  # back to terminal shell for input
            user_command = input()
            command_string = common.control_command_check(graders, user_command)
            if command_string == "command_not_checked":
                graders.auto_mode = False
                auto_available = graders.decode(user_command)
                graders.auto_mode = True

    if (graders.grader.new_query):
        graders.print_status()
        graders.grader.new_query = False

    # except:
    #     print("Might be your input so fast.")
    #     continue
web_controller.quite_driver()