import web
import common
import db
from appscript import *

command_string = "command_not_checked"

# default_url = "https://crowdcollect2.siri.apple.com/main/project/"
# default_url = "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-spot2-2020-06-29/grading/zh_HK/s/8830c484a27f24a4b7b10e83587dcac0/r/8830c484a27f24a4b7b10e83587dcac0"
default_url = "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-spot2-2020-06-29/grading/zh_HK/s/a0c628c0eb0ea5ac694877af44ae6f91/r/a0c628c0eb0ea5ac694877af44ae6f91"
web_controller = web.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
db_controller = db.Database()
graders = common.Graders(web_controller, db_controller)

terminal = app('Terminal')
loop_count = 0
while (not (command_string == "quit")):

    if loop_count == 0: # first time
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
    loop_count = loop_count + 1
web_controller.quite_driver()