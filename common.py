import projects
import config

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

def time_delay_set(graders, ans, overtime_bypass=False):
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
    # set time delay
    if ans == "-t" and len(ans) == 2:
        graders.grader.time_delay = time_delay
        print("Time delay: ", time_delay)
        return True
    if ans == "-dft" and len(ans) == 4:
        graders.grader.find_time_delay = time_delay
        print("Find Ans Time delay: ", time_delay)
        return True

def print_proj_list():
    print("\n")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    print("Please choose the required project Number: ")
    for index, project in enumerate(config.projects_info):
        print((index+1), ": (", project["type"],") ", project["name"])

def menu_choice():
    max_proj_num = len(config.projects_info)
    project_index = None
    project_type = None
    while(project_index==None):
        print_proj_list()
        project_index = num_input_check()
        if project_index == None:
            continue
        if (project_index <= 0 or project_index > max_proj_num):
            print("Invalid range of Number.")
            project_index = None
            continue
        project_index = project_index - 1
        project_type = config.projects_info[project_index]["type"]
    print("Type of Project: ", project_type, " activated.")
    return project_index

class Graders:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.grader = None
        self.projects_query_done = 0
        self.auto_mode = False
        self.auto_available = False
        self.print_extra_info = False

    def setup_project(self, project_index):
        # keep the done count if user switch to other project
        if self.grader:
            self.projects_query_done = self.grader.query_done
        # create new grader
        self.grader = projects.base_grader(self.web_controller, self.db_controller)
        # set the project type
        self.grader.project_type = config.projects_info[project_index]["type"]
        # open the required project link
        link = config.projects_info[project_index]["link"]
        self.grader.web_controller.open_project_link(link)

        # run the TOKEN program immediately
        if config.projects_info[project_index]["type"] == "token":
            print("GUI program running....")
            self.grader.token_GUI_execute()

        # run classify need extra info provided
        if config.projects_info[project_index]["type"] == "classify":
            self.print_extra_info = True
        else:
            self.print_extra_info = False

    def print_list(self, str_list):
        for string in str_list:
            print(string)

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

    elif (ans == "-q"):
        return quit_program

    elif (ans == "-p"):
        graders.projects_query_done = graders.grader.query_done # keep previous amount of done number
        project_index = menu_choice()
        graders.setup_project(project_index)
        return command_checked

    elif (ans == "-auto" or ans == "--a"):
        graders.auto_mode = True
        graders.auto_available = True
        print("Auto-mode activated.")
        return auto_activated

    elif (ans == "-nauto"):
        graders.auto_mode = False
        print("Auto-mode de-activated.")
        return command_checked

    elif (ans == "-t"):
        set_ok = time_delay_set(graders, ans)
        if not set_ok:
            print("Set timer failed. Try again.")
        return command_checked

    elif (ans == "-md"):
        if graders.grader.manual_timer == False:
            graders.grader.manual_timer = True
            print("Manual timer set. \nType '-md' again for cancel.")
        elif graders.grader.manual_timer == True:
            graders.grader.manual_timer = False
            print("Manual timer cancel. \nType '-md' again for activation.")
        return command_checked

    elif (ans == "-view"):
        graders.grader.view = True
        print("grader-ans show.")
        return command_checked

    elif (ans == "-hide"):
        graders.grader.view = False
        print("grader-ans hide.")
        return command_checked

    elif (ans == "-update"):
        graders.grader.db_controller.update_local_config_from_db()
        print("Update info OK")
        return command_checked

    elif (ans == "-help"):
        for ptype, info in config.help_command.items():
            print(ptype, ": ")
            for index, description in info.items():
                print(index, ": ", description)
            print("")
        return command_checked

    elif (ans == "-df"):
        graders.grader.find_delay = True
        print("Delay Find Answer Activated.")
        return command_checked

    elif (ans == "-ndf"):
        graders.grader.find_delay = False
        print("Delay Find Answer De-activated.")
        return command_checked

    elif (ans == "-dft"):
        set_ok = time_delay_set(graders, ans)
        if not set_ok:
            print("Set timer failed. Try again.")
        return command_checked

    elif (ans == "-lazyconfig"):
        # view
        graders.grader.view = True
        # find ans delay
        graders.grader.find_delay = True
        graders.grader.find_time_delay = 60
        # next delay
        graders.grader.time_delay = 200
        # auto mode activate
        graders.auto_mode = True
        graders.auto_available = True
        print("Lazy config set done.")
        return command_checked

    elif (ans == "--rg"):
        graders.grader.db_controller.graders_id_update()
        return command_checked

    elif (ans == "--rp"):
        graders.grader.db_controller.project_info_update()
        return command_checked

    else:
        return command_not_checked




