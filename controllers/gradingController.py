import time
import tkinter as tk
from functools import partial
import config
from models import gradingModel, dbModel, infoModel, answerModel
from views.prints import *
from utils import inputs, sounds

def resume_standard_mode(graders):
    # reset auto mode
    graders.auto_mode = False
    graders.auto_available = True
    # reset the full-auto
    graders.grader.full_auto = False
    graders.grader.find_delay = False
    graders.grader.find_time_delay = 240
    # reset tg mode
    graders.grader.tg = None
    # print_allowed
    graders.grader.print_allowed = True
    return True

def set_auto_mode(graders):
    graders.auto_mode = True
    graders.auto_available = True
    # reset the full-auto
    graders.grader.full_auto = False
    graders.grader.find_delay = False

def set_full_auto_mode(graders):
    graders.auto_mode = True
    graders.auto_available = True
    graders.grader.full_auto = True
    graders.grader.find_delay = True

def set_lazy_mode(graders):
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

def resume_tg_manual_mode(graders):
    # reset auto mode
    graders.auto_mode = False
    graders.auto_available = True
    # reset the full-auto
    graders.grader.full_auto = False
    graders.grader.find_delay = False
    return True

def time_delay_set(graders, ans, overtime_bypass=False):
    print("Enter the delay time(Second): ")
    time_delay = inputs.num_check()
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

class Graders:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.grader = None
        self.auto_mode = False
        self.auto_available = True
        self.print_extra_info = False

    def setup_project(self, project_index, new_grader=True, ghost_menu=False):
        if ghost_menu:
            type = config.ghost_projects_info[project_index]["type"]
            link = config.ghost_projects_info[project_index]["link"]
        else:
            type = config.projects_info[project_index]["type"]
            link = config.projects_info[project_index]["link"]

        if new_grader:
            # create new grader
            self.grader = base_grader(self.web_controller, self.db_controller)
        # set the project type
        self.grader.project_type = type
        # open the required project link
        self.grader.web_controller.open_project_link(link)
        # if tg mode, then help to click required location
        if self.grader.tg is not None:
            self.web_controller.click_start_project(project_index)

        # situations depend different project type
        # run the TOKEN program immediately
        if type == "token":
            if self.grader.tg is None:
                print("GUI program running....")
                self.grader.token_GUI_execute()
            else:
                print_at("That is not proper project in telegram\nSet up project failed", self.grader.tg)
                return False

        # run classify need extra info provided
        elif type == "classify":
            if self.grader.tg is None:
                self.print_extra_info = True
            else:
                print_at("That is not proper project in telegram\nSet up project failed", self.grader.tg)
                return False
        return True

    def decode(self, command, ans=''):
        if (not self.auto_mode and not command) or (self.auto_mode and not self.auto_available and not command):
            gradingFinish = self.grader.execute(ans)
            return gradingFinish
        elif (self.auto_mode and self.auto_available and not command):
            gradingFinish = self.grader.auto_execute()
            return gradingFinish

    def run(self):
        if self.auto_mode == False:

            user_input, command = answerModel.enter(self)
            _ = self.decode(command, user_input)

        elif self.auto_mode == True:

            if self.auto_available == True:
                self.auto_available = self.decode(command=False)

            # usually because answer cannot found so auto_available=False
            if self.auto_available == False:
                user_input, command = answerModel.enter(self)
                self.auto_available = self.decode(command, user_input)

        if (self.grader.new_query):
            print_status(self.grader)
            limit_reached = gradingModel.check_limit_reached(self.grader)
            if limit_reached:  # check for limit reach, if do, assign auto_available=false
                self.auto_available = False
            self.grader.new_query = False

        return user_input

