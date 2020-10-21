import projects
import config
import tg_bot

def print_at(txt, tg=None, print_allowed=True):
    if print_allowed:
        if tg == None:
            print(txt)
        else:
            tg.bot.send_message(tg.chat_id, txt)

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
    if time_delay == None:
        return False
    elif not overtime_bypass:
        if ((time_delay < 0) or (time_delay > 15000)):
            print("Invalid range. (0-15000)")
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

def get_grader_access_level(graders):
    usr_id = graders.web_controller.get_grader_id()
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["level"]
    return None

def get_grader_tg_token(graders):
    usr_id = graders.web_controller.get_grader_id()
    for info in config.graders_info:
        if usr_id == info["_id"]:
            return info["token"]
    return None

def resume_standard_mode(graders):
    # reset auto mode
    graders.auto_mode = False
    graders.auto_available = True
    # reset the full-auto
    graders.grader.full_auto = False
    graders.grader.find_delay = False
    graders.grader.find_time_delay = 60
    # reset tg mode
    graders.grader.tg = None
    # print_allowed
    graders.grader.print_allowed = True
    return True

def resume_tg_manual_mode(graders):
    # reset auto mode
    graders.auto_mode = False
    graders.auto_available = True
    # reset the full-auto
    graders.grader.full_auto = False
    graders.grader.find_delay = False
    graders.grader.find_time_delay = 60
    return True

class Graders:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.grader = None
        self.auto_mode = False
        self.auto_available = False
        self.print_extra_info = False

    def setup_project(self, project_index, new_grader=True):
        if new_grader:
            # create new grader
            self.grader = projects.base_grader(self.web_controller, self.db_controller)
        # set the project name
        self.grader.project_id = config.projects_info[project_index]["name"]
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

        if config.projects_info[project_index]["type"] == "spot12_ten":
            self.grader.max_web_search_links = 10
        else:
            self.grader.max_web_search_links = 3

    def print_list(self, str_list):
        for string in str_list:
            print_at(string, self.grader.tg)

    def decode(self, ans=''):
        if (self.auto_mode == False):
            gradingFinish = self.grader.execute(ans)
            return gradingFinish
        elif (self.auto_mode == True):
            gradingFinish = self.grader.auto_execute()
            return gradingFinish

    def print_status(self):
        done = str(self.grader.query_done).strip()
        delays = str(self.grader.time_delay).strip()
        md = str(self.grader.manual_timer).strip()
        print_at("Done: " + done + " t-" + delays + " MD-" + md + "\n", self.grader.tg, self.grader.print_allowed)

def control_command_check(graders, ans):
    command_checked = "command_checked"
    command_not_checked = "command_not_checked"
    auto_activated = "auto"
    quit_program = "quit"

    if ans == '':
        print("cannot input empty string")
        return command_checked

    if ans[0] == '-':

        if (ans == "-q"):
            return quit_program

        elif (ans == "-p"):
            graders.grader.db_controller.update_local_config_from_db()
            project_index = menu_choice()
            graders.setup_project(project_index, new_grader=False)
            return command_checked

        elif (ans == "-auto" or ans == "--a"):
            level = get_grader_access_level(graders)
            if level == 's' or level == 'a':
                graders.auto_mode = True
                graders.auto_available = True
                # reset the full-auto
                graders.grader.full_auto = False
                graders.grader.find_delay = False
                graders.grader.find_time_delay = 60
                print("Auto-mode activated.")
            return command_checked

        elif (ans == "-nauto"):
            resume_standard_mode(graders)
            print("Auto-mode de-activated.")
            return command_checked

        elif (ans == "-t"):
            set_ok = time_delay_set(graders, ans)
            if not set_ok:
                print("Set timer failed. Try again.")
            return command_checked

        elif (ans == "-md"):
            graders.grader.manual_timer = True
            print("Manual timer activated. \nPress -nd to cancel.")
            return command_checked

        elif (ans == "-nd"):
            graders.grader.manual_timer = False
            print("Manual timer cancel. \nPress -md to activated.")
            return command_checked

        elif (ans == "-view"):
            graders.grader.view = True
            print("grader-ans show.")
            return command_checked

        elif (ans == "-nview"):
            graders.grader.view = False
            print("grader-ans hide.")
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
            print("Delay find answer activated.")
            return command_checked

        elif (ans == "-ndf"):
            graders.grader.find_delay = False
            print("Delay find answer de-activated.")
            return command_checked

        elif (ans == "-dft"):
            set_ok = time_delay_set(graders, ans)
            if not set_ok:
                print("Set timer failed. Try again.")
            return command_checked

        elif (ans == "-fauto"):
            level = get_grader_access_level(graders)
            if level == 's':
                graders.auto_mode = True
                graders.auto_available = True
                graders.grader.full_auto = True
                graders.grader.find_delay = True
                graders.grader.find_time_delay = 320
                print("Full auto activated, time delay after found:", graders.grader.time_delay)
            return command_checked

        elif (ans == "-nfauto"):
            resume_standard_mode(graders)
            print("Full auto de-activated")
            return command_checked

        elif (ans == "-alarm"):
            graders.grader.alarm = True
            print("Alarm sound activated.")
            return command_checked

        elif (ans == "-nalarm"):
            graders.grader.alarm = False
            print("Alarm sound de-activated.")
            return command_checked

        elif (ans == "-lazyconfig"):
            level = get_grader_access_level(graders)
            if level == 's':
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

        elif (ans == "-done"):
            print("Please enter the number: ")
            done = num_input_check()
            if (done == None):
                print("Invalid input.")
            else:
                print("Successful")
                graders.grader.query_done = done
            return command_checked

        elif (ans == "-telegram"):
            resume_standard_mode(graders)
            token = get_grader_tg_token(graders)
            tg = tg_bot.Telegram_Bot(token=token)
            graders.grader.tg = tg
            print("Telegram Online\nType /s in your telegram chat room")
            try:
                tg.run(graders)  # Looping
            except Exception:
                pass
            print("Telegram Offline")
            resume_standard_mode(graders)
            return quit_program

        elif (ans == "-silence"): # print less mode
            graders.grader.print_allowed = False
            graders.grader.view = False
            print("Print less.")
            return command_checked

        elif (ans == "-nsilence"): # print more mode
            graders.grader.print_allowed = True
            graders.grader.view = True
            print("Print more.")
            return command_checked

        elif (ans == "--rg"):
            graders.grader.db_controller.graders_id_update()
            return command_checked

        elif (ans == "--rp"):
            graders.grader.db_controller.project_info_update()
            return command_checked
        else:
            print("Invalid Control Command")
            return command_checked  # avoid to go further in the ans parser if user type command wrongly
    else:
        return command_not_checked