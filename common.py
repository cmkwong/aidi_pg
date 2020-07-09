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

def time_delay_set(graders, overtime_bypass=False):
    print("Enter the delay time(Second): ")
    time_delay = num_input_check()
    if not overtime_bypass:
        if ((time_delay < 1) or (time_delay > 260)):
            print("Invalid range. (1-260)")
            return False
    else:
        if (time_delay < 0):
            print("Timer cannot be negative.")
            return False
    graders.grader.time_delay = time_delay
    print("Time delay: ", time_delay)
    return True

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
        if self.grader:
            self.projects_query_done = self.grader.query_done
        self.grader = projects.base_grader(self.web_controller, self.db_controller)
        self.grader.project_type = projects_info[project_index]["type"]
        link = projects_info[project_index]["link"]
        #link = ""
        self.grader.web_controller.open_project_link(link)

    def decode(self, ans):
        if (self.auto_mode == False):
            gradingFinish = self.grader.execute(ans)
            return gradingFinish
        elif (self.auto_mode == True):
            gradingFinish = self.grader.auto_execute()
            return gradingFinish

    def get_query_done(self):
        return (self.projects_query_done + self.grader.query_done)

    def print_status(self):
        seconds = str(self.get_query_done()).strip()
        delays = str(self.grader.time_delay).strip()
        md = str(self.grader.manual_timer).strip()
        print("Done: " + seconds + " t-" + delays + " MD-" + md + "\n")

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
        graders.auto_mode = True
        print("Auto-mode activated.")
        return auto_activated

    elif (ans[0:6] == "-nauto"):
        graders.auto_mode = False
        print("Auto-mode de-activated.")
        return command_checked

    elif (ans[0:2] == "-t"):
        set_ok = time_delay_set(graders)
        if not set_ok:
            print("Set timer failed. Try again.")
        return command_checked

    elif (ans[0:3] == "-md"):
        if graders.grader.manual_timer == False:
            graders.grader.manual_timer = True
            print("Manual timer set. \nType '-ft' again for cancel.")
        elif graders.grader.manual_timer == True:
            graders.grader.manual_timer = False
            print("Manual timer cancel. \nType '-ft' again for activation.")

    elif (ans[0:4] == "--rg"):
        graders.grader.db_controller.graders_id_update()
        return command_checked

    elif (ans[0:4] == "--rp"):
        graders.grader.db_controller.project_info_update()
        return command_checked

    else:
        return command_not_checked




