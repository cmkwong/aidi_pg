import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils import osSystem
import config
import time
import re

class Web:
    def __init__(self, init_url):
        self.init_url = init_url
        self.browser = None
        self.original_window = None
        self.currentLink = None

    def open_chrome(self, executable_path="../driver/chromedriver"):
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']) # disappear the warning
        chrome_options.add_extension(r'./src/appleconnect.crx')
        chrome_options.add_extension(r'./src/working_extension.crx')
        self.update_driver(executable_path)
        self.browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
        self.browser.get(self.init_url)

    def update_driver(self, executable_path):
        print("Updating Chrome driver ... ")
        osSystem.download_driver(executable_path)

    def open_myLink(self, link):
        self.back_tag_one()
        self.browser.get(link)
        self.init_working_tag()

    def init_working_tag(self):
        self.original_window = self.browser.current_window_handle

    def back_tag_one(self):
        self.browser.switch_to.window(self.original_window)

    def close_other_tags(self):
        try:
            for window_handle in self.browser.window_handles:
                if window_handle != self.original_window:
                    self.browser.switch_to.window(window_handle)
                    self.browser.close()
                    self.back_tag_one()
        except Exception as e:
            print(e)
            print(config.MESSAGE_CLOSE_TAGS_ERROR)
            self.browser.quit()
            self.reopen_current_browser()
            return False
        return True

    def reopen_current_browser(self):
        self.open_chrome()
        self.init_working_tag()
        self.open_myLink(self.currentLink)

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

    def click_all_results(self, max_answer_slots, project_type):
        # click results
        try:
            self.browser.execute_script(config.CLICK_ALL_RESULTS_COMMAND[project_type] % max_answer_slots)
            # open web search
            self.click_web_search(project_type)
            self.back_tag_one()
        except:
            print("error of click all results")

    def click_web_search(self, project_type):
        self.back_tag_one()
        js_code = config.CLICK_WEB_SEARCH_COMMAND[project_type]
        self.browser.execute_script(js_code)

    def click_next_btn(self, project_type, auto=False):
        self.back_tag_one()
        js_code = config.CLICK_NEXT_BTN_COMMAND[project_type] % (int(auto))
        self.browser.execute_script(js_code)

    def click_previous_btn(self):
        self.back_tag_one()
        js_code = "window.document.getElementById('grading-nav-previous-shortcut').click();"
        self.browser.execute_script(js_code)

    def click_selector(self, selector_string):
        self.back_tag_one()
        js_code = "window.document.querySelector('" + selector_string + "').click();"
        self.browser.execute_script(js_code)

    def click_start_project(self, project_index, timeout=5):
        js_code = config.CLICK_START_PRJ_COMMAND % (timeout * 1000, config.projects_info[project_index]["location"])
        self.browser.execute_script(js_code)

    def flash_web_search(self, project_type):
        # open web search
        self.click_web_search(project_type)
        self.close_other_tags()

    def flash_all_results(self, max_answer_slots, project_type):
        self.click_all_results(max_answer_slots, project_type)
        closeTagsOk = self.close_other_tags()
        if not closeTagsOk:
            return False
        return True

    def findElemById(self, elemId):
        """
        Find the element existed or not
        :return:
        """
        js_code = f"return document.getElementById('{elemId}')"
        if self.browser.execute_script(js_code):
            return True
        return False

    def get_web_search_link(self, project_type):
        js_code = config.GET_WEB_SEARCH_LINK_COMMAND[project_type]
        link = self.browser.execute_script(js_code)
        return link

    def get_result_links(self, project_type):
        self.back_tag_one()
        js_code = config.GET_RESULT_LINKS_COMMAND[project_type]
        links = self.browser.execute_script(js_code)
        return links

    def get_link_details(self, project_type):
        self.back_tag_one()
        js_code = config.GET_RESULT_LINK_DETAILS_COMMAND[project_type]
        link_details = self.browser.execute_script(js_code)
        return link_details

    def get_search_date(self, project_type):
        js_code = config.GET_SEARCH_DATE_COMMAND[project_type]
        search_date = self.browser.execute_script(js_code)
        return search_date

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

    def get_projectId_from_url(self):
        project_link = self.get_motherTag_url()
        project_id = None

        # project_id and project locale
        result = re.search(r"/project/(\S+?)/", project_link)
        if result:
            project_id = result.group(1)
        return project_id

    def get_queryCode_from_url(self):
        project_link = self.get_motherTag_url()
        query_code = None

        # query code
        result = re.search(r"/s/(\S+?)/", project_link)
        if result:
            query_code = result.group(1)
        return query_code

    def get_projectId_locale_from_url(self, url=None):
        if not url:
            url = self.currentLink
        project_id, project_locale = None, None

        # project_id and project locale
        result = re.search(r"/project/(\S+?)/grading/(\S+?)/", url)
        if result:
            project_id, project_locale = result.group(1), result.group(2)
        return project_id, project_locale

    def get_grader_name_from_cc(self):
        js_code = """
                    var grader_name = document.querySelector("#dd-menu__shared_component__-1-item0").innerText.trim().replace(/ /g, '');
                    return grader_name;
                """
        grader_name = self.browser.execute_script(js_code)
        return grader_name

    def get_grader_id_from_cc(self):
        grader_name = self.get_grader_name_from_cc()
        for info in config.graders_info:
            if grader_name == info["name"]:
                return info["grader_id"]
        return None

    def get_query_answer(self, project_type):
        data = None
        try: # prevent getting error if it is not project expected
            data = self.browser.execute_script(config.GET_QUERY_ANSWER_COMMAND[project_type])
        except:
            pass
        return data

    def get_report_data(self):
        click_pj_groups_icon = """
            document.querySelectorAll('.icon.sf-symbol-chevron-down')[0].click();
        """
        click_pj_icon = """
            document.querySelectorAll('.icon.sf-symbol-chevron-down')[1].click();
        """
        get_pj_name = """
            return document.querySelector('.highcharts-xaxis-labels').textContent;
        """
        click_locate_icon = """
            document.querySelectorAll('.icon.sf-symbol-chevron-down')[2].click();
        """
        get_locate = """
            return document.getElementById('locale-selection').value.trim();
        """
        get_done = """
            return parseInt(document.querySelector(".highcharts-data-labels").querySelectorAll('tspan.highcharts-text-outline')[0].textContent.replace(',','').trim());
        """
        get_working_hrs = """
            return parseFloat(document.querySelector('.highcharts-subtitle').querySelectorAll('tspan')[7].textContent.trim());
        """
        get_breaking_hrs = """
            return parseFloat(document.querySelector('.highcharts-subtitle').querySelectorAll('tspan')[9].textContent.trim());
        """

        def _get_list_len(click_icon):
            len_command = """
                return document.querySelector('.listbox').querySelectorAll('li').length;
            """
            self.browser.execute_script(click_icon)
            list_length = int(self.browser.execute_script(len_command))
            self.browser.execute_script(click_icon)
            return list_length

        def _click_list_item(click_icon, num):
            click_command = """
                document.querySelector('.listbox').querySelectorAll('li')[%s].click();
            """
            self.browser.execute_script(click_icon)
            time.sleep(0.3)
            self.browser.execute_script(click_command % num)
            time.sleep(0.3)

        report = {}
        pj_groups_length = _get_list_len(click_pj_groups_icon)
        if pj_groups_length == 0:
            return False

        # project groups
        for i in range(pj_groups_length):
            _click_list_item(click_pj_groups_icon, i)
            pjs_len = _get_list_len(click_pj_icon)

            # projects
            for j in range(1, pjs_len):
                _click_list_item(click_pj_icon, j)
                locate_len = _get_list_len(click_locate_icon)

                # locale
                for k in range(1, locate_len):
                    _click_list_item(click_locate_icon, k)

                    # get data from a project
                    locate = self.browser.execute_script(get_locate)
                    pj_name = self.browser.execute_script(get_pj_name)
                    done = self.browser.execute_script(get_done)
                    working_hrs = self.browser.execute_script(get_working_hrs)
                    breaking_hrs = self.browser.execute_script(get_breaking_hrs)
                    report[(pj_name, locate)] = [done, working_hrs, breaking_hrs]
        return report

    def findProjectLinkByName(self, prjName, timeout):
        searchBarReady = self.browser.execute_script(config.CHECK_SEARCH_BAR_READY % timeout)   # check search bar ready or not
        if searchBarReady:
            self.browser.execute_script(config.ENTER_PRJ_NAME % prjName)    # enter project name
            link = self.browser.execute_script(config.FIND_PRJLINK_BY_NAME % (prjName, timeout))    # get the project link once search
            return link
        return False

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

    def zoom_body_style(self, percentage):
        js_code = """
            document.body.style.zoom=%s;
        """
        js_code = js_code % percentage
        self.browser.execute_script(js_code)

    def zoom_browser(self, percent):
        try:
            original_url = self.get_motherTag_url()
            self.browser.get('chrome://settings/')
            self.browser.execute_script('chrome.settingsPrivate.setDefaultZoom({});'.format(percent))
            self.open_myLink(original_url)
            return True
        except:
            print("cannot zoom browser")
            return False

    def scrollIntoView(self, project_type):
        time.sleep(0.5)
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'utterance'))
            WebDriverWait(self.browser, 2).until(element_present) # in second
        except:
            print('timeout for scroll')
        self.browser.execute_script(config.SCROLL_TO_VIEW_COMMAND[project_type])

    def insert_comment(self, project_type, text):
        js_code = config.INSERT_COMMENT_COMMAND[project_type]
        self.browser.execute_script(js_code % text)

    def check_current_report(self, month, date, time_out=10):
        """
        :param month: String
        :param date: Int
        """
        month_ok = False
        cc_month = None
        check_cur_month_code = """
            var month = document.querySelector('.cur_month').innerText.trim();
            return month;
            """
        click_next_month_btn_code = """
            document.querySelector('.flatpickr-next-month').click()
            """
        click_date_code = """
            document.querySelector('.flatpickr-wrapper').querySelectorAll('.flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)')[%s].click();
            document.querySelector('.flatpickr-wrapper').querySelectorAll('.flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)')[%s].click();
        """
        # check if it is current month in first time
        refer_time = time.time()
        while not cc_month:
            try:
                if (time.time() - refer_time) > time_out:
                    print("Time Out")
                    return False
                cc_month = self.browser.execute_script(check_cur_month_code)
            except:
                continue
        if month == cc_month:
            month_ok = True
        # loop for current month
        while not month_ok:
            self.browser.execute_script(click_next_month_btn_code)
            if month == self.browser.execute_script(check_cur_month_code):
                month_ok = True
        # click the current date
        click_date_code = click_date_code % (date - 1, date - 1)
        self.browser.execute_script(click_date_code)
        self.back_tag_one()
        return True

    def check_project_finished_popUp(self):
        popUp_js_code = """
            try {
              const message = document.querySelector("#swal2-content").innerText;
              const pos = message.search('_');
              const locale = message.substring(pos-2,pos+3);
              if (locale) {
                return locale;
              }
            } catch (err) {
                return false;
            }
        """
        # pop_up message
        return self.browser.execute_script(popUp_js_code)

    def textarea_words(self, path, text):
        textarea = self.browser.find_element_by_css_selector(path)
        #textarea.click()
        textarea.clear()
        textarea.send_keys(text)
        return True

    def get_cheat_sheet_querys(self):
        query_codes = self.browser.execute_script(config.GET_CHEAT_QUERY_CODE)
        query_texts = self.browser.execute_script(config.GET_CHEAT_QUERY_TEXT)
        project_id = self.browser.execute_script(config.GET_CHEAT_PROJECT_ID)
        for query_code, query_text in zip(query_codes, query_texts):
            config.cheat_sheet.add((query_text, project_id, query_code))
        print("Project id: {} \nGot: {} querys \nLocal: {}".format(project_id, len(query_codes), len(config.cheat_sheet)))

    def quite_driver(self):
        self.browser.quit()