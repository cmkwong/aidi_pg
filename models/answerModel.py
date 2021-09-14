from models import commandModel
from appscript import *
terminal = app('Terminal')

def enter(checker):
    # setting placeholder
    placeholder = 'Input: '
    terminal.activate()             # back to terminal shell for input
    user_input = input(placeholder) # waiting user input

    command = commandModel.control_command_check(checker, user_input)
    return user_input, command