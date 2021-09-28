from models import menuModel
from utils import inputs
import config

def control_command_check(checker, ans):
    command_checked = True
    command_not_checked = False
    quit_program = "quit"

    if ans == '':
        print("cannot input empty string")
        return command_checked

    if ans[0] == '-':

        if (ans == "-q"):
            return quit_program

        elif (ans == "-p"):
            # check version
            checker.check_version()
            # update local config: projects and graders
            checker.db_controller.update_local_config_from_db()
            # print the menu
            project_index = menuModel.menu_choice(checker.prev_project_index, config.projects_info)
            # print the project status
            checker.print_project_status(project_index)
            return command_checked

        elif (ans == "-r"):
            if checker.prev_project_index in range(len(config.projects_info)):
                checker.print_project_status(checker.prev_project_index)
            else:
                print("No project selected. Type -p.")
            return command_checked

        elif (ans == "-update"):
            # update the project list
            project_list = []
            try:
                project_list = checker.get_projectList_from_txt()
            except:
                print("Cannot get the project list")
            checker.print_projectList_confirm(project_list)
            confirmed = inputs.user_confirm()   # yes to confirm, else to cancel
            if confirmed:   # yes to confirm, else to cancel
                checker.db_controller.project_info_update(project_list)
            else:
                print("Cancelled")
            return command_checked

        else:
            print("Invalid Control Command")
            return command_checked  # avoid to go further in the ans parser if user type command wrongly
    else:
        return command_not_checked