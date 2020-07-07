import projects
from config import *

MAX_PROJ_NUM = len(projects_info)

def num_input_check():
    try:
        num_input = input()
        num_input = int(num_input)
    except ValueError:
        print("That is not a number. \nPlease enter a Number.")
        return None
    except KeyboardInterrupt:
        print("Wrong input")
        return None
    return num_input

def time_delay_set(graders):
    print("Enter the delay time(Second): ")
    time_delay = num_input_check()
    if ((time_delay < 10) or (time_delay > 260)):
        print("Invalid range. (10-260)")
        time_delay = None
    if (time_delay is not None):
        graders.grader.time_delay = time_delay
        print("Time delay: ", time_delay)
        return True
    else:
        print("Time delay cannot set.")
        return False

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
        project_index = num_input_check()
        if project_index == None:
            continue
        if (project_index <= 0 or project_index > MAX_PROJ_NUM):
            print("Invalid range of Number.")
            project_index = None
            continue
        project_index = project_index - 1
        project_type = projects_info[project_index]["type"]
    print("Type of Project: ", project_type, " activated.")
    return project_index

class Graders:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.grader = None
        self.projects_query_done = 0
        self.auto_mode = False

    def setup_project(self, project_index):
        self.grader = projects.base_grader(self.web_controller, self.db_controller)
        self.grader.project_type = projects_info[project_index]["type"]
        link = projects_info[project_index]["link"]
        #link = "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-spot2-2020-06-29/grading/zh_HK/s/8830c484a27f24a4b7b10e83587dcac0/r/8830c484a27f24a4b7b10e83587dcac0"
        self.grader.web_controller.open_project_link(link)

    def decode(self, ans):
        if (self.auto_mode == False):
            gradingFinish = self.grader.execute(ans)
            return gradingFinish
        elif (self.auto_mode == True):
            gradingFinish = self.grader.auto_execute()
            if gradingFinish == False:
                self.auto_mode = False
            return gradingFinish

    def get_query_done(self):
        return (self.projects_query_done + self.grader.query_done)

    def print_status(self):
        print("Done: ", self.get_query_done())

def control_command_check(graders, ans):
    command_checked = "command_checked"
    command_not_checked = "command_not_checked"
    auto_activated = "auto"
    quit_program = "quit"

    if (ans[0:2] == "-l"):
        url = ans[3:]
        graders.grader.web_controller.open_project_link(url)
        return command_checked

    elif (ans[0:2] == "-q"):
        return quit_program

    elif (ans[0:2] == "-p"):
        graders.projects_query_done = graders.grader.query_done # keep previous amount of done number
        project_index = menu_choice()
        graders.setup_project(project_index)
        return command_checked

    elif (ans[0:5] == "-auto"):
        if graders.auto_mode == False:
            graders.auto_mode = True
            set_ok = time_delay_set(graders)
            if not set_ok:
                graders.auto_mode = False
                print("Set auto mode failed. Try again.")
                return False
            print("Auto-mode activated.")
            return auto_activated
        elif graders.auto_mode == True:
            graders.auto_mode = False
            print("Auto-mode de-activated.")
            return False

    elif (ans[0:2] == "-t"):
        _ = time_delay_set(graders)
        return command_checked

    elif (ans[0:4] == "--rg"):
        graders.grader.db_controller.graders_id_update()
        return command_checked

    elif (ans[0:4] == "--rp"):
        graders.grader.db_controller.project_info_update()
        return command_checked

    else:
        return command_not_checked




