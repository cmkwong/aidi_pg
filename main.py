import web
import common
from appscript import *
user_command = "-p"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
controller = web.web_controller(init_url=default_url)
controller.open_chrome()
controller.init_working_tag()
decoder = common.Decoder(controller)
terminal = app('Terminal')
while (user_command!='-q'):

    if (user_command == "-p"):
        PROJECT_TYPE = common.menu_choice()
        decoder.setup_project(PROJECT_TYPE)

    if (decoder.grader.new_query):
        decoder.print_status()
    print("Answer Input: ")
    terminal.activate() # back to terminal shell for input
    user_command = input()
    try: # bigger exception, avoid accidently close down
        common.control_command_check(decoder.grader, user_command)
        if user_command != "-q" and user_command != "-p":
            gradingFinish = decoder.decode(user_command)
    except:
        print("Might be your input so fast.")
        continue

controller.quite_driver()