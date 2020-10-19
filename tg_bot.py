# import telebot
# import common
# import config
#
# class Telegram_Bot:
#     def __init__(self, token):
#         self.chat_id = False
#         self.bot = telebot.TeleBot(token)
#         self.old_query_text = None
#         self.current_query_text = False
#         self.tg_available = False
#         self.gradingFinish = False
#         self.auto_user = False
#         self.ans_found = True
#
#     def handle_grading_finish(self, graders):
#
#         if (graders.grader.new_query):
#             graders.print_status()
#             graders.grader.new_query = False
#
#         # I dont want typing control command will come into here, so i set the condition if grading finished
#         if self.gradingFinish:
#             # waiting until next query next query
#             self.gradingFinish = False
#             if not graders.auto_mode:
#                 self.bot.send_message(self.chat_id, "Graded OK")
#                 self.old_query_text = self.current_query_text
#                 self.current_query_text = graders.grader.send_tg_info(old_query_text=self.old_query_text, time_out=10)
#                 if self.current_query_text is False:
#                     self.tg_available = False
#                     self.bot.send_message(self.chat_id, "Cannot get the next query text\nType /s to continue or /q to quit")
#
#         if self.auto_user:
#             graders.auto_mode = True
#
#     def run(self, graders):
#
#         @self.bot.message_handler(commands=['q'])
#         def send_message(message):
#             self.bot.send_message(message.chat.id, "Mac disconnected. Bye.")
#             raise Exception("Quite Telegram")
#
#         @self.bot.message_handler(commands=['s'])
#         def send_message(message):
#             self.chat_id = message.chat.id
#             if self.chat_id is False:
#                 self.bot.send_message(self.chat_id, "Cannot get the chat ID")
#                 self.tg_available = False
#             else:
#                 self.bot.send_message(self.chat_id, "Got the chat ID")
#                 self.current_query_text = graders.grader.send_tg_info()
#                 if self.current_query_text is False:
#                     self.bot.send_message(message.chat.id, "Cannot get the query text\nEnsure your Mac in correct page")
#                     self.tg_available = False
#                 else:
#                     self.tg_available = True
#
#         @self.bot.message_handler(commands=['auto'])
#         def send_message(message):
#
#             # authentication
#             pass
#
#
#         @self.bot.message_handler(func=lambda message: True)
#         def echo_message(message):
#
#             if self.tg_available == False:
#                 self.bot.send_message(message.chat.id, "Please type /s first")
#             else:
#                 if graders.auto_mode == False:
#
#                     # extra print needed
#                     if graders.print_extra_info == True:
#                         if graders.grader.project_type == "classify":
#                             graders.print_list(config.classify_extra_info_list)
#                     user_command = message.text
#                     self.gradingFinish = graders.decode(user_command)
#
#                     self.handle_grading_finish(graders)
#                     self.bot.send_message(self.chat_id, "Input:")
#
#                 elif graders.auto_mode == True:
#
#                     while graders.auto_available == True:
#                         self.ans_found = graders.decode()
#                         graders.auto_available = self.ans_found
#                         graders.auto_mode = graders.auto_available
#
#                         if (graders.grader.new_query):
#                             graders.print_status()
#                             graders.grader.new_query = False
#
#                     if self.ans_found is False:
#                         self.current_query_text = graders.grader.send_tg_info()
#                         if self.current_query_text is False:
#                             self.tg_available = False
#                             self.bot.send_message(self.chat_id, "Cannot get the next query text\nType /s to continue or /q to quit")
#
#                     graders.auto_mode = False
#
#         self.bot.polling()
