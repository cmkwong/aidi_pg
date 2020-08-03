import time
import tkinter as tk
from functools import partial
import numpy as np
import config

def base_code_check(controller, ans, max_web_search_links):
    if (ans == '`'):
        # web_search
        try:
            controller.click_web_search()
        except:
            print("Not available '`'")
            return None # None is Error
        return True
    elif (ans == '!'):
        # close other tags
        try:
            controller.close_other_tags()
        except:
            print("Not available '!'")
            return None
        return True
    elif (ans == '~'):
        # open three results
        try:
            links = controller.get_links()
        except:
            links = []
            print("Not available '~'")
            return None
        controller.open_links_new_tags(links, max_web_search_links)
        # open web search
        controller.click_web_search()
        return True
    elif (ans == ''):
        print("cannot input empty string")
        return None
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
        self.new_query = False
        self.grader_id = None
        self.project_id = None
        self.project_type = None
        self.time_delay = 1
        self.find_delay = False
        self.find_time_delay = 60
        self.manual_timer = False
        self.view = False

    def update_grader_info(self):
        self.grader_id = self.web_controller.get_grader_id()
        self.project_id = self.web_controller.get_project_id_from_url()
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

    def delay_timer(self):
        print("Delay...")
        try:
            for i in reversed(range(0, self.time_delay+1)):
                time.sleep(1)
                print(i, " seconds", end='\r')
        except KeyboardInterrupt:
            self.reopen_current_browser()
            print("Timer interrupted. Reopening...")
            return False
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

    def get_query_text(self):
        query_text = None
        if self.project_type in ["spot12", "saf", "eval3"]:
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
            print("project type in renew function not set yet")
            return None
        time_out = time.time()
        print("Loading Query....10s")
        while (query_text==None):
            try:
                if (time.time() - time_out) > 10:
                    print("Time Out")
                    return None
                query_text = self.web_controller.browser.execute_script(js_code)
                time.sleep(0.5)
            except:
                continue # continue looping
        return query_text

    def get_query_url(self):
        js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
        query_web_search_url = self.web_controller.browser.execute_script(js_code)
        return query_web_search_url

    def insert_db_query(self):
        answer_id = None

        if self.project_type in ["spot12", "saf", "eval3", "classify"]:
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
                print("Error: query insert unsuccessfully.")

        return answer_id

    def update_db_ans(self, answer_id, ans):
        if self.project_type in ["spot12", "saf", "eval3", "classify"]:
            # update grader answer
            if answer_id is not None:
                self.db_controller.grader_answer_update(self.grader_id, answer_id, answer=ans)
            else:
                print("Error: answer insert unsuccessfully")

    def grading(self, ans):
        if (self.project_type == "spot12"):
            if len(ans) > 3:
                print("Wrong length of answer.")
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
                        print("--------Not correct ans detected.--------")
                        return False
                num = num + 1
            if (len(ans) == 1):
                self.web_controller.click_by_id("result2_validationno_result2")
                self.web_controller.click_by_id("result3_validationno_result3")
            elif (len(ans) == 2):
                self.web_controller.click_by_id("result3_validationno_result3")
            return True

        elif (self.project_type == "saf"):
            num = 1
            if len(ans) > 1:
                print("Wrong length of answer.")
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
                    print("--------Not correct ans detected.--------")
                    return False
            return True

        elif (self.project_type == "eval3"):
            max_num = 3
            len_ans = len(ans)
            num = 1
            if len(ans) > 4:
                print("Wrong length of answer.")
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
                            print("--------Not correct ans detected.--------")
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
                self.web_controller.browser.execute_script("document.querySelector('textarea').value = '%s';" % comment)
                ans = ans[:ans.find('-m')].replace(' ', '')
            # topic
            if ans[0] is 'a':
                self.web_controller.select_query_click('#query_topicarts_and_entertainment')
            elif ans[0] is 'b':
                self.web_controller.select_query_click('#query_topicfood_and_drink')
            elif ans[0] is 'c':
                self.web_controller.select_query_click('#query_topicsports')
            elif ans[0] is 'd':
                self.web_controller.select_query_click('#query_topichealth_fitness_medicine_and_science')
            elif ans[0] is 'e':
                self.web_controller.select_query_click('#query_topicgeneral_retailers_and_marketplaces')
            elif ans[0] is 'f':
                self.web_controller.select_query_click('#query_topicbusiness_industry_economics_and_finance')
            elif ans[0] is 'g':
                self.web_controller.select_query_click('#query_topiccomputing_technology_telecommunication_and_internet_use')
            elif ans[0] is 'h':
                self.web_controller.select_query_click('#query_topiclife')
            elif ans[0] is 'i':
                self.web_controller.select_query_click('#query_topicplaces_travel_cars_and_transportation')
            elif ans[0] is 'j':
                self.web_controller.select_query_click('#query_topicsociety')
            elif ans[0] is 'k':
                self.web_controller.select_query_click('#query_topicother_ambiguous_or_unknown')
            else:
                print("--------Not correct ans detected.--------")
                return False
            # goal
            if ans[1] is 'a':
                self.web_controller.select_query_click('#query_goallearn_about')
            elif ans[1] is 'b':
                self.web_controller.select_query_click('#query_goallearn_answer')
            elif ans[1] is 'c':
                self.web_controller.select_query_click('#query_goaleshop')
            elif ans[1] is 'd':
                self.web_controller.select_query_click('#query_goallocate')
            elif ans[1] is 'e':
                self.web_controller.select_query_click('#query_goalbe_entertained')
            elif ans[1] is 'f':
                self.web_controller.select_query_click('#query_goallaunch_download')
            elif ans[1] is 'g':
                self.web_controller.select_query_click('#query_goalfind_online_service')
            elif ans[1] is 'h':
                self.web_controller.select_query_click('#query_goalnavigate')
            elif ans[1] is 'i':
                self.web_controller.select_query_click('#query_goalunknown_other')
            else:
                print("--------Not correct ans detected.--------")
                return False
            if len(ans) > 2:
                # loop: set the check false
                js_code = """
                    for (var i=0;i<21;i++) {
                        var checked = document.querySelectorAll('.ui.checkbox.checkbox-row input')[i].checked;
                        if (checked === true) {
                            document.querySelectorAll('.ui.checkbox.checkbox-row input')[i].click();
                        }
                    }
                """
                # set some delay because click action takes some time
                for _ in np.arange(2):
                    self.web_controller.browser.execute_script(js_code)
                    time.sleep(0.5)
                str_ans = "abcdefghijklmnopqrstu"
                for c in ans[2:]:
                    pos = str_ans.find(c)
                    if pos == -1:
                        print("--------Not correct ans detected.--------")
                        return False
                    time.sleep(0.1)
                    self.web_controller.browser.execute_script("document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].click();")
                    time.sleep(0.1)
                    self.web_controller.browser.execute_script("document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].checked = true;")
            return True

        else:
            print("Project type not setup correctly.")
            return False

    def execute(self, ans):
        renew_ok = self.renew_status()
        if not renew_ok:
            return False
        base_command = base_code_check(self.web_controller, ans, max_web_search_links=3)
        if ((base_command == True) or (base_command == None)):
            return False
        elif (not base_command):

            # insert query and grader info into database
            answer_id = self.insert_db_query()

            # execute the command
            grade_ok = self.grading(ans)
            if not grade_ok:
                return False

            # timer
            if self.manual_timer:
                timer_ok = self.delay_timer()
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
            print("text: ", self.query_text)

        ans = None
        grader_name = "Unknown"
        # find delay
        if self.find_delay:
            try:
                # delay to find
                print("Finding Ans Delay ... Max:", self.find_time_delay)
                for i in reversed(range(0, self.find_time_delay)):
                    time.sleep(1)
                    print(i+1, " seconds", end='\r')

                    # read from database every 5 seconds
                    time_interval = self.find_time_delay_level()
                    if ((i+1) % time_interval) == 0:
                        ans, grader_name = self.db_controller.find_one_ans(self.project_id, self.query_text, print_allowed=False)
                        if ans != None:
                            break
            except KeyboardInterrupt:
                self.reopen_current_browser()
                print("Timer interrupted. Reopening...")
                return False

        # not find delay
        elif not self.find_delay:
            ans, grader_name = self.db_controller.find_one_ans(self.project_id, self.query_text)

        # if no Answer found, return false, auto_available will be false
        if (ans == None):
            print("Not Found!\n")
            return False

        # press web search
        self.web_controller.click_web_search()
        self.web_controller.close_other_tags()

        if self.view:
            # if query and answer found
            print("Got from: ", grader_name, "\nAns: ", ans)

        # grading ans that from database
        grade_ok = self.grading(ans)
        if not grade_ok:
            return False

        timer_ok = self.delay_timer()
        if not timer_ok:
            return False
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