class base_grader:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.query_link = None
        self.query_text = None
        self.p_query_text = None
        self.query_done = 0
        self.done_upper_limit = -1  # stop when done reach the custom limit and reset once reached
        self.new_query = False
        self.grader_id = None
        self.project_id = None
        self.project_locale = None
        self.project_type = None
        self.time_delay = 1
        self.find_delay = False
        self.find_time_delay = 240
        self.manual_timer = False
        self.view = False               # print grader answer
        self.full_auto = False
        self.project_code = {}          # only used if project_type=standard. Otherwise, it is special project type, eg token
        # sound alarm
        self.alarm = True
        # telegram tg
        self.tg = None
        self.print_allowed = True       # most likely is just for telegram, mute and nmute command to control
        self.tg_timer_interrupt_signal = False
        self.timer_running = False
        # training mode, if so, find ans from most popular one
        self.training = False

    def renew_status(self):

        # update grader_id (for access the DB)
        if self.grader_id is None:
            self.grader_id = dbModel.update_grader_info(self.web_controller, self.db_controller)

        # renew project info every grading
        self.project_id, self.project_locale = self.web_controller.get_project_id_locale_from_url()
        if not self.project_id or not self.project_locale:
            print_at("Invalid grading in this page.", self.tg, self.print_allowed)
            return False

        # get query text
        self.query_text = infoModel.get_query_text(self.project_type, self.tg, self.web_controller, self.print_allowed)
        if self.query_text == None:
            return False
        self.query_link = self.web_controller.get_motherTag_url()
        self.new_query = False

        # get project code in when project_type: standard mode
        if self.project_id in config.projects_code.keys():
            self.project_code = config.projects_code[self.project_id]
        else:
            self.project_code = infoModel.get_project_code(self.web_controller, self.project_type) # get the project code if have not seen before
            config.projects_code[self.project_id] = self.project_code       # store the project_code into global dictionary (config)

        return True

    def update_status(self):
        # increase the query done if it is new query
        if (self.query_text != self.p_query_text):
            self.query_done = self.query_done + 1
            self.p_query_text = self.query_text
            self.new_query = True

    def reopen_current_browser(self):
        self.web_controller.open_chrome()
        self.web_controller.init_working_tag()
        self.web_controller.open_project_link(self.query_link)

    def delay_timer(self, time_used=0, alarm=True):
        self.timer_running = True
        try:
            if self.full_auto:
                time_delay = self.time_delay + 1 - time_used
                if time_delay <= 0:
                    time_delay = 1
            else:
                time_delay = self.time_delay + 1
            print_at("Delay...", self.tg, print_allowed=self.print_allowed)
            for i in reversed(range(0, time_delay)):
                time.sleep(1)
                if not self.tg: print(i, " seconds", end='\r')
                # tg stop interrupt
                if self.tg_timer_interrupt_signal:
                    self.tg_timer_interrupt_signal = False
                    self.timer_running = False
                    return False
            if alarm:
                sounds.beep("Times up", self.tg)
        except KeyboardInterrupt:
            self.reopen_current_browser()
            if not self.tg: print("Timer interrupted. Reopening...")
            self.timer_running = False
            return False
        self.timer_running = False
        return True

    def delay_find_for_answer(self):
        try:
            # delay to find
            print_at("Finding Ans Delay ... Max:" + str(self.find_time_delay), self.tg,
                     print_allowed=self.print_allowed)
            self.timer_running = True
            for i in reversed(range(0, self.find_time_delay + 1)):
                time.sleep(1)
                if not self.tg: print(i, " seconds", end='\r')
                if self.tg_timer_interrupt_signal:
                    self.tg_timer_interrupt_signal = False
                    self.timer_running = False
                    return False

                # read from database every 20 seconds
                time_interval = gradingModel.find_time_delay_level(self.find_time_delay)
                if ((i % time_interval) == 0) or ((i % self.find_time_delay) == 0):
                    if self.training:
                        Answer = self.db_controller.find_most_popular(self.project_id, self.project_locale, self.query_text, self.tg, print_allowed=False)
                    else:
                        Answer = self.db_controller.find_one_ans(self.project_id, self.project_locale, self.query_text, self.tg, print_allowed=False)
                    if Answer != None:
                        Answer.find_ok, Answer.find_time_used = True, self.find_time_delay - i
                        self.timer_running = False
                        return Answer

            self.timer_running = False
            return None
        except KeyboardInterrupt:
            self.reopen_current_browser()
            if not self.tg: print("Timer interrupted. Reopening...")
            self.timer_running = False
            return False

    def execute(self, ans):
        renew_ok = self.renew_status()
        if not renew_ok:
            return False
        # check if there is base command: ~, `, !
        base_command = gradingModel.base_code_check(self.web_controller, self.project_type, ans, max_answer_slots=self.project_code["max_answer_slots"], tg=self.tg)
        if base_command:
            return False
        # otherwise
        else:

            # insert query and grader info into database
            query_id = None
            if self.project_type in config.UPDATE_DB_PROJS:
                query_id = self.db_controller.query_insert(self.project_type, self.project_id, self.project_locale, self.query_text, self.web_controller)
                if not query_id:
                    return False

            # press web search if in tg mode
            if self.tg is not None:
                self.web_controller.flash_all_tags(self.project_code["max_answer_slots"], self.project_type)

            # execute the command
            grade_ok = gradingModel.grading(ans, self.web_controller, self.project_type, self.tg, auto=False, project_code=self.project_code)
            if not grade_ok:
                return False

            # timer
            if self.manual_timer:
                timer_ok = self.delay_timer(alarm=self.alarm)
                if not timer_ok:
                    return False

            self.web_controller.click_next_btn()

            # update ans into db
            if self.project_type in config.UPDATE_DB_PROJS:
                self.db_controller.answer_insert(ans, self.grader_id, query_id, self.query_link)

            # update status after finish a grading
            self.update_status()

            return True

    def auto_execute(self):
        # auto mode
        renew_ok = self.renew_status()
        if not renew_ok:
            return False

        if self.view:
            print_at("text: " + self.query_text, self.tg)

        # find delay
        Answer = None
        if self.find_delay:
            Answer = self.delay_find_for_answer() # Answer = False: interrupted; Answer = None: Not Found
            if Answer == False:
                return False

        # not find delay
        elif not self.find_delay:
            if self.training:
                Answer = self.db_controller.find_most_popular(self.project_id, self.project_locale, self.query_text, self.tg)
            else:
                Answer = self.db_controller.find_one_ans(self.project_id, self.project_locale, self.query_text, self.tg)

        # if no Answer found, return false, auto_available will be false
        if (Answer == None):
            if self.alarm:
                sounds.beep("Times up", self.tg)   # Not Found
            print_at("Not Found!\n", self.tg)
            return False

        if self.view:
            # if query and answer found
            if self.training:
                print_popular_ans_detail(Answer, self.tg)
            else: # if not training
                print_at("Got from: " + str(Answer.grader_name) + "\nAns: " + str(Answer.ans), self.tg)

        # timer delay
        timer_ok = self.delay_timer(time_used=Answer.find_time_used, alarm=False)
        if not timer_ok:
            return False

        # press web search
        self.web_controller.flash_all_tags(self.project_code["max_answer_slots"], self.project_type)

        # grading ans that from database
        grade_ok = gradingModel.grading(Answer.ans, self.web_controller, self.project_type, self.tg, auto=True, project_code=self.project_code)
        if not grade_ok:
            return False

        # press next
        self.web_controller.click_next_btn()

        # update status after finish a grading
        self.update_status()

        return True

    def token_GUI_execute(self):
        window = tk.Tk()
        window.title("Token")
        window.wm_attributes("-topmost", 1)

        def grade_handler(self):
            try:
                # grading
                grade_ok = gradingModel.grading("-k-", self.web_controller, self.project_type, self.tg)
                # click next button
                window.focus_force()
                if grade_ok:
                    self.web_controller.click_next_btn()
            except:
                print("grading failed - token")

            window.focus_force()

        def vague_handler(self):
            try:
                # grading
                grade_ok = gradingModel.grading("-n-", self.web_controller, self.project_type, self.tg)
                # click next button
                window.focus_force()
                if grade_ok:
                    self.web_controller.click_next_btn()
            except:
                print("vague failed - token")

        send_btn = tk.Button(window, text="Grade", fg="green", command=partial(grade_handler, self))
        vague_btn = tk.Button(window, text="Vague", fg="red", command=partial(vague_handler, self))

        vague_btn.grid(row=0, column=0)
        send_btn.grid(row=0, column=1)

        # listen the event
        window.mainloop()
        print("GUI program turned-off.")

