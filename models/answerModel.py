from models import commandModel
from views.prints import *

def enter(placeholder, graders, terminal):
    terminal.activate()  # back to terminal shell for input
    user_input = input(placeholder)

    # exception for valid project because mostly the answer is 'n'
    if graders.grader.project_type == 'valid' and len(user_input) == 0:
        user_input = 'n'

    command_string = commandModel.control_command_check(graders, user_input)
    return user_input, command_string