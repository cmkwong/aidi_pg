import projects
MAX_PROJ_NUM = 2

def menu_input():
    try:
        num_input = input()
        num_input = int(num_input)
    except ValueError:
        print("That is not a number. \nPlease enter a Number.")
        return None
    except KeyboardInterrupt:
        print("Wrong input")
        return None
    if (num_input <= 0 or num_input > MAX_PROJ_NUM):
        print("Invalid range of Number.")
        return None
    return num_input

def print_proj_list():
    print("\n")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    print("Please choose the required project Number: ")
    print("1. spot1/2")
    print("2. saf")

def menu_choice():
    num_input = None
    while(num_input==None):
        print_proj_list()
        num_input = menu_input()
    print("Type of Project: ", num_input, " activated.")
    return num_input

class Graders:
    def __init__(self, web_controller):
        self.web_controller = web_controller
        self.grader = None
        self.projects_query_done = 0

    def setup_project(self, project_type):
        if (project_type == 1):
            self.grader = projects.spot12_project(self.web_controller)
        elif (project_type == 2):
            self.grader = projects.saf_project(self.web_controller)

    def decode(self, ans):
        gradingFinish = self.grader.grading(ans)
        return gradingFinish

    def get_query_done(self):
        return (self.projects_query_done + self.grader.query_done)

    def print_status(self):
        print("Done: ", self.get_query_done())

def control_command_check(graders, ans):
    if (ans[0:2] == "-l"):
        url = ans[3:]
        graders.grader.controller.open_project_link(url)
        command_string = "command_checked"
        return command_string
    elif (ans[0:2] == "-q"):
        command_string = "quit"
        return command_string
    elif (ans[0:2] == "-p"):
        graders.projects_query_done = graders.grader.query_done # keep previous amount of done number
        PROJECT_TYPE = menu_choice()
        graders.setup_project(PROJECT_TYPE)
        command_string = "command_checked"
        return command_string
    else:
        command_string = "command_not_checked"
        return command_string




