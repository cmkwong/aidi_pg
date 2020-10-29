from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
import time
import numpy as np
import re

class Web:
    def __init__(self, init_url):
        self.init_url = init_url
        self.browser = None
        self.original_window = None

    def open_chrome(self, executable_path="../driver/chromedriver"):
        chrome_options = Options()
        chrome_options.add_extension(r'appleconnect.crx')
        self.browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
        self.browser.get(self.init_url)
        # Alert(self.browser).accept()
        # Alert(self.browser).dismiss()

    def open_safari(self, executable_path='/usr/bin/safaridriver'):
        self.browser = webdriver.Safari(executable_path=executable_path)
        self.browser.get(self.init_url)
        # Alert(self.browser).accept()
        # Alert(self.browser).dismiss()

    def open_project_link(self, link):
        self.back_tag_one()
        self.browser.get(link)
        self.init_working_tag()

    def init_working_tag(self):
        self.original_window = self.browser.current_window_handle

    def back_tag_one(self):
        self.browser.switch_to.window(self.original_window)

    def close_other_tags(self):
        # js_code = "window.close();"
        for window_handle in self.browser.window_handles:
            # time_out = time.time()
            if window_handle != self.original_window:
                self.browser.switch_to.window(window_handle)
                # if time.time() - time_out <= 2:
                #     self.browser.execute_script(js_code)
                # if time.time() - time_out > 2:
                self.browser.close()
        self.back_tag_one()

    def click_by_id_until(self, id):
        element = WebDriverWait(self.browser.find_element_by_id(id), 5).until(EC.element_to_be_clickable((By.ID, id)))
        element.click()

    def click_by_id(self, id):
        self.back_tag_one()
        js_code = "window.document.getElementById('" + id + "').click();"
        self.browser.execute_script(js_code)

    def select_query_click(self, query):
        self.back_tag_one()
        js_code = "window.document.querySelector('" + query + "').click();"
        self.browser.execute_script(js_code)

    def click_by_class(self, class_name):
        self.back_tag_one()
        js_code = "window.document.getElementsByClassName('" + class_name + "').click();"
        self.browser.execute_script(js_code)

    def click_web_search(self):
        self.back_tag_one()
        js_code = "window.document.getElementsByClassName('clicked validates-clicked')[0].click();"
        self.browser.execute_script(js_code)

    def click_next_btn(self):
        self.back_tag_one()
        js_code = "window.document.getElementById('grading-nav-next-shortcut').click();"
        self.browser.execute_script(js_code)

    def click_selector(self, selector_string):
        self.back_tag_one()
        js_code = "window.document.querySelector('" + selector_string + "').click();"
        self.browser.execute_script(js_code)

    def click_start_project(self, project_index):
        check_txt = """
            var start_txt = document.querySelector("#start").innerText;
            return start_txt
        """
        start_txt = None
        refer_time = time.time()
        while not start_txt:
            try:
                if (time.time() - refer_time) > 10:
                    return False
                start_txt = self.browser.execute_script(check_txt)
                time.sleep(0.5)
            except:
                continue # continue looping
        js_code = ''
        raw_string = """
                    document.querySelector('.selection').querySelector('.menu').getElementsByTagName('div')[%s].click();
                    document.querySelector("#start").click();
                """
        if config.projects_info[project_index]["location"] == "zh_HK":
            js_code = raw_string % 1
        elif config.projects_info[project_index]["location"] == "en_US":
            js_code = raw_string % 0
        self.browser.execute_script(js_code)

    def get_web_search_link(self):
        js_code = """
                    var link = document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href');
                    return link
        """
        link = self.browser.execute_script(js_code)
        return link

    def get_links(self):
        self.back_tag_one()
        # get num of result-set
        js_code = """
                    var num = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('result-set').length;
                    return num;
                """
        num_sets = self.browser.execute_script(js_code)
        # get num of links in each result-set
        num_links = []
        for num_set in np.arange(num_sets):
            raw_string = """
                var num = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('result-set')[%s].getElementsByTagName('a').length;
                return num;
            """
            js_code = raw_string % (num_set)
            num_links.append(self.browser.execute_script(js_code))
        links = []
        for i in np.arange(num_sets):
            for n in np.arange(num_links[i]):
                raw_string = """
                    var link = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('result-set')[%s].getElementsByTagName('a')[%s].getAttribute('href');
                    return link;
                """
                js_code = raw_string % (i, n)
                links.append(self.browser.execute_script(js_code))
        return links

    def get_link_details(self):
        self.back_tag_one()
        # get num of result-set
        js_code = """
                    var num = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('result-set').length;
                    return num;
                """
        num_sets = self.browser.execute_script(js_code)
        # get num of links in each result-set
        num_links = []
        for num_set in np.arange(num_sets):
            raw_string = """
                var num = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('result-set')[%s].getElementsByTagName('a').length;
                return num;
            """
            js_code = raw_string % (num_set)
            num_links.append(self.browser.execute_script(js_code))
        link_details = []
        for i in np.arange(num_sets):
            for n in np.arange(num_links[i]):
                raw_string = """
                    var html_code = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('result-set')[%s].getElementsByTagName('a')[%s].text;
                    return html_code;
                """
                js_code = raw_string % (i, n)
                link_details.append(self.browser.execute_script(js_code))
        return link_details

    def get_motherTag_url(self):
        self.back_tag_one()
        js_code = """
            var link = window.location["href"];
            return link;
        """
        return self.browser.execute_script(js_code)

    def get_html(self):
        self.back_tag_one()
        html = self.browser.page_source
        time.sleep(1)
        return html

    def get_project_id_from_url(self):
        project_id = None
        project_link = self.get_motherTag_url()
        regex = re.compile(r"/project/\S+?/")
        matches = regex.finditer(project_link)
        for match in matches:
            project_id = project_link[match.span()[0]+9:match.span()[1]-1]
        return project_id

    def get_grader_id(self):
        js_code = """
            var usr_name = document.querySelector("#ccmenu2-item0").innerText;
            return usr_name;
        """
        usr_name = self.browser.execute_script(js_code)
        usr_name = usr_name.replace('\n', '')
        usr_name = usr_name.replace(' ', '')
        for info in config.graders_info:
            if usr_name == info["name"]:
                return info["_id"]
        return None

    def open_links_new_tags(self, links, max_tags):
        self.back_tag_one()
        for i, link in enumerate(links):
            try:
                self.browser.execute_script("window.open('%s');" % link)
            except:
                print("A result link cannot open: \n", link)
            if (i+1) == max_tags:
                self.back_tag_one()
                break
        self.back_tag_one()

    def click_tokens_btn(self):
        js_code = """
            var length = document.querySelectorAll("#labeled-token").length;
            for (var i=0; i<length; i++) {
                document.querySelector(".ui.compact.basic.button").click();
            }
        """
        self.browser.execute_script(js_code)

    def quite_driver(self):
        self.browser.quit()

