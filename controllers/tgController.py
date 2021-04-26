import telebot
import config
from models import tgModel, menuModel
from controllers import gradingController, authController
from views.prints import *

class Telegram_Bot:
    def __init__(self, token):
        self.chat_id = False
        self.bot = telebot.TeleBot(token)
        self.old_query_text = None
        self.current_query_text = False
        self.tg_available = False
        self.gradingFinish = False
        self.auto_user = False

    def auto_run(self, graders):
        # start auto running first
        if graders.auto_mode == True:
            self.bot.send_message(self.chat_id, "Auto-mode activated\nAuto-running ... ")
            while graders.auto_available:
                graders.auto_available = graders.decode()

                if (graders.grader.new_query):
                    print_status(graders.grader)
                    graders.grader.new_query = False

            if graders.auto_available is False:
                self.current_query_text = graders.grader.send_tg_info(old_query_text=self.old_query_text,
                                                                      time_out=10)
                self.next_query_check()
                # inside grader.py, need to set False for user input manually
                graders.auto_mode = False
                self.bot.send_message(self.chat_id, "input-a:")

    def next_query_check(self):
        if self.current_query_text is False:
            self.tg_available = False
            self.bot.send_message(self.chat_id, "Cannot get the next query text\nType /s to continue or /q to quit")
        else:
            self.tg_available = True

    def stop_timer(self, graders, chat_id):
        if graders.grader.timer_running:
            graders.grader.tg_timer_interrupt_signal = True
            self.bot.send_message(chat_id, "Timer Interrupted")
            return True
        return False

    def run(self, graders):

        @self.bot.message_handler(commands=['q'])
        def quit_tg(message):
            self.stop_timer(graders, message.chat.id)
            self.bot.send_message(message.chat.id, "Telegram disconnected. Bye.")
            raise Exception("Quite Telegram")

        @self.bot.message_handler(commands=['p'])
        def select_project(message):
            graders.db_controller.update_local_config_from_db()
            project_list_txt = menuModel.get_project_list_text()
            msg = self.bot.reply_to(message, project_list_txt + "\nEnter project Number: ")
            self.bot.register_next_step_handler(msg, set_project)

        def set_project(message):
            project_index = message.text
            if not project_index.isdigit():
                self.bot.send_message(message.chat.id, "This is not a number")
                return False
            project_index = int(project_index) - 1
            project_type = config.projects_info[project_index]["type"]
            self.bot.send_message(message.chat.id, "Type of Project: " + project_type + " activated.")
            graders.setup_project(project_index, new_grader=False)
            # reset the grader
            self.stop_timer(graders, message.chat.id)
            gradingController.resume_tg_manual_mode(graders) # cancel auto mode
            self.tg_available = False

        @self.bot.message_handler(commands=['auto'])
        def auto_activate(message):
            if self.tg_available == False:
                self.bot.send_message(message.chat.id, "Please type /s first")
            else:
                level = authController.get_grader_access_level(graders)
                if level == 's' or level == 'a':
                    self.auto_user = True
                    graders.auto_mode = True
                    graders.auto_available = True
                    # reset the full-auto
                    graders.grader.full_auto = False
                    graders.grader.find_delay = False
                    graders.grader.find_time_delay = 60

                    # auto: loop finding, print, if not found, showing next query
                    self.auto_run(graders)
                else:
                    self.bot.send_message(message.chat.id, "Invalid Command")

        @self.bot.message_handler(commands=['nauto'])
        def auto_deactivate(message):
            self.auto_user = False
            gradingController.resume_tg_manual_mode(graders)
            self.bot.send_message(message.chat.id, "Auto-mode de-activated.")

        @self.bot.message_handler(commands=['fauto'])
        def fauto_activate(message):
            if self.tg_available == False:
                self.bot.send_message(message.chat.id, "Please type /s first")
            else:
                level = authController.get_grader_access_level(graders)
                if level == 's':
                    self.auto_user = True
                    graders.auto_mode = True
                    graders.auto_available = True
                    graders.grader.full_auto = True
                    graders.grader.find_delay = True
                    graders.grader.find_time_delay = 300
                    self.bot.send_message(self.chat_id, "Full auto activated, time delay after found:" + str(graders.grader.time_delay))

                    # auto: loop finding, print, if not found, showing next query
                    self.auto_run(graders)
                else:
                    self.bot.send_message(message.chat.id, "Invalid Command")

        @self.bot.message_handler(commands=['nfauto'])
        def nfauto_deactivate(message):
            self.auto_user = False
            gradingController.resume_tg_manual_mode(graders)
            self.bot.send_message(message.chat.id, "Full auto de-activated")

        @self.bot.message_handler(commands=['t'])
        def set_time_delay(message):
            msg = self.bot.reply_to(message, "Enter delay time(s): ")
            self.bot.register_next_step_handler(msg, enter_time)

        def enter_time(message):
            time = message.text
            if not time.isdigit():
                self.bot.send_message(message.chat.id, "This is not a number")
                return False
            graders.grader.time_delay = int(time)
            self.bot.send_message(message.chat.id, "Time delay set")

        @self.bot.message_handler(commands=['done'])
        def set_done_count(message):
            msg = self.bot.reply_to(message, "Enter done count: ")
            self.bot.register_next_step_handler(msg, set_done)

        def set_done(message):
            done = message.text
            if not done.isdigit():
                self.bot.send_message(message.chat.id, "This is not a number")
                return False
            graders.grader.query_done = int(done)
            self.bot.send_message(message.chat.id, "done count set")

        @self.bot.message_handler(commands=['view'])
        def view_grading(message):
            graders.grader.view = True
            self.bot.send_message(message.chat.id, "grader-ans show.")

        @self.bot.message_handler(commands=['nview'])
        def not_view_grading(message):
            graders.grader.view = False
            self.bot.send_message(message.chat.id, "grader-ans hide")

        @self.bot.message_handler(commands=['mute'])
        def silence(message):
            graders.grader.print_allowed = False
            graders.grader.view = False
            self.bot.send_message(message.chat.id, "Silence On")

        @self.bot.message_handler(commands=['nmute'])
        def not_silence(message):
            graders.grader.print_allowed = True
            graders.grader.view = False
            self.bot.send_message(message.chat.id, "Silence Off")

        @self.bot.message_handler(commands=['md'])
        def delay_on(message):
            graders.grader.manual_timer = True
            self.bot.send_message(message.chat.id, "Delay On")

        @self.bot.message_handler(commands=['nd'])
        def delay_off(message):
            graders.grader.manual_timer = False
            self.bot.send_message(message.chat.id, "Delay Off\n-nd to cancel")

        @self.bot.message_handler(commands=['stop'])
        def stop_timer(message):
            stopped = self.stop_timer(graders, message.chat.id)
            if not stopped:
                self.bot.send_message(message.chat.id, "Timer is not running")

        @self.bot.message_handler(commands=['status'])
        def check_status(message):
            done = str(graders.grader.query_done).strip()
            delays = str(graders.grader.time_delay).strip()
            md = str(graders.grader.manual_timer).strip()
            self.bot.send_message(message.chat.id, "Done: " + done + " t-" + delays + " MD-" + md)

        @self.bot.message_handler(commands=['train'])
        def set_train_mode(message):
            graders.grader.training = True
            self.bot.send_message(message.chat.id, "Train mode activated.")

        @self.bot.message_handler(commands=['ntrain'])
        def set_ntrain_mode(message):
            graders.grader.training = False
            self.bot.send_message(message.chat.id, "Train mode de-activated.")

        @self.bot.message_handler(commands=['conflict'])
        def set_project_id_for_conflict(message):
            if self.tg_available == False:
                self.bot.send_message(message.chat.id, "Please type /s first")
            else:
                level = authController.get_grader_access_level(graders)
                if level == 's':
                    msg = self.bot.reply_to(message, "Enter Project ID ")
                    self.bot.register_next_step_handler(msg, check_conflict)

        def check_conflict(message):
            project_id = message.text
            usr_id = graders.web_controller.get_grader_id()
            conflict = graders.grader.db_controller.find_conflict(project_id, usr_id, graders.grader.tg,print_allowed=True)
            if conflict:
                print_conflict(conflict, self)

        @self.bot.message_handler(commands=['limit'])
        def set_limit_number(message):
            msg = self.bot.reply_to(message, "Enter limit number: ")
            self.bot.register_next_step_handler(msg, set_limit)

        def set_limit(message):
            limit = message.text
            if not limit.isdigit():
                self.bot.send_message(message.chat.id, "This is not a number")
                return False
            graders.grader.done_upper_limit = int(limit)
            self.bot.send_message(message.chat.id, "Limit set")

        @self.bot.message_handler(commands=['help'])
        def help(message):
            help_text = ''
            for ptype, info in config.help_command.items():
                help_text = help_text + ptype + ": \n"
                for index, description in info.items():
                    help_text += index + ": " + description + '\n'
                help_text += '\n'
            self.bot.send_message(message.chat.id, help_text)

        @self.bot.message_handler(commands=['s'])
        def start_tg(message):
            self.chat_id = message.chat.id
            if self.chat_id is False:
                self.bot.send_message(self.chat_id, "Cannot get the chat ID")
                self.tg_available = False
            else:
                self.bot.send_message(self.chat_id, "Got the chat ID")
                self.current_query_text = tgModel.send_tg_info(graders.grader)
                self.next_query_check()

        @self.bot.message_handler(func=lambda message: True)
        def echo_message(message):

            if self.tg_available == False:
                self.bot.send_message(message.chat.id, "Please type /s first")
            else:
                if graders.auto_mode == False:

                    # extra print needed
                    if graders.print_extra_info == True:
                        if graders.grader.project_type == "classify":
                            print_list(graders.grader, config.classify_extra_info_list)
                    user_command = message.text
                    self.gradingFinish = graders.decode(user_command)

                    # turn back to auto available
                    if self.auto_user:
                        graders.auto_mode = True
                        graders.auto_available = True

                    if (graders.grader.new_query):
                        print_status(graders.grader)
                        graders.grader.new_query = False
                        # # check if limit reach
                        # limit_reached = graders.grader.check_limit_reached()
                        # if limit_reached:
                        #     self.auto_user = False
                        #     graders.auto_mode = False
                        #     graders.auto_available = False

                    # I dont want typing control command will come into here, so i set the condition if grading finished
                    if self.gradingFinish:
                        # waiting until next query next query
                        self.gradingFinish = False
                        self.old_query_text = self.current_query_text
                        if graders.auto_mode == False:
                            self.current_query_text = tgModel.send_tg_info(graders.grader, old_query_text=self.old_query_text, time_out=10)
                            self.next_query_check()
                    if graders.auto_mode == False:
                        self.bot.send_message(self.chat_id, "Input:")

                    # auto: loop finding, print, if not found, showing next query
                    self.auto_run(graders)

        self.bot.polling()