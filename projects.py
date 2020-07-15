import time
import tkinter as tk
from functools import partial

def base_code_check(controller, ans, max_web_search_links):
    if (ans[0] == '`'):
        # web_search
        try:
            controller.click_web_search()
        except:
            print("Not available '`'")
        return True
    elif (ans[0] == '!'):
        # close other tags
        try:
            controller.close_other_tags()
        except:
            print("Not available '!'")
        return True
    elif (ans[0] == '~'):
        # open three results
        try:
            links = controller.get_links()
        except:
            links = []
            print("Not available '~'")
        controller.open_links_new_tags(links, max_web_search_links)
        # open web search
        controller.click_web_search()
        return True
    else:
        return False

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
        self.time_delay = 2
        self.manual_timer = False
        self.view = False

    def renew_status(self):
        self.query_text = self.get_query_text()
        if self.query_text == None:
            return False
        self.current_url = self.web_controller.get_motherTag_url()
        self.new_query = False
        return True

    def update_status(self):
        # increase the query done if it is new query
        if (self.query_text != self.p_query_text):
            self.query_done = self.query_done + 1
            self.p_query_text = self.query_text
            self.new_query = True

    def delay_timer(self):
        print("Delay...")
        for i in reversed(range(0, self.time_delay+1)):
            time.sleep(1)
            print(i, " seconds", end='\r')

    def get_query_text(self):
        query_text = None
        if self.project_type == "spot12" or self.project_type == "saf" or self.project_type == "eval3":
            js_code = """
                var query_text = document.getElementsByClassName("iframe")[0].getElementsByTagName("iframe").item(0).contentDocument.getElementsByClassName("search-input form-control")[0].getAttribute("value");
                return query_text;
            """
        elif self.project_type == "token":
            js_code = """
                var query_text = document.querySelector("#input-field").querySelector("input").value;
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
        # insert query and answer
        try:
            result_links = self.web_controller.get_links()
        except:
            result_links = []
        if self.grader_id is None or self.project_id is None:
            self.grader_id = self.web_controller.get_grader_id()
            self.project_id = self.web_controller.get_project_id()
        query_id = self.db_controller.query_insert(self.project_id, self.query_text, result_links)
        answer_id = None
        if query_id is not None:
            answer_id = self.db_controller.grader_answer_insert(self.grader_id, query_id, query_link=self.current_url)
        else:
            print("Error: query insert unsuccessfully.")
        return answer_id

    def update_db_ans(self, answer_id, ans):
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
            else:
                # js_code = """
                #             document.querySelector('#input-field').querySelector("input").value = arguments[0];
                #         """
                # self.web_controller.browser.execute_script(js_code, ans)
                js_code = """
                    document.getElementById("gradingStatePossible to grade").click();
                    document.querySelector('#input-field').querySelector("input").value = '';
                """
                self.web_controller.browser.execute_script(js_code)
                # special way to send text into input-field
                inputElement = self.web_controller.browser.find_element_by_id("input-field").find_elements_by_tag_name("input")[0]
                for a in ans:
                    inputElement.send_keys(a)
                    #time.sleep(0.01)

                #press token looping
                self.web_controller.click_tokens_btn()
            return True

        else:
            print("Project type not setup correctly.")
            return False

    def spot_wrapper_execute(self, ans):
        renew_ok = self.renew_status()
        if not renew_ok:
            return False
        base_command = base_code_check(self.web_controller, ans, max_web_search_links=3)
        if (base_command):
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
                self.delay_timer()
            self.web_controller.click_next_btn()

            # update ans into db
            self.update_db_ans(answer_id, ans)

            # update status after finish a grading
            self.update_status()

            return True

    def spot_wrapper_auto_execute(self):
        # auto mode
        renew_ok = self.renew_status()
        if not renew_ok:
            return False
        if self.project_id is None:
            self.project_id = self.web_controller.get_project_id()

        if self.view:
            print("text: ", self.query_text)

        # read from database
        ans, grader_name = self.db_controller.find_one_ans(self.project_id, self.query_text)
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

        self.delay_timer()
        self.web_controller.click_next_btn()

        # update status after finish a grading
        self.update_status()

        return True

    def token_wrapper_execute(self):
        window = tk.Tk()
        window.title("Token")
        window.wm_attributes("-topmost", 1)

        entry = tk.Entry(fg="black", bg="white", width=50)

        def send_handler(self):
            try:
                # get entry text
                ans = entry.get()

                # grading
                grade_ok = self.grading(ans)
                time.sleep(0.5)
                # click next button
                #self.web_controller.click_next_btn()
            except:
                print("grading failed - token")

            window.focus_force()

        def vague_handler(self):
            try:
                grade_ok = self.grading("-n-")
                time.sleep(0.5)
                window.focus_force()
            except:
                print("vague failed - token")

        def read_handler(self):
            try:
                query_text = self.get_query_text()
                # delete text
                entry.delete(0, tk.END)
                entry.insert(0, query_text)
            except:
                print("read failed - token")

        send_btn = tk.Button(window, text="Grade", fg="green", command=partial(send_handler, self))
        bad_btn = tk.Button(window, text="Vague", fg="red", command=partial(vague_handler, self))
        read_btn = tk.Button(window, text="Read", fg="blue", command=partial(read_handler, self))

        bad_btn.grid(row=0, column=0)
        read_btn.grid(row=0, column=1)
        send_btn.grid(row=0, column=2)
        entry.grid(row=0, column=3)


        # listen the event
        window.mainloop()
        print("GUI program turned-off.")

