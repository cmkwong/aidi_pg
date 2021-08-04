from views.prints import *
from utils import sounds
import time
import numpy as np

def pattern_one(a, num, web_controller, tg=None):
    if (a == 'i'):
        web_controller.click_by_id(
            ("result" + str(num) + "_validationresult" + str(num) + "_inappropriate"))
    elif (a == 'l'):
        web_controller.click_by_id(
            ("result" + str(num) + "_validationresult" + str(num) + "_wrong_language"))
    elif (a == 'x'):
        web_controller.click_by_id(
            ("result" + str(num) + "_validationresult" + str(num) + "_cannot_be_judged"))
    else:
        web_controller.click_by_id(
            ("result" + str(num) + "_validationresult" + str(num) + "_can_be_judged"))
        if (a == 'e'):
            web_controller.click_by_id(("result" + str(num) + "_relevanceexcellent"))
        elif (a == 'g'):
            web_controller.click_by_id(("result" + str(num) + "_relevancegood"))
        elif (a == 'f'):
            web_controller.click_by_id(("result" + str(num) + "_relevancefair"))
        elif (a == 'b'):
            web_controller.click_by_id(("result" + str(num) + "_relevancebad"))
        else:
            print_at("--------Not correct ans detected.--------", tg)
            return False
    return True

def valid_answer_length(ans, web_controller, max_answer_slots):
    links = web_controller.get_result_links()
    required_length = min(len(links), max_answer_slots)
    if len(ans) == required_length:
        return True
    else:
        return False

