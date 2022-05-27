from models import commandModel
from views.prints import *
import config
from appscript import *
terminal = app('Terminal')

def enter(graders, command):
    # setting placeholder
    placeholder = 'Input: '
    if graders.auto_mode: placeholder = 'Input-a: '

    # extra print if needed
    if not command:
        if graders.grader.project_type == "classify":
            print_list(graders.grader, config.classify_extra_info_list)
        elif graders.grader.project_type == "sbs":
            print_list(graders.grader, config.sbs_extra_info_list)
            # graders.grader.web_controller.zoom_browser(0.8)
            graders.grader.web_controller.scrollIntoView(graders.grader.project_type)

    terminal.activate()             # back to terminal shell for input
    user_input = input(placeholder) # waiting user input

    # preset user-input
    if not command:
        if graders.grader.project_type == 'valid':
            user_input = 'n'

    command = commandModel.control_command_check(graders, user_input)
    return user_input, command