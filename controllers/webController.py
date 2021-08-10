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
        for window_handle in self.browser.window_handles:
            if window_handle != self.original_window:
                self.browser.switch_to.window(window_handle)
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

    def click_all_links(self, max_answer_slots):
        # open three results
        links = self.get_result_links()
        self.open_links_new_tags(links, max_answer_slots)
        # open web search
        self.click_web_search()

    def click_web_search(self):
        self.back_tag_one()
        js_code = "window.document.getElementsByClassName('clicked validates-clicked')[0].click();"
        self.browser.execute_script(js_code)

    def click_next_btn(self):
        self.back_tag_one()
        js_code = "window.document.getElementById('grading-nav-next-shortcut').click();"
        self.browser.execute_script(js_code)

    def click_previous_btn(self):
        self.back_tag_one()
        js_code = "window.document.getElementById('grading-nav-previous-shortcut').click();"
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
        if config.projects_info[project_index]["location"] == "en_US":
            js_code = raw_string % 0
        elif config.projects_info[project_index]["location"] == "zh_HK":
            js_code = raw_string % 1
        elif config.projects_info[project_index]["location"] == "zh_TW":
            js_code = raw_string % 2
        self.browser.execute_script(js_code)

    def flash_web_search(self):
        # open web search
        self.click_web_search()
        self.close_other_tags()

    def flash_all_tags(self, max_answer_slots):
        # get links
        try:
            links = self.get_result_links()
        except:
            links = []
            return False
        # open the links one-by-one
        links = links[:max_answer_slots]
        for link in links:
            try:
                self.browser.execute_script("window.open('%s');" % link)
                self.close_other_tags()
            except:
                print("A result link cannot open: \n", link)
        # open web search
        self.flash_web_search()
        return True

    def get_web_search_link(self):
        js_code = """
                    var link = document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href');
                    return link
        """
        link = self.browser.execute_script(js_code)
        return link

    def get_link_details__discard(self):
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

    def get_result_links(self):
        self.back_tag_one()
        js_code = """
            list = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.querySelectorAll("div.parsec-result");
            filter_list = [];
            for (let i=0; i<list.length; i++) {
                if (getComputedStyle(list[i],'::after').content === "counter(section)") {
                    filter_list.push(list[i].querySelector('a').getAttribute('href'));
                }
            }
            return filter_list;
        """
        links = self.browser.execute_script(js_code)
        return links

    def get_link_details(self):
        self.back_tag_one()
        js_code = """
                    list = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.querySelectorAll("div.parsec-result");
                    filter_list = [];
                    for (let i=0; i<list.length; i++) {
                        let title = '';
                        if (list[i].querySelector('.title')) { 
                            title = list[i].querySelector('.title').textContent.trim();
                        } else {
                            title = "Empty Title";
                        };
                        let description = '';
                        let description_list = list[i].querySelectorAll('.description');
                        if (description_list.length !== 0) {
                            for (let k=0; k < description_list.length; k++) {
                                description += description_list[k].textContent.trim() + '\\n';
                            }
                        } else {
                            description = "Empty Description";
                        };
                        filter_list.push(title + '\\n' + description);
                    }
                    return filter_list;
                """
        link_details = self.browser.execute_script(js_code)
        return link_details

    def get_search_date(self):
        js_code = """
            var text = document.querySelector(".message.blue").querySelector("p").firstChild.textContent;
            return text;
        """
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

    def get_project_id_locale_from_url(self):
        project_link = self.get_motherTag_url()
        project_id, project_locale = '', ''

        # project_id
        regex = re.compile(r"/project/\S+?/")
        matches = regex.finditer(project_link)
        for match in matches:
            project_id = project_link[match.span()[0] + 9:match.span()[1] - 1]

        # project locale
        regex = re.compile(r"/grading/\S+?/")
        matches = regex.finditer(project_link)
        for match in matches:
            project_locale = project_link[match.span()[0] + 9:match.span()[1] - 1]
        return project_id, project_locale

    def get_grader_id(self):
        js_code = """
            var usr_name = document.querySelector("#dd-menu__shared_component__-1-item0").innerText;
            return usr_name;
        """
        usr_name = self.browser.execute_script(js_code)
        usr_name = usr_name.replace('\n', '')
        usr_name = usr_name.replace(' ', '')
        for info in config.graders_info:
            if usr_name == info["name"]:
                return info["_id"]
        return None

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

    def get_report_data2(self):
        click_pj_groups_icon = """
            document.querySelectorAll('.icon.sf-symbol-chevron-down')[0].click();
        """
        get_pj_groups_len = """
            return document.querySelector('.listbox').querySelectorAll('li').length;
        """
        click_pj_group = """
            document.querySelector('.listbox').querySelectorAll('li')[%s].click();
        """
        click_pj_icon = """
            document.querySelectorAll('.icon.sf-symbol-chevron-down')[1].click();
        """
        get_pjs_len = """
            return document.querySelector('.listbox').querySelectorAll('li').length;
        """
        click_pj = """
            document.querySelectorAll('.icon.sf-symbol-chevron-down')[1].click();
            document.querySelector('.listbox').querySelectorAll('li')[%s].click();
        """
        get_pj_name = """
            return document.querySelector('.highcharts-xaxis-labels').textContent;
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
        report = {}
        self.browser.execute_script(click_pj_groups_icon)
        pj_groups_length = int(self.browser.execute_script(get_pj_groups_len))
        print("{} project group len".format(pj_groups_length))
        self.browser.execute_script(click_pj_groups_icon)
        if pj_groups_length == 0:
            return False
        for i in range(pj_groups_length):
            self.browser.execute_script(click_pj_groups_icon)
            self.browser.execute_script(click_pj_group % i)
            print("pj_group i={} clicked.".format(i))
            self.browser.execute_script(click_pj_icon)
            pjs_len = int(self.browser.execute_script(get_pjs_len))
            print('{} project len'.format(pjs_len))
            self.browser.execute_script(click_pj_icon)
            for j in range(1, pjs_len):
                self.browser.execute_script(click_pj % j)
                print("pj j={} clicked.".format(j))
                pj_name = self.browser.execute_script(get_pj_name)
                print(pj_name)
                done = self.browser.execute_script(get_done)
                working_hrs = self.browser.execute_script(get_working_hrs)
                breaking_hrs = self.browser.execute_script(get_breaking_hrs)
                report[pj_name] = [done, working_hrs, breaking_hrs]
        return report

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

    def zoom_browser(self, percentage):
        js_code = """
            document.body.style.zoom=%s;
        """
        js_code = js_code % percentage
        self.browser.execute_script(js_code)

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

    # def textarea_words(self, text, tab_times):
    #     keyboard = Controller()
    #     for _ in range(tab_times):
    #         keyboard.press(Key.tab)
    #         keyboard.release(Key.tab)
    #     keyboard.type(text)
    #     return True

    def textarea_words(self, path, text):
        textarea = self.browser.find_element_by_css_selector(path)
        #textarea.click()
        textarea.clear()
        textarea.send_keys(text)
        return True

    def quite_driver(self):
        self.browser.quit()