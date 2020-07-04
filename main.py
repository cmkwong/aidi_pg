import web
import common
import db
from appscript import *

command_string = "command_not_checked"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
web_controller = web.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
db_controller = db.Database()
graders = common.Graders(web_controller, db_controller)

terminal = app('Terminal')
first_time = True
while (not (command_string == "quit")):

    if first_time:
        PROJECT_TYPE = common.menu_choice()
        graders.setup_project(PROJECT_TYPE)

    # try: # bigger exception, avoid accidently close down
    print("Answer Input: ")
    terminal.activate()  # back to terminal shell for input
    user_command = input()
    command_string = common.control_command_check(graders, user_command)
    if command_string == "command_not_checked":
        gradingFinish = graders.decode(user_command)
    if (graders.grader.new_query):
        graders.print_status()
    # except:
    #     print("Might be your input so fast.")
    #     continue
    first_time = False
web_controller.quite_driver()