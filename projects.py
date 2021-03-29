import time
import tkinter as tk
from functools import partial
import numpy as np
import os
import common
import config

def base_code_check(controller, ans, max_web_search_links, tg=None):
    if (ans == '`'):
        # web_search
        try:
            controller.click_web_search()
        except:
            common.print_at("Not available '`'", tg)
            return None # None is Error
        return True
    elif (ans == '!'):
        # close other tags
        try:
            controller.close_other_tags()
        except:
            common.print_at("Not available '!'", tg)
            return None
        return True
    elif (ans == '~'):
        click_all_links_ok = controller.click_all_links(max_web_search_links)
        if not click_all_links_ok:
            common.print_at("Not available '~'", tg)
            return None
        return click_all_links_ok
    else:
        return False # False = continue

class base_grader:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.current_url = None
        self.query_text = None
        self.p_query_text = None
        self.query_done = 0
        self.done_upper_limit = -1  # stop when done reach the custom limit and reset once reached
        self.new_query = False
        self.grader_id = None
        self.project_id = None
        self.project_type = None
        self.time_delay = 1
        self.find_delay = False
        self.find_time_delay = 60
        self.manual_timer = False
        self.view = False               # print grader answer
        self.full_auto = False
        self.max_web_search_links = 3
        # sound alarm
        self.alarm = True
        # telegram tg
        self.tg = None
        self.print_allowed = True       # most likely is just for telegram, mute and nmute command to control
        self.tg_timer_interrupt_signal = False
        self.timer_running = False
        # training mode, if so, find ans from most popular one
        self.training = False

    def update_grader_info(self):
        self.grader_id = self.web_controller.get_grader_id()
        # update the project id
        project_link = self.web_controller.get_motherTag_url()
        self.project_id = self.web_controller.get_project_id_from_url(project_link)
        # update the db login info
        login, pw = self.db_controller.grader_id_to_login_info(self.grader_id)
        self.db_controller.update_db_config(login=login, pw=pw)

    def renew_status(self):
        self.query_text = self.get_query_text()
        if self.query_text == None:
            return False
        self.current_url = self.web_controller.get_motherTag_url()
        self.new_query = False

        # if either has no grader id or project id
        if self.grader_id is None or self.project_id is None:
            self.update_grader_info()

        return True

    def check_limit_reached(self):
        # check if the done reached the custom limit
        if (self.query_done >= self.done_upper_limit) and (self.done_upper_limit > 0):
            common.print_at("Limit Reached.\n", self.tg)
            self.beep("Times up")
            self.done_upper_limit = -1 # reset
            return True
        return False

    def update_status(self):
        # increase the query done if it is new query
        if (self.query_text != self.p_query_text):
            self.query_done = self.query_done + 1
            self.p_query_text = self.query_text
            self.new_query = True

    def reopen_current_browser(self):
        self.web_controller.open_chrome()
        self.web_controller.init_working_tag()
        self.web_controller.open_project_link(self.current_url)

    def beep(self, text):
        if not self.tg:
            sound = "say " + text
            os.system(sound)

    def delay_timer(self, time_used=0, alarm=True):
        self.timer_running = True
        try:
            if self.full_auto:
                time_delay = self.time_delay + 1 - time_used
                if time_delay <= 0:
                    time_delay = 1
            else:
                time_delay = self.time_delay + 1
            common.print_at("Delay...", self.tg, print_allowed=self.print_allowed)
            for i in reversed(range(0, time_delay)):
                time.sleep(1)
                if not self.tg: print(i, " seconds", end='\r')
                # tg stop interrupt
                if self.tg_timer_interrupt_signal:
                    self.tg_timer_interrupt_signal = False
                    self.timer_running = False
                    return False
            if alarm:
                self.beep("Times up")
        except KeyboardInterrupt:
            self.reopen_current_browser()
            if not self.tg: print("Timer interrupted. Reopening...")
            self.timer_running = False
            return False
        self.timer_running = False
        return True

    def find_time_delay_level(self):
        if self.find_time_delay > 200:
            return 20
        elif self.find_time_delay <= 200 and self.find_time_delay > 100:
            return 10
        elif self.find_time_delay <= 100 and self.find_time_delay > 60:
            return 5
        elif self.find_time_delay <= 60 and self.find_time_delay > 20:
            return 4
        elif self.find_time_delay <= 20 and self.find_time_delay > 1:
            return 2

    def get_query_text(self, filter_query=None, time_out=10):
        query_text, filter_query = filter_query, filter_query
        if self.project_type in config.GET_QUERY_TEXT_PROJS:
            js_code = """
                var query_text = document.getElementsByClassName("iframe")[0].getElementsByTagName("iframe").item(0).contentDocument.getElementsByClassName("search-input form-control")[0].getAttribute("value");
                return query_text;
            """
        elif self.project_type == "token":
            js_code = """
                var query_text = document.querySelector("#input-field").querySelector("input").value;
                return query_text;
            """
        elif self.project_type == "classify":
            js_code = """
                var query_text = document.querySelector('#display-section').querySelector('h1').textContent;
                return query_text;
            """
        else:
            common.print_at("project type in renew function not set yet", self.tg)
            return None
        refer_time = time.time()
        common.print_at("Loading...", self.tg, print_allowed=self.print_allowed)
        while (query_text==filter_query):
            try:
                if (time.time() - refer_time) > time_out:
                    common.print_at("Time Out", self.tg)
                    return None
                query_text = self.web_controller.browser.execute_script(js_code)
                time.sleep(0.5)
            except:
                continue # continue looping
        return query_text

    def get_links_and_details(self, time_out=10):
        refer_time = time.time()
        links = []
        link_details = []
        while (len(links) == 0):
            try:
                if (time.time() - refer_time) > time_out:
                    return None
                # get links
                links = self.web_controller.get_links()
                # get links text
                link_details = self.web_controller.get_link_details()
                time.sleep(0.5)
            except:
                continue  # continue looping
        return links, link_details


    def get_query_url(self):
        js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
        query_web_search_url = self.web_controller.browser.execute_script(js_code)
        return query_web_search_url

    def insert_db_query(self):
        answer_id = None

        if self.project_type in config.UPDATE_DB_PROJS:
            # insert query and answer
            try:
                result_links = self.web_controller.get_links()
            except:
                result_links = []

            query_id = self.db_controller.query_insert(self.project_id, self.query_text, result_links)

            # insert upper part of answer
            if query_id is not None:
                answer_id = self.db_controller.grader_answer_insert(self.grader_id, query_id, query_link=self.current_url)
            else:
                common.print_at("Error: query insert unsuccessfully.", self.tg)

        return answer_id

    def update_db_ans(self, answer_id, ans):
        if self.project_type in config.UPDATE_DB_PROJS:
            # update grader answer
            if answer_id is not None:
                self.db_controller.grader_answer_update(self.grader_id, answer_id, answer=ans)
            else:
                common.print_at("Error: answer insert unsuccessfully", self.tg)

    # for tg_bot.py used
    def send_tg_info(self, old_query_text=None, time_out=10):
        length_links = 0
        # get query text (plus condition)
        query_text = self.get_query_text(filter_query=old_query_text, time_out=time_out)
        if not query_text:
            return False
        try:
            # get search date
            search_date = self.web_controller.get_search_date()
            # get web search links
            web_search_link = self.web_controller.get_web_search_link()
            # get links and its details
            links, link_details = self.get_links_and_details(time_out=10)
        except:
            return False
        # combined into one text
        max_index = min(len(links), self.max_web_search_links)
        text = search_date + '\n\n' + query_text + '\n' + \
               "web search link: " + web_search_link + '\n' + \
               "No. of Results: " + str(max_index)
        for i in range(max_index):
            text = text + "\n\n-*-*-*-*-*- " + str(i+1) + " -*-*-*--*-*-"
            text = text + '\n' + link_details[i][:600] + '\n' + links[i]
        # send message to tg
        self.tg.bot.send_message(self.tg.chat_id, text)
        return query_text

    def grading(self, ans, auto=False):
        if (self.project_type == "spot12"):
            if len(ans) > self.max_web_search_links:
                common.print_at("Wrong length of answer.", self.tg)
                return False
            num = 1
            for a in ans:
                if (a == 'i'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
                elif (a == 'l'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
                elif (a == 'x'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
                else:
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    if (a == 'e'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
                    elif (a == 'g'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
                    elif (a == 'f'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
                    elif (a == 'b'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
                    else:
                        common.print_at("--------Not correct ans detected.--------", self.tg)
                        return False
                num = num + 1
            if (len(ans) == 1):
                self.web_controller.click_by_id("result2_validationno_result2")
                self.web_controller.click_by_id("result3_validationno_result3")
            elif (len(ans) == 2):
                self.web_controller.click_by_id("result3_validationno_result3")
            return True

        elif (self.project_type == "amp") or (self.project_type == "maps"):
            if len(ans) > self.max_web_search_links:
                common.print_at("Wrong length of answer.", self.tg)
                return False
            num = 1
            for a in ans:
                if (a == 'i'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
                elif (a == 'l'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
                elif (a == 'x'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
                else:
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    if (a == 'e'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
                    elif (a == 'g'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
                    elif (a == 'f'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
                    elif (a == 'b'):
                        self.web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
                    else:
                        common.print_at("--------Not correct ans detected.--------", self.tg)
                        return False
                num = num + 1
            # the rest ans by 10 is no results
            no_results_length = self.max_web_search_links - len(ans)
            for i in range(no_results_length):
                command_string = "result" + str(num+i) + "_validationno_result" + str(num+i)
                self.web_controller.click_by_id(command_string)
            return True

        elif (self.project_type == "deepscrape"):
            # checking wrong length
            if ans[0] != 'n':
                if len(ans) > self.max_web_search_links:
                    common.print_at("Wrong length of answer.", self.tg)
                    return False
            else:
                if len(ans) > 11 or len(ans) == 1:
                    common.print_at("Wrong length of answer.", self.tg)
                    return False

            if ans[0] == 'v':
                # press vague
                self.web_controller.click_by_id("query_vagueyes_vague")
            else:
                self.web_controller.click_by_id("query_vagueno")
                if ans[0] == 'n':
                    # press query inappropriate
                    self.web_controller.click_by_id("query_appropriatefalse")
                    ans = ans[1:]
                else:
                    self.web_controller.click_by_id("query_appropriatetrue")
                num = 1
                for a in ans:
                    if (a == 'i'):
                        self.web_controller.click_by_id(
                            ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
                    elif (a == 'l'):
                        self.web_controller.click_by_id(
                            ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
                    elif (a == 'x'):
                        self.web_controller.click_by_id(
                            ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
                    else:
                        self.web_controller.click_by_id(
                            ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                        if (a == 'e'):
                            self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
                        elif (a == 'g'):
                            self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
                        elif (a == 'f'):
                            self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
                        elif (a == 'b'):
                            self.web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
                        else:
                            common.print_at("--------Not correct ans detected.--------", self.tg)
                            return False
                    self.web_controller.click_by_id(("result" + str(num+1) + "_shownyes"))
                    num = num + 1
                self.web_controller.click_by_id(("result" + str(num) + "_shownno"))
            return True

        elif (self.project_type == "saf"):
            num = 1
            if len(ans) > 1:
                common.print_at("Wrong length of answer.", self.tg)
                return False
            if (ans == 'i'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
            elif (ans == 'l'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
            elif (ans == 'x'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
            else:
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                if (ans == 'e'):
                    self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
                elif (ans == 'g'):
                    self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
                elif (ans == 'f'):
                    self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
                elif (ans == 'b'):
                    self.web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
                else:
                    common.print_at("--------Not correct ans detected.--------", self.tg)
                    return False
            return True

        elif (self.project_type == "eval3"):
            max_num = 3
            len_ans = len(ans)
            num = 1

            # checking wrong length
            if ans[0] != 'n':
                if len(ans) > 3:
                    common.print_at("Wrong length of answer.", self.tg)
                    return False
            else:
                if len(ans) > 4:
                    common.print_at("Wrong length of answer.", self.tg)
                    return False

            if ans[0] == 'v':
                # press vague
                self.web_controller.click_by_id("query_vagueyes_vague")
            else:
                self.web_controller.click_by_id("query_vagueno")
                if ans[0] == 'n':
                    # press query inappropriate
                    len_ans = len_ans - 1
                    self.web_controller.click_by_id("query_appropriatefalse")
                else:
                    self.web_controller.click_by_id("query_appropriatetrue")
                for a in ans:
                    if a == "i":
                        # press result inappropriate
                        self.web_controller.click_by_id("result" + str(num) + "_validationresult" + str(num) + "_inappropriate")
                    elif a == "l":
                        self.web_controller.click_by_id("result"+str(num)+"_validationresult"+str(num)+"_wrong_language")
                    elif a == "x":
                        self.web_controller.click_by_id("result"+str(num)+"_validationresult"+str(num)+"_cannot_be_judged")
                    else:
                        # press can be judge
                        self.web_controller.click_by_id(
                            "result" + str(num) + "_validationresult" + str(num) + "_can_be_judged")
                        if a == "e":
                            # press excellent
                            self.web_controller.click_by_id("result" + str(num) + "_relevanceexcellent")
                        elif a == "g":
                            # press good
                            self.web_controller.click_by_id("result" + str(num) + "_relevancegood")
                        elif a == "f":
                            # press fair
                            self.web_controller.click_by_id("result" + str(num) + "_relevancefair")
                        elif a == "b":
                            # press bad
                            self.web_controller.click_by_id("result" + str(num) + "_relevancebad")
                        else:
                            common.print_at("--------Not correct ans detected.--------", self.tg)
                            return False
                    if num == max_num:
                        continue
                    elif num == len_ans:
                        self.web_controller.click_by_id("result" + str(num+1) + "_shownno")
                    elif num < len_ans:
                        self.web_controller.click_by_id("result" + str(num+1) + "_shownyes")
                    num = num + 1
            return True

        elif (self.project_type == "token"):
            if (ans[0:3] == '-n-'):
                # press skip
                js_code = """
                    document.getElementById('gradingStateSkip - Poor quality / Ambiguous').click();
                """
                self.web_controller.browser.execute_script(js_code)
                # press token looping
                self.web_controller.click_tokens_btn()
            elif (ans[0:3] == '-k-'):
                js_code = """
                    document.getElementById("gradingStatePossible to grade").click();
                """
                self.web_controller.browser.execute_script(js_code)

                # press token looping
                self.web_controller.click_tokens_btn()
            return True

        elif (self.project_type == "classify"):
            if "-m" in ans:
                comment = ans[ans.find('-m')+3:]
                comment = comment.replace("\'", '')
                comment = comment.replace("\"", '')
                if auto == False:
                    self.web_controller.browser.execute_script("document.querySelector('textarea').value = '%s';" % comment)
                ans = ans[:ans.find('-m')].replace(' ', '')
            # topic
            if ans[0] is '1':
                self.web_controller.select_query_click('#query_topicarts_and_entertainment')
            elif ans[0] is '2':
                self.web_controller.select_query_click('#query_topicfood_and_drink')
            elif ans[0] is '3':
                self.web_controller.select_query_click('#query_topicsports')
            elif ans[0] is '4':
                self.web_controller.select_query_click('#query_topichealth_fitness_medicine_and_science')
            elif ans[0] is '5':
                self.web_controller.select_query_click('#query_topicgeneral_retailers_and_marketplaces')
            elif ans[0] is '6':
                self.web_controller.select_query_click('#query_topicbusiness_industry_economics_and_finance')
            elif ans[0] is '7':
                self.web_controller.select_query_click('#query_topiccomputing_technology_telecommunication_and_internet_use')
            elif ans[0] is '8':
                self.web_controller.select_query_click('#query_topiclife')
            elif ans[0] is '9':
                self.web_controller.select_query_click('#query_topicplaces_travel_cars_and_transportation')
            elif ans[0] is 'a':
                self.web_controller.select_query_click('#query_topicsociety')
            elif ans[0] is 'b':
                self.web_controller.select_query_click('#query_topicother_ambiguous_or_unknown')
            else:
                common.print_at("--------Not correct ans detected.--------", self.tg)
                return False
            # goal
            if ans[1] is '1':
                self.web_controller.select_query_click('#query_goallearn_about')
            elif ans[1] is '2':
                self.web_controller.select_query_click('#query_goallearn_answer')
            elif ans[1] is '3':
                self.web_controller.select_query_click('#query_goaleshop')
            elif ans[1] is '4':
                self.web_controller.select_query_click('#query_goallocate')
            elif ans[1] is '5':
                self.web_controller.select_query_click('#query_goalbe_entertained')
            elif ans[1] is '6':
                self.web_controller.select_query_click('#query_goallaunch_download')
            elif ans[1] is '7':
                self.web_controller.select_query_click('#query_goalfind_online_service')
            elif ans[1] is '8':
                self.web_controller.select_query_click('#query_goalnavigate')
            elif ans[1] is '9':
                self.web_controller.select_query_click('#query_goalunknown_other')
            else:
                common.print_at("--------Not correct ans detected.--------", self.tg)
                return False
            if len(ans) > 2:
                # loop: set the check false (reset)
                js_code = """
                    for (var i=0;i<21;i++) {
                        var checked = document.querySelectorAll('.ui.checkbox.checkbox-row input')[i].checked;
                        if (checked == true) {
                            document.querySelectorAll('.ui.checkbox.checkbox-row input')[i].click();
                            document.querySelectorAll('.ui.checkbox.checkbox-row input')[i].checked = false;
                        }
                    }
                """
                # set some delay because click action takes some time
                for _ in np.arange(2):
                    self.web_controller.browser.execute_script(js_code)
                    time.sleep(0.1)
                str_ans = "abcdefghijklmnopqrstu"
                for c in ans[2:]:
                    pos = str_ans.find(c)
                    if pos == -1:
                        common.print_at("--------Not correct ans detected.--------", self.tg)
                        return False
                    time.sleep(0.1)
                    self.web_controller.browser.execute_script("document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].click();")
                    time.sleep(0.1)
                    self.web_controller.browser.execute_script("document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].checked = true;")
            return True

        else:
            common.print_at("Project type not setup correctly.", self.tg)
            return False

    def execute(self, ans):
        renew_ok = self.renew_status()
        if not renew_ok:
            return False
        base_command = base_code_check(self.web_controller, ans, max_web_search_links=self.max_web_search_links, tg=self.tg)
        if ((base_command == True) or (base_command == None)):
            return False
        elif (not base_command):

            # insert query and grader info into database
            answer_id = self.insert_db_query()

            # press web search if in tg mode
            if self.tg is not None:
                self.web_controller.click_all_links(self.max_web_search_links)
                self.web_controller.close_other_tags()

            # execute the command
            grade_ok = self.grading(ans, auto=False)
            if not grade_ok:
                return False

            # timer
            if self.manual_timer:
                timer_ok = self.delay_timer(alarm=self.alarm)
                if not timer_ok:
                    return False

            self.web_controller.click_next_btn()

            # update ans into db
            self.update_db_ans(answer_id, ans)

            # update status after finish a grading
            self.update_status()

            return True

    def auto_execute(self):
        # auto mode
        renew_ok = self.renew_status()
        if not renew_ok:
            return False

        if self.view:
            common.print_at("text: " + self.query_text, self.tg)

        Answer = None
        # find delay
        find_time_used = 0
        if self.find_delay:
            try:
                # delay to find
                common.print_at("Finding Ans Delay ... Max:" + str(self.find_time_delay), self.tg, print_allowed=self.print_allowed)
                self.timer_running = True
                for i in reversed(range(0, self.find_time_delay+1)):
                    time.sleep(1)
                    if not self.tg: print(i, " seconds", end='\r')
                    if self.tg_timer_interrupt_signal:
                        self.tg_timer_interrupt_signal = False
                        self.timer_running = False
                        return False

                    # read from database every 5 seconds
                    time_interval = self.find_time_delay_level()
                    if ((i % time_interval) == 0) or ((i % self.find_time_delay) == 0):
                        if self.training:
                            Answer = self.db_controller.find_most_popular(self.project_id, self.query_text, self.tg, print_allowed=False)
                        else:
                            Answer = self.db_controller.find_one_ans(self.project_id, self.query_text, self.tg, print_allowed=False)
                        if Answer != None:
                            find_time_used = self.find_time_delay - i
                            self.timer_running = False
                            break
                self.timer_running = False
            except KeyboardInterrupt:
                self.reopen_current_browser()
                if not self.tg: print("Timer interrupted. Reopening...")
                self.timer_running = False
                return False

        # not find delay
        elif not self.find_delay:
            if self.training:
                Answer = self.db_controller.find_most_popular(self.project_id, self.query_text, self.tg)
            else:
                Answer = self.db_controller.find_one_ans(self.project_id, self.query_text, self.tg)

        # if no Answer found, return false, auto_available will be false
        if (Answer == None):
            if self.alarm:
                self.beep("Times up")   # Not Found
            common.print_at("Not Found!\n", self.tg)
            return False

        if self.view:
            # if query and answer found
            if self.training:
                common.print_popular_ans_detail(Answer, self.tg)
            else: # if not training
                common.print_at("Got from: " + str(Answer.grader_name) + "\nAns: " + str(Answer.ans), self.tg)

        # timer delay
        timer_ok = self.delay_timer(time_used=find_time_used, alarm=False)
        if not timer_ok:
            return False

        # press web search
        self.web_controller.click_all_links(self.max_web_search_links)
        self.web_controller.close_other_tags()

        # grading ans that from database
        grade_ok = self.grading(Answer.ans, auto=True)
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
                grade_ok = self.grading("-k-")
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
                grade_ok = self.grading("-n-")
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

