import config
from models import menuModel, reportModel, infoModel, authModel, dbModel
from controllers import gradingController, tgController
from utils import inputs, osSystem
from views.prints import *
import datetime

def control_command_check(graders, ans):
    command_checked = True
    command_not_checked = False
    quit_program = "quit"

    if ans == '':
        print("cannot input empty string")
        return command_checked

    if ans[0] == '-':
        # ------------------------------getting user level and update grader info--------------------------------- #
        try:
            if graders.grader.grader_level == 0:
                graders.grader.grader_level = authModel.get_grader_access_level_from_cc(graders)
            # update grader info
            if graders.grader.grader_id is None:
                graders.grader.grader_id = dbModel.update_grader_info_from_cc(graders.grader.web_controller)
        except:
            graders.grader.grader_level = 0

        # ------------------------------Commands--------------------------------- #
        if graders.grader.grader_level >= 0:

            if (ans == "-q"):
                return quit_program

        if graders.grader.grader_level >= 1:

            if (ans == "-p"):
                graders.grader.db_controller.get_project_list()
                project_index = menuModel.menu_choice(graders.prev_project_index)
                graders.open_project(project_index)
                return command_checked

            elif (ans == "-pe"):  # project error
                try:
                    # check if pop-up
                    popUp_locale = graders.grader.web_controller.check_project_finished_popUp()
                    if popUp_locale:
                        # get the project info and grader name
                        project_id = graders.grader.web_controller.get_projectId_from_url()
                        grader_name = graders.grader.web_controller.get_grader_name_from_cc()
                        graders.grader.db_controller.project_finish_update(project_id, popUp_locale, grader_name, graders.grader.tg)
                    else:
                        print("No Finished Pop-up.")
                except:
                    print("Please try again.")
                return command_checked

            elif (ans == "-t"):
                time_delay = gradingController.time_delay_set()
                if not time_delay:
                    print("Set timer failed. Try again.")
                else:
                    graders.grader.time_delay = time_delay
                    print("Time delay: ", time_delay)
                return command_checked

            elif (ans == "-md"):
                graders.grader.manual_timer = True
                print("Manual timer activated. \nPress -nd to cancel.")
                return command_checked

            elif (ans == "-nd"):
                graders.grader.manual_timer = False
                print("Manual timer cancel. \nPress -md to activated.")
                return command_checked

            elif (ans == "-done"):
                print("Please enter the number: ")
                num = inputs.int_input()
                if (num == None):
                    print("Invalid input.")
                else:
                    print("Successful")
                    graders.grader.query_done = num
                return command_checked

            elif (ans == "-limit"):
                print("Please enter the number: ")
                num = inputs.int_input()
                if (num == None):
                    print("Invalid input.")
                else:
                    print("Successful")
                    graders.grader.done_upper_limit = num
                return command_checked

            elif (ans == "-alarm"):
                graders.grader.alarm = True
                print("Alarm sound activated.")
                return command_checked

            elif (ans == "-nalarm"):
                graders.grader.alarm = False
                print("Alarm sound de-activated.")
                return command_checked

            elif (ans == "-zoom"):
                print("Please enter the number(0.5-1.5): ")
                num = inputs.float_input()
                if (num == None):
                    print("Invalid input.")
                else:
                    if graders.grader.web_controller.zoom_browser(num):
                        print("Successful")
                return command_checked

            elif (ans == "-help"):
                for ptype, info in config.help_command.items():
                    print(ptype, ": ")
                    for index, description in info.items():
                        print(index, ": ", description)
                    print("")
                return command_checked

            elif (ans == "-mute"):  # print less mode
                graders.grader.print_allowed = False
                graders.grader.view = False
                print("Print less.")
                return command_checked

            elif (ans == "-nmute"):  # print more mode
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
                graders.web_controller.zoom_body_style(0.7)
                return command_checked

            elif (ans == "-text"):
                try:
                    report = graders.grader.web_controller.get_report_data()
                    if report:
                        reportModel.print_report(report)
                    else:
                        print("No report")
                except:
                    print("Error")
                return command_checked

            elif (ans == "-sc"):
                try:
                    saved_dir = reportModel.print_screen(graders.grader.web_controller)
                    print("saved in {}.".format(saved_dir))
                except:
                    print('screenshot error')
                return command_checked

            elif (ans == "-ssc"):
                try:
                    saved_dir = reportModel.print_screen(graders.grader.web_controller, saved=True)
                    print("saved in {}.".format(saved_dir))
                except:
                    print('screenshot error')
                return command_checked

            elif (ans == "-pay"):
                try:
                    usr_name = graders.grader.web_controller.get_grader_name_from_cc()
                    expired_date = graders.grader.db_controller.get_expired_date(usr_name)
                    print("Due date before: \u001b[31m{}\u001b[0m".format(expired_date))
                    print("Please attach your \u001b[32mname\u001b[0m on the payment description.")
                    osSystem.show_img('./src/payme_qr.png')
                except:
                    print('Please try again.')
                return command_checked

        if graders.grader.grader_level >= 2:
            if (ans == "-auto" or ans == "--a"):
                gradingController.set_auto_mode(graders)
                return command_checked

            elif (ans == "-nauto"):
                gradingController.resume_standard_mode(graders)
                print("Auto-mode de-activated.")
                return command_checked

            elif (ans == "-view"):
                graders.grader.view = True
                print("grader-ans show.")
                return command_checked

            elif (ans == "-nview"):
                graders.grader.view = False
                print("grader-ans hide.")
                return command_checked

            elif (ans == "-df"):
                graders.grader.find_delay = True
                print("Delay find answer activated.")
                return command_checked

            elif (ans == "-ndf"):
                graders.grader.find_delay = False
                print("Delay find answer de-activated.")
                return command_checked

            elif (ans == "-fauto"):
                gradingController.set_full_auto_mode(graders)
                return command_checked

            elif (ans == "-nfauto"):
                gradingController.resume_standard_mode(graders)
                print("Full auto de-activated")
                return command_checked

            elif (ans == "-timeout"):
                print("Please enter the number: ")
                num = inputs.int_input()
                if (num == None):
                    print("Invalid input.")
                else:
                    print("Successful")
                    graders.grader.info_timeout = num
                return command_checked

            elif (ans == "-dist"):
                try:
                    graders.grader.project_setup()
                    graders.grader.query_prepare(auto=False)
                    print("Finding: {} ({})".format(graders.grader.query_text, graders.grader.query_code))
                    Answer = graders.grader.db_controller.find_most_popular(graders.grader.project_id,
                                                                            graders.grader.project_locale,
                                                                            graders.grader.query_code)
                    gradingController.print_popular_ans_detail(Answer, graders.grader.tg)
                except:
                    print_at(config.MESSAGE_NOT_FOUND, graders.grader.tg)
                return command_checked

            elif (ans == "--test_tg"):
                link_details = graders.grader.web_controller.get_link_details('standard')
                print(link_details)
                return command_checked

            elif (ans == "-tg"):
                gradingController.resume_standard_mode(graders)
                token = authModel.get_grader_tgToken_from_cc(graders)
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

            elif (ans == "-train"):
                graders.grader.training = True
                print("Training mode activated.")
                return command_checked

            elif (ans == "-ntrain"):
                graders.grader.training = False
                print("Training mode de-activated.")
                return command_checked

            elif (ans == "-conflict"):
                project_id = input("Input project ID: ")
                grader_name = graders.web_controller.get_grader_name_from_cc()
                conflict = graders.grader.db_controller.find_conflict(project_id, grader_name, graders.grader.tg, print_allowed=True)
                if conflict:
                    print_conflict(conflict, graders.grader.tg)
                return command_checked

        if graders.grader.grader_level >= 3:
            if (ans == "-gp"):
                graders.grader.db_controller.get_ghost_project_list()
                project_index = menuModel.menu_choice(graders.prev_project_index, ghost=True)
                graders.open_project(project_index, ghost_menu=True)
                return command_checked

            elif (ans == "--ftd"):
                time_delay = gradingController.time_delay_set()
                if not time_delay:
                    print("Set timer failed. Try again.")
                else:
                    graders.grader.find_time_delay = time_delay
                    print("Find Ans Time delay: ", time_delay)
                return command_checked

            elif (ans == "-lazyconfig"):
                gradingController.set_lazy_mode(graders)
                return command_checked

            elif (ans == "-checkCode"):
                project_code = infoModel.get_project_code(graders.grader.web_controller)
                for key, value in project_code.items():
                    print("{}: {}".format(key, value))
                return command_checked

            elif (ans == "-getcheat"):
                graders.grader.web_controller.get_cheat_sheet_querys()
                return command_checked

            elif (ans == "-incheat"):
                path = "../../../Desktop"
                file_name = "cheatsheet.csv"
                osSystem.read_cheat_sheet(path, file_name)
                return command_checked

            elif (ans == "-outcheat"):
                path = "../../../Desktop"
                file_name = "cheatsheet.csv"
                osSystem.output_cheat_sheet(path, file_name)
                return command_checked

        print("Invalid Command")
        return command_checked  # avoid to go further in the ans parser if user type command wrongly
    else:
        return command_not_checked