def grading(ans, web_controller, project_type, tg, auto=False, project_code=None):

    if project_type == "standard":

        # check if no project code, return False
        if not project_code:
            print_at("No project code in standard project type.", tg)
            return False
        max_answer_slots = project_code["max_answer_slots"] # assign as local variable

        # if vague of query
        if project_code['vague']:
            if ans[0] == 'v':
                # press vague
                web_controller.click_by_id("query_vagueyes_vague")
                return True
            else:
                web_controller.click_by_id("query_vagueno")

        # if appropriate of query
        if project_code['appropriate_query']:
            if ans[0] == 'n':
                # press query inappropriate
                web_controller.click_by_id("query_appropriatefalse")
                ans = ans[1:]
            else:
                web_controller.click_by_id("query_appropriatetrue")

        # checking wrong length
        if not valid_answer_length(ans, web_controller, max_answer_slots):
            print_at("Wrong length of answer.", tg)
            return False

        # grading answer
        num = 1
        # for spot12, amp ... with yes/no after pattern one
        if project_code['pattern_one_yes_no']:
            for a in ans:
                pattern_ok = pattern_one(a, num, web_controller, tg)
                if not pattern_ok:
                    return False
                if len(ans) > num:
                    web_controller.click_by_id(("result" + str(num + 1) + "_shownyes"))
                elif num != max_answer_slots:
                    web_controller.click_by_id(("result" + str(num + 1) + "_shownno"))
                num = num + 1
        # for spot12, amp, eval3 ...
        else:
            for a in ans:
                pattern_ok = pattern_one(a, num, web_controller, tg)
                if not pattern_ok:
                    return False
                num = num + 1
            # the rest ans by 10 is no results
            no_results_length = max_answer_slots - len(ans)
            for i in range(no_results_length):
                web_controller.click_by_id("result" + str(num + i) + "_validationno_result" + str(num + i))
        return True

    elif (project_type == "token"):
        if (ans[0:3] == '-n-'):
            # press skip
            js_code = """
                document.getElementById('gradingStateSkip - Poor quality / Ambiguous').click();
            """
            web_controller.browser.execute_script(js_code)
            # press token looping
            web_controller.click_tokens_btn()
        elif (ans[0:3] == '-k-'):
            js_code = """
                document.getElementById("gradingStatePossible to grade").click();
            """
            web_controller.browser.execute_script(js_code)

            # press token looping
            web_controller.click_tokens_btn()
        return True

    elif (project_type == "classify"):
        if "-m" in ans:
            comment = ans[ans.find('-m') + 3:]
            comment = comment.replace("\'", '')
            comment = comment.replace("\"", '')
            if auto == False:
                web_controller.browser.execute_script("document.querySelector('textarea').value = '%s';" % comment)
            ans = ans[:ans.find('-m')].replace(' ', '')
        # topic
        if ans[0] is '1':
            web_controller.select_query_click('#query_topicarts_and_entertainment')
        elif ans[0] is '2':
            web_controller.select_query_click('#query_topicfood_and_drink')
        elif ans[0] is '3':
            web_controller.select_query_click('#query_topicsports')
        elif ans[0] is '4':
            web_controller.select_query_click('#query_topichealth_fitness_medicine_and_science')
        elif ans[0] is '5':
            web_controller.select_query_click('#query_topicgeneral_retailers_and_marketplaces')
        elif ans[0] is '6':
            web_controller.select_query_click('#query_topicbusiness_industry_economics_and_finance')
        elif ans[0] is '7':
            web_controller.select_query_click(
                '#query_topiccomputing_technology_telecommunication_and_internet_use')
        elif ans[0] is '8':
            web_controller.select_query_click('#query_topiclife')
        elif ans[0] is '9':
            web_controller.select_query_click('#query_topicplaces_travel_cars_and_transportation')
        elif ans[0] is 'a':
            web_controller.select_query_click('#query_topicsociety')
        elif ans[0] is 'b':
            web_controller.select_query_click('#query_topicother_ambiguous_or_unknown')
        else:
            print_at("--------Not correct ans detected.--------", tg)
            return False
        # goal
        if ans[1] is '1':
            web_controller.select_query_click('#query_goallearn_about')
        elif ans[1] is '2':
            web_controller.select_query_click('#query_goallearn_answer')
        elif ans[1] is '3':
            web_controller.select_query_click('#query_goaleshop')
        elif ans[1] is '4':
            web_controller.select_query_click('#query_goallocate')
        elif ans[1] is '5':
            web_controller.select_query_click('#query_goalbe_entertained')
        elif ans[1] is '6':
            web_controller.select_query_click('#query_goallaunch_download')
        elif ans[1] is '7':
            web_controller.select_query_click('#query_goalfind_online_service')
        elif ans[1] is '8':
            web_controller.select_query_click('#query_goalnavigate')
        elif ans[1] is '9':
            web_controller.select_query_click('#query_goalunknown_other')
        else:
            print_at("--------Not correct ans detected.--------", tg)
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
                web_controller.browser.execute_script(js_code)
                time.sleep(0.1)
            str_ans = "abcdefghijklmnopqrstu"
            for c in ans[2:]:
                pos = str_ans.find(c)
                if pos == -1:
                    print_at("--------Not correct ans detected.--------", tg)
                    return False
                time.sleep(0.1)
                web_controller.browser.execute_script(
                    "document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].click();")
                time.sleep(0.1)
                web_controller.browser.execute_script(
                    "document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].checked = true;")
        return True

    elif (project_type == "valid"):

        # flash web search
        web_controller.flash_web_search()

        if ans == 'v':
            web_controller.click_by_id("query_validationquery_vague")
        elif ans == 'i':
            web_controller.click_by_id("query_validationquery_inappropriate")
        elif ans == 'l':
            web_controller.click_by_id("query_validationquery_wrong_language")
        elif ans == 'n':
            web_controller.click_by_id("query_validationvalid")
        elif ans[0] == '@':
            ans = ans[1:]
            web_controller.click_by_id("query_validationother")
            web_controller.textarea_words("#text-widget-wrapper textarea", ans)
        else:
            print_at("--------Not correct ans detected.--------", tg)
            return False
        return True

    else:
        print_at("Project type not setup correctly.", tg)
        return False

