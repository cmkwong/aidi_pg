from models import commandModel
from views.prints import *
import config
from appscript import *
terminal = app('Terminal')

def enter(graders):
    # setting placeholder
    placeholder = 'Answer Input: '
    if graders.auto_mode: placeholder = 'Answer Input-a: '

    # extra print if needed
    if graders.extra_preAction == True:
        if graders.grader.project_type == "classify":
            print_list(graders.grader, config.classify_extra_info_list)
        elif graders.grader.project_type == "sbs":
            print_list(graders.grader, config.sbs_extra_info_list)
            graders.grader.web_controller.zoom_browser(0.8)
            graders.grader.web_controller.scrollIntoView(graders.grader.project_type)

    terminal.activate()             # back to terminal shell for input
    user_input = input(placeholder) # waiting user input

    # exception for valid/side-by-side project because mostly the answer is 'n'
    if (graders.grader.project_type == 'valid' or graders.grader.project_type == 'sbs') and len(user_input) == 0:
        user_input = 'n'

    command = commandModel.control_command_check(graders, user_input)
    return user_input, command