import telebot
import common
import config

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
            while self.gradingFinish:
                self.gradingFinish = graders.decode()

                if (graders.grader.new_query):
                    graders.print_status()
                    graders.grader.new_query = False

            if self.gradingFinish is False:
                self.current_query_text = graders.grader.send_tg_info(old_query_text=self.old_query_text,
                                                                      time_out=10)
                self.next_query_check()
                # inside grader.py, need to set False for user input manually
                graders.auto_mode = False
                graders.auto_available = False
                self.bot.send_message(self.chat_id, "input-a:")

    def next_query_check(self):
        if self.current_query_text is False:
            self.tg_available = False
            self.bot.send_message(self.chat_id, "Cannot get the next query text\nType /s to continue or /q to quit")
        else:
            self.tg_available = True

    def run(self, graders):

        @self.bot.message_handler(commands=['q'])
        def quit_tg(message):
            self.bot.send_message(message.chat.id, "Mac disconnected. Bye.")
            raise Exception("Quite Telegram")

        @self.bot.message_handler(commands=['auto'])
        def auto_activate(message):
            if self.tg_available == False:
                self.bot.send_message(message.chat.id, "Please type /s first")
            else:
                level = common.get_grader_access_level(graders)
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

        @self.bot.message_handler(commands=['nauto'])
        def auto_deactivate(message):
            self.auto_user = False
            common.resume_tg_manual_mode(graders)
            self.bot.send_message(message.chat.id, "Auto-mode de-activated.")

        @self.bot.message_handler(commands=['fauto'])
        def fauto_activate(message):
            if self.tg_available == False:
                self.bot.send_message(message.chat.id, "Please type /s first")
            else:
                level = common.get_grader_access_level(graders)
                if level == 's':
                    self.auto_user = True
                    graders.auto_mode = True
                    graders.auto_available = True
                    graders.grader.full_auto = True
                    graders.grader.find_delay = True
                    graders.grader.find_time_delay = 320
                    self.bot.send_message(self.chat_id, "Full auto activated, time delay after found:" + str(graders.grader.time_delay))

                    # auto: loop finding, print, if not found, showing next query
                    self.auto_run(graders)

        @self.bot.message_handler(commands=['nfauto'])
        def nfauto_deactivate(message):
            self.auto_user = False
            common.resume_tg_manual_mode(graders)
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

        @self.bot.message_handler(commands=['silence'])
        def silence(message):
            graders.grader.print_allowed = False
            graders.grader.view = False
            self.bot.send_message(message.chat.id, "Silence On")

        @self.bot.message_handler(commands=['nsilence'])
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
            graders.grader.tg_timer_interrupt_signal = True
            self.bot.send_message(message.chat.id, "Timer Interrupted")

        @self.bot.message_handler(commands=['s'])
        def start_tg(message):
            self.chat_id = message.chat.id
            if self.chat_id is False:
                self.bot.send_message(self.chat_id, "Cannot get the chat ID")
                self.tg_available = False
            else:
                self.bot.send_message(self.chat_id, "Got the chat ID")
                self.current_query_text = graders.grader.send_tg_info()
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
                            graders.print_list(config.classify_extra_info_list)
                    user_command = message.text
                    self.gradingFinish = graders.decode(user_command)

                    # turn back to auto available
                    if self.auto_user:
                        graders.auto_mode = True
                        graders.auto_available = True

                    if (graders.grader.new_query):
                        graders.print_status()
                        graders.grader.new_query = False

                    # I dont want typing control command will come into here, so i set the condition if grading finished
                    if self.gradingFinish:
                        # waiting until next query next query
                        self.gradingFinish = False
                        self.old_query_text = self.current_query_text
                        if graders.auto_mode == False:
                            self.current_query_text = graders.grader.send_tg_info(old_query_text=self.old_query_text, time_out=10)
                            self.next_query_check()
                    if graders.auto_mode == False:
                        self.bot.send_message(self.chat_id, "Input:")

                    # auto: loop finding, print, if not found, showing next query
                    self.auto_run(graders)

        self.bot.polling()