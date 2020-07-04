import time

def base_code_check(controller, ans, max_web_search_links):
    if (ans[0] == '`'):
        # web_search
        controller.click_web_search()
        return True
    elif (ans[0] == '!'):
        # close other tags
        controller.close_other_tags()
        return True
    elif (ans[0] == '~'):
        # open three results
        links = controller.get_links()
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
        self.previous_url = None
        self.current_url = None
        self.query_done = 0
        self.new_query = False
        self.grader_id = None
        self.project_id = None
        self.project_type = None

    def get_query_text(self):
        query_text = None
        js_code = """
            var query_text = document.getElementsByClassName("iframe")[0].getElementsByTagName("iframe").item(0).contentDocument.getElementsByClassName("search-input form-control")[0].getAttribute("value");
            return query_text;
        """
        js_code2 = "document.getElementsByClassName('search-input form-control')[0].getAttribute('value')"
        while (query_text==None):
            try:
                query_text = self.web_controller.browser.execute_script(js_code)
                time.sleep(0.5)
            except:
                continue
        return query_text

    def get_query_url(self):
        js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
        query_web_search_url = self.web_controller.browser.execute_script(js_code)
        return query_web_search_url

    def insert_db_query(self):
        # insert query and answer
        text = self.get_query_text()
        result_links = self.web_controller.get_links()
        if self.grader_id is None or self.project_id is None:
            self.grader_id = self.web_controller.get_grader_id()
            self.project_id = self.web_controller.get_project_id()
        query_id = self.db_controller.query_insert(self.project_id, text, result_links)
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
                elif (a == 'e'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
                elif (a == 'g'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
                elif (a == 'f'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
                elif (a == 'b'):
                    self.web_controller.click_by_id(
                        ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
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
            self.web_controller.click_next_btn()

        elif (self.project_type == "saf"):
            num = 1
            if (ans == 'i'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
            elif (ans == 'l'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
            elif (ans == 'x'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
            elif (ans == 'e'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
            elif (ans == 'g'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
            elif (ans == 'f'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
            elif (ans == 'b'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
            else:
                print("--------Not correct ans detected.--------")
                return False
            self.web_controller.click_next_btn()

        else:
            print("Project type not setup correctly.")

    def execute(self, ans):
        self.current_url = self.web_controller.get_motherTag_url()
        self.new_query = False # set to default false
        base_command = base_code_check(self.web_controller, ans, max_web_search_links=3)
        if (base_command):
            return False
        elif (not base_command):

            # insert query and grader info into database
            answer_id = self.insert_db_query()

            # execute the command
            self.grading(ans)

            # update ans into db
            self.update_db_ans(answer_id, ans)

            # increase the query done if it is new query
            if (self.current_url != self.previous_url):
                self.query_done = self.query_done + 1
                self.previous_url = self.current_url
                self.new_query = True
            return True


class saf_project:
    def __init__(self, web_controller, db_controller):
        self.web_controller = web_controller
        self.db_controller = db_controller
        self.previous_url = None
        self.current_url = None
        self.query_done = 1
        self.new_query = True

    def get_query_text(self):
        query_text = None
        js_code = """
            var query_text = document.getElementsByClassName("iframe")[0].getElementsByTagName("iframe").item(0).contentDocument.getElementsByClassName("search-input form-control")[0].getAttribute("value");
            return query_text;
        """
        js_code2 = "document.getElementsByClassName('search-input form-control')[0].getAttribute('value')"
        while (query_text == None):
            try:
                query_text = self.web_controller.browser.execute_script(js_code)
                time.sleep(0.5)
            except:
                continue
        return query_text

    def get_query_url(self):
        js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
        query_web_search_url = self.web_controller.browser.execute_script(js_code)
        return query_web_search_url

    def grading(self, ans):
        self.current_url = self.web_controller.get_motherTag_url()
        self.new_query = False  # set to default false
        base_command = base_code_check(self.web_controller, ans, max_web_search_links=3)
        if (base_command):
            return False
        elif (not base_command):
            num = 1
            if (ans == 'i'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
            elif (ans == 'l'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
            elif (ans == 'x'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
            elif (ans == 'e'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
            elif (ans == 'g'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
            elif (ans == 'f'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
            elif (ans == 'b'):
                self.web_controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
            else:
                print("--------Not correct ans detected.--------")
                return False
            self.web_controller.click_next_btn()

            # increase the query done if it is new query
            if (self.current_url != self.previous_url):
                self.query_done = self.query_done + 1
                self.previous_url = self.current_url
                self.new_query = True
            return True