def grading_2(ans, web_controller, project_type, max_answer_slots, tg, auto=False):
    if (project_type == "spot12"):
        if not valid_answer_length(ans, web_controller, max_answer_slots):
            print_at("Wrong length of answer.", tg)
            return False
        num = 1
        for a in ans:
            pattern_ok = pattern_one(a, num, web_controller, tg)
            if not pattern_ok:
                return False
            num = num + 1
        if (len(ans) == 1):
            web_controller.click_by_id("result2_validationno_result2")
            web_controller.click_by_id("result3_validationno_result3")
        elif (len(ans) == 2):
            web_controller.click_by_id("result3_validationno_result3")
        return True

    elif (project_type == 'spot12t'):
        if not valid_answer_length(ans, web_controller, max_answer_slots):
            print_at("Wrong length of answer.", tg)
            return False
        num = 1
        for a in ans:
            pattern_ok = pattern_one(a, num, web_controller, tg)
            if not pattern_ok:
                return False
            if len(ans) > num:
                web_controller.click_by_id(("result" + str(num + 1) + "_shownyes"))
            elif num != max_answer_slots:
                web_controller.click_by_id(("result" + str(num + 1) + "_shownno"))
            num = num + 1
        return True

    elif (project_type == "amp") or (project_type == "maps") or project_type == 'saf2':
        if not valid_answer_length(ans, web_controller, max_answer_slots):
            print_at("Wrong length of answer.", tg)
            return False
        num = 1
        for a in ans:
            pattern_ok = pattern_one(a, num, web_controller, tg)
            if not pattern_ok:
                return False
            num = num + 1
        # the rest ans by 10 is no results
        no_results_length = max_answer_slots - len(ans)
        for i in range(no_results_length):
            command_string = "result" + str(num + i) + "_validationno_result" + str(num + i)
            web_controller.click_by_id(command_string)
        return True

    elif (project_type == "deepscrape"):
        # checking wrong length
        if ans[0] == 'n':
            if not valid_answer_length(ans[1:], web_controller, max_answer_slots) or len(ans) == 1:
                print_at("Wrong length of answer.", tg)
                return False
        else:
            if not valid_answer_length(ans, web_controller, max_answer_slots):
                print_at("Wrong length of answer.", tg)
                return False

        if ans[0] == 'v':
            # press vague
            web_controller.click_by_id("query_vagueyes_vague")
        else:
            web_controller.click_by_id("query_vagueno")
            if ans[0] == 'n':
                # press query inappropriate
                web_controller.click_by_id("query_appropriatefalse")
                ans = ans[1:]
            else:
                web_controller.click_by_id("query_appropriatetrue")
            num = 1
            for a in ans:
                pattern_ok = pattern_one(a, num, web_controller, tg)
                if not pattern_ok:
                    return False
                web_controller.click_by_id(("result" + str(num + 1) + "_shownyes"))
                num = num + 1
            web_controller.click_by_id(("result" + str(num) + "_shownno"))
        return True

    elif (project_type == "saf"):
        # checking wrong length
        if not valid_answer_length(ans, web_controller, max_answer_slots):
            print_at("Wrong length of answer.", tg)
            return False

        num = 1
        pattern_ok = pattern_one(ans, num, web_controller, tg)
        if not pattern_ok:
            return False
        return True

    elif (project_type == "eval3"):
        # checking wrong length
        if ans[0] == 'n':
            if not valid_answer_length(ans[1:], web_controller, max_answer_slots) or len(ans) == 1:
                print_at("Wrong length of answer.", tg)
                return False
        else:
            if not valid_answer_length(ans, web_controller, max_answer_slots):
                print_at("Wrong length of answer.", tg)
                return False

        max_num = 3
        len_ans = len(ans)
        num = 1

        if ans[0] == 'v':
            # press vague
            web_controller.click_by_id("query_vagueyes_vague")
        else:
            web_controller.click_by_id("query_vagueno")
            if ans[0] == 'n':
                # press query inappropriate
                len_ans = len_ans - 1
                web_controller.click_by_id("query_appropriatefalse")
            else:
                web_controller.click_by_id("query_appropriatetrue")
            for a in ans:
                pattern_ok = pattern_one(a, num, web_controller, tg)
                if not pattern_ok:
                    return False
                if num == max_num:
                    continue
                elif num == len_ans:
                    web_controller.click_by_id("result" + str(num + 1) + "_shownno")
                elif num < len_ans:
                    web_controller.click_by_id("result" + str(num + 1) + "_shownyes")
                num = num + 1
        return True

    elif (project_type == "token"):
        if (ans[0:3] == '-n-'):
            # press skip
            js_code = """
                document.getElementById('gradingStateSkip - Poor quality / Ambiguous').click();
            """
            web_controller.browser.execute_script(js_code)
            # press token looping
            web_controller.click_tokens_btn()
        elif (ans[0:3] == '-k-'):
            js_code = """
                document.getElementById("gradingStatePossible to grade").click();
            """
            web_controller.browser.execute_script(js_code)

            # press token looping
            web_controller.click_tokens_btn()
        return True

    elif (project_type == "classify"):
        if "-m" in ans:
            comment = ans[ans.find('-m') + 3:]
            comment = comment.replace("\'", '')
            comment = comment.replace("\"", '')
            if auto == False:
                web_controller.browser.execute_script("document.querySelector('textarea').value = '%s';" % comment)
            ans = ans[:ans.find('-m')].replace(' ', '')
        # topic
        if ans[0] is '1':
            web_controller.select_query_click('#query_topicarts_and_entertainment')
        elif ans[0] is '2':
            web_controller.select_query_click('#query_topicfood_and_drink')
        elif ans[0] is '3':
            web_controller.select_query_click('#query_topicsports')
        elif ans[0] is '4':
            web_controller.select_query_click('#query_topichealth_fitness_medicine_and_science')
        elif ans[0] is '5':
            web_controller.select_query_click('#query_topicgeneral_retailers_and_marketplaces')
        elif ans[0] is '6':
            web_controller.select_query_click('#query_topicbusiness_industry_economics_and_finance')
        elif ans[0] is '7':
            web_controller.select_query_click(
                '#query_topiccomputing_technology_telecommunication_and_internet_use')
        elif ans[0] is '8':
            web_controller.select_query_click('#query_topiclife')
        elif ans[0] is '9':
            web_controller.select_query_click('#query_topicplaces_travel_cars_and_transportation')
        elif ans[0] is 'a':
            web_controller.select_query_click('#query_topicsociety')
        elif ans[0] is 'b':
            web_controller.select_query_click('#query_topicother_ambiguous_or_unknown')
        else:
            print_at("--------Not correct ans detected.--------", tg)
            return False
        # goal
        if ans[1] is '1':
            web_controller.select_query_click('#query_goallearn_about')
        elif ans[1] is '2':
            web_controller.select_query_click('#query_goallearn_answer')
        elif ans[1] is '3':
            web_controller.select_query_click('#query_goaleshop')
        elif ans[1] is '4':
            web_controller.select_query_click('#query_goallocate')
        elif ans[1] is '5':
            web_controller.select_query_click('#query_goalbe_entertained')
        elif ans[1] is '6':
            web_controller.select_query_click('#query_goallaunch_download')
        elif ans[1] is '7':
            web_controller.select_query_click('#query_goalfind_online_service')
        elif ans[1] is '8':
            web_controller.select_query_click('#query_goalnavigate')
        elif ans[1] is '9':
            web_controller.select_query_click('#query_goalunknown_other')
        else:
            print_at("--------Not correct ans detected.--------", tg)
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
                web_controller.browser.execute_script(js_code)
                time.sleep(0.1)
            str_ans = "abcdefghijklmnopqrstu"
            for c in ans[2:]:
                pos = str_ans.find(c)
                if pos == -1:
                    print_at("--------Not correct ans detected.--------", tg)
                    return False
                time.sleep(0.1)
                web_controller.browser.execute_script(
                    "document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].click();")
                time.sleep(0.1)
                web_controller.browser.execute_script(
                    "document.querySelectorAll('.ui.checkbox.checkbox-row input')[" + str(pos) + "].checked = true;")
        return True

    elif (project_type == "valid"):

        # flash web search
        web_controller.flash_web_search()

        if ans == 'v':
            web_controller.click_by_id("query_validationquery_vague")
        elif ans == 'i':
            web_controller.click_by_id("query_validationquery_inappropriate")
        elif ans == 'l':
            web_controller.click_by_id("query_validationquery_wrong_language")
        elif ans == 'n':
            web_controller.click_by_id("query_validationvalid")
        elif ans[0] == '@':
            ans = ans[1:]
            web_controller.click_by_id("query_validationother")
            web_controller.textarea_words("#text-widget-wrapper textarea", ans)
        else:
            print_at("--------Not correct ans detected.--------", tg)
            return False
        return True

    else:
        print_at("Project type not setup correctly.", tg)
        return False

def check_limit_reached(grader):
    # check if the done reached the custom limit
    if (grader.query_done >= grader.done_upper_limit) and (grader.done_upper_limit > 0):
        print_at("Limit Reached.\n", grader.tg)
        sounds.beep("Times up", grader.tg)
        done_upper_limit = -1 # reset
        return True
    return False

def find_time_delay_level(find_time_delay):
    if find_time_delay > 200:
        return 20
    elif find_time_delay <= 200 and find_time_delay > 100:
        return 15
    elif find_time_delay <= 100 and find_time_delay > 60:
        return 10
    elif find_time_delay <= 60 and find_time_delay > 20:
        return 5
    elif find_time_delay <= 20 and find_time_delay > 1:
        return 2