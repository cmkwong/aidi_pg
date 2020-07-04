import projects
from config import *

MAX_PROJ_NUM = len(projects_info)

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
    return num_input-1

def print_proj_list():
    print("\n")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    print("Please choose the required project Number: ")
    for index, project in enumerate(projects_info):
        print((index+1), ": ", project["_id"])

def menu_choice():
    project_index = None
    project_type = None
    while(project_index==None):
        print_proj_list()
        project_index = menu_input()
        if project_index == None:
            continue
        project_type = projects_info[project_index]["type"]
    print("Type of Project: ", project_type, " activated.")
    return project_index

class Graders:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.grader = None
        self.projects_query_done = 0

    def setup_project(self, project_index):
        self.grader = projects.base_grader(self.web_controller, self.db_controller)
        self.grader.project_type = projects_info[project_index]["type"]
        link = projects_info[project_index]["link"]
        #link = "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-spot2-2020-06-29/grading/zh_HK/s/8830c484a27f24a4b7b10e83587dcac0/r/8830c484a27f24a4b7b10e83587dcac0"
        self.grader.web_controller.open_project_link(link)

    def decode(self, ans):
        gradingFinish = self.grader.execute(ans)
        return gradingFinish

    def get_query_done(self):
        return (self.projects_query_done + self.grader.query_done)

    def print_status(self):
        print("Done: ", self.get_query_done())

def control_command_check(graders, ans):
    if (ans[0:2] == "-l"):
        url = ans[3:]
        graders.grader.web_controller.open_project_link(url)
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
    elif (ans[0:4] == "--rg"):
        graders.grader.db_controller.graders_id_update()
    elif (ans[0:4] == "--rp"):
        graders.grader.db_controller.project_info_update()
    else:
        command_string = "command_not_checked"
        return command_string




