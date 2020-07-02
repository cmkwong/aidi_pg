import web
import common
from appscript import *
command_string = "command_not_checked"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
controller = web.web_controller(init_url=default_url)
controller.open_chrome()
controller.init_working_tag()
graders = common.Graders(controller)
terminal = app('Terminal')
loop_count = 0
while (not (command_string == "quit")):

    if loop_count == 0: # first time
        PROJECT_TYPE = common.menu_choice()
        graders.setup_project(PROJECT_TYPE)

    try: # bigger exception, avoid accidently close down
        print("Answer Input: ")
        terminal.activate()  # back to terminal shell for input
        user_command = input()
        command_string = common.control_command_check(graders, user_command)
        if command_string == "command_not_checked":
            gradingFinish = graders.decode(user_command)
        if (graders.grader.new_query):
            graders.print_status()
    except:
        print("Might be your input so fast.")
        continue
    loop_count = loop_count + 1
controller.quite_driver()