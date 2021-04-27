import config
from models import menuModel, reportModel, answerModel
from controllers import authController, gradingController, tgController
from utils.inputs import *
from views.prints import *
import datetime

def control_command_check(graders, ans):
    command_checked = "command_checked"
    command_not_checked = "command_not_checked"
    quit_program = "quit"

    if ans == '':
        print("cannot input empty string")
        return command_checked

    if ans[0] == '-':

        if (ans == "-q"):
            return quit_program

        elif (ans == "-p"):
            graders.grader.db_controller.update_local_config_from_db()
            project_index = menuModel.menu_choice()
            graders.setup_project(project_index, new_grader=False)
            return command_checked

        elif (ans == "-gp"):
            graders.grader.db_controller.update_local_config_from_db()
            project_index = menuModel.ghost_menu_choice()
            graders.setup_project(project_index, new_grader=False, ghost_menu=True)
            return command_checked

        elif (ans == "-auto" or ans == "--a"):
            level = authController.get_grader_access_level(graders)
            if level == 's' or level == 'a':
                gradingController.set_auto_mode(graders)
            return command_checked

        elif (ans == "-nauto"):
            gradingController.resume_standard_mode(graders)
            print("Auto-mode de-activated.")
            return command_checked

        elif (ans == "-t"):
            set_ok = gradingController.time_delay_set(graders, ans)
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
            set_ok = gradingController.time_delay_set(graders, ans)
            if not set_ok:
                print("Set timer failed. Try again.")
            return command_checked

        elif (ans == "-fauto"):
            level = authController.get_grader_access_level(graders)
            if level == 's':
                gradingController.set_full_auto_mode(graders)
            return command_checked

        elif (ans == "-nfauto"):
            gradingController.resume_standard_mode(graders)
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
            level = authController.get_grader_access_level(graders)
            if level == 's':
                gradingController.set_lazy_mode(graders)
            return command_checked

        elif (ans == "-done"):
            print("Please enter the number: ")
            done = num_check()
            if (done == None):
                print("Invalid input.")
            else:
                print("Successful")
                graders.grader.query_done = done
            return command_checked

        elif (ans == "-limit"):
            print("Please enter the number: ")
            limit = num_check()
            if (limit == None):
                print("Invalid input.")
            else:
                print("Successful")
                graders.grader.done_upper_limit = limit
            return command_checked

        elif (ans == "-telegram"):
            gradingController.resume_standard_mode(graders)
            token = authController.get_grader_tg_token(graders)
            tg = tgController.Telegram_Bot(token=token)
            graders.grader.tg = tg
            print("Telegram Online\n"
                  "Type /s in your telegram chat room\n"
                  "Type /q in your telegram chat room if you want to quit telegram\n"
                  "DO NOT turn off this MAC WIFI")
            try:
                tg.run(graders)  # Looping
            except Exception:
                pass
            print("Telegram Offline")
            gradingController.resume_standard_mode(graders)
            return command_checked

        elif (ans == "-mute"): # print less mode
            graders.grader.print_allowed = False
            graders.grader.view = False
            print("Print less.")
            return command_checked

        elif (ans == "-nmute"): # print more mode
            graders.grader.print_allowed = True
            graders.grader.view = True
            print("Print more.")
            return command_checked

        elif (ans == "-report") or (ans == "-re"):
            # get the current date
            now = datetime.datetime.now()
            month, day = config.MONTHS[now.month], now.day
            graders.web_controller.browser.get("https://crowdcollect2.siri.apple.com/reports/productivity")
            graders.web_controller.check_current_report(month, day)
            graders.web_controller.zoom_browser(0.7)
            return command_checked

        elif (ans == "-txt"):
            try:
                report = graders.grader.web_controller.get_report_data()
                if report:
                    reportModel.print_report(report)
                else:
                    print("No report")
            except:
                print("Disabled")
            return command_checked

        elif (ans == "-train"):
            graders.grader.training = True
            print("Training mode activated.")
            return command_checked

        elif (ans == "-ntrain"):
            graders.grader.training = False
            print("Training mode de-activated.")
            return command_checked

        elif (ans == "-conflict"):
            level = authController.get_grader_access_level(graders)
            if level == 's':
                project_id = input("Input project ID: ")
                usr_id = graders.web_controller.get_grader_id()
                conflict = graders.grader.db_controller.find_conflict(project_id, usr_id, graders.grader.tg, print_allowed=True)
                if conflict:
                    print_conflict(conflict, graders.grader.tg)
            return command_checked

        # elif (ans == "--rg"):
        #     graders.grader.db_controller.graders_id_update()
        #     return command_checked
        #
        # elif (ans == "--rp"):
        #     graders.grader.db_controller.project_info_update()
        #     return command_checked
        #
        # elif (ans == "--rgp"):
        #     graders.grader.db_controller.ghost_project_info_update()
        #     return command_checked
        #
        # elif (ans == "--rv"):
        #     graders.grader.db_controller.version_update()
        #     return command_checked

        else:
            print("Invalid Control Command")
            return command_checked  # avoid to go further in the ans parser if user type command wrongly
    else:
        return command_not_checked