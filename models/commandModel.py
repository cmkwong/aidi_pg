from models import menuModel

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
            checker.db_controller.update_local_config_from_db()
            project_index = menuModel.menu_choice()
            checker.print_project_status(project_index)
            return command_checked

        elif (ans == "-update"):
            # update the project list
            return command_checked

        else:
            print("Invalid Control Command")
            return command_checked  # avoid to go further in the ans parser if user type command wrongly
    else:
        return command_not_checked