import numpy as np
import time
from bs4 import BeautifulSoup

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

class spot12_project:
    def __init__(self, controller):
        self.controller = controller
        self.previous_url = None
        self.current_url = None
        self.query_done = 0
        self.new_query = True

    def get_query_text(self):
        query_text = None
        js_code = """
            var query_text = document.getElementsByClassName("iframe")[0].getElementsByTagName("iframe").item(0).contentDocument.getElementsByClassName("search-input form-control")[0].getAttribute("value");
            return query_text;
        """
        js_code2 = "document.getElementsByClassName('search-input form-control')[0].getAttribute('value')"
        while (query_text==None):
            try:
                query_text = self.controller.browser.execute_script(js_code)
                time.sleep(0.5)
            except:
                continue
        return query_text

    def get_query_url(self):
        js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
        query_web_search_url = self.controller.browser.execute_script(js_code)
        return query_web_search_url

    def grading(self, ans):
        self.current_url = self.controller.get_motherTag_url()
        self.new_query = False # set to default false
        base_command = base_code_check(self.controller, ans, max_web_search_links=3)
        if (base_command):
            return False
        elif (not base_command):
            num = 1
            for a in ans:
                if (a=='i'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
                elif (a=='l'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
                elif (a=='x'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
                elif(a=='e'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
                elif (a=='g'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.controller.click_by_id(("result" + str(num) + "_relevancegood"))
                elif (a=='f'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.controller.click_by_id(("result" + str(num) + "_relevancefair"))
                elif (a=='b'):
                    self.controller.click_by_id(("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                    self.controller.click_by_id(("result" + str(num) + "_relevancebad"))
                else:
                    print("--------Not correct ans detected.--------")
                    return False
                num = num + 1
            if (len(ans)==1):
                self.controller.click_by_id("result2_validationno_result2")
                self.controller.click_by_id("result3_validationno_result3")
            elif (len(ans)==2):
                self.controller.click_by_id("result3_validationno_result3")
            self.controller.click_next_btn()

            # increase the query done if it is new query
            if (self.current_url != self.previous_url):
                self.query_done = self.query_done + 1
                self.previous_url = self.current_url
                self.new_query = True
            return True


class saf_project:
    def __init__(self, controller):
        self.controller = controller
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
                query_text = self.controller.browser.execute_script(js_code)
                time.sleep(0.5)
            except:
                continue
        return query_text

    def get_query_url(self):
        js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
        query_web_search_url = self.controller.browser.execute_script(js_code)
        return query_web_search_url

    def grading(self, ans):
        self.current_url = self.controller.get_motherTag_url()
        self.new_query = False  # set to default false
        base_command = base_code_check(self.controller, ans, max_web_search_links=3)
        if (base_command):
            return False
        elif (not base_command):
            num = 1
            if (ans == 'i'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
            elif (ans == 'l'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
            elif (ans == 'x'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
            elif (ans == 'e'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
            elif (ans == 'g'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.controller.click_by_id(("result" + str(num) + "_relevancegood"))
            elif (ans == 'f'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.controller.click_by_id(("result" + str(num) + "_relevancefair"))
            elif (ans == 'b'):
                self.controller.click_by_id(
                    ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
                self.controller.click_by_id(("result" + str(num) + "_relevancebad"))
            else:
                print("--------Not correct ans detected.--------")
                return False
            self.controller.click_next_btn()

            # increase the query done if it is new query
            if (self.current_url != self.previous_url):
                self.query_done = self.query_done + 1
                self.previous_url = self.current_url
                self.new_query = True
            return True
