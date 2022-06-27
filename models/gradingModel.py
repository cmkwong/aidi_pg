from views.prints import *
from utils import sounds
import time
import numpy as np
import config
import re

def base_code_check(controller, project_type, ans, max_answer_slots, tg=None):
    if (ans == '`'):
        # web_search
        try:
            controller.click_web_search(project_type)
        except:
            print_at(config.MESSAGE_BASE_COMMAND_ERROR.format('`'), tg)
            return True # None is Error
        return True
    elif (ans == '!'):
        # close other tags
        try:
            controller.close_other_tags()
        except:
            print_at(config.MESSAGE_BASE_COMMAND_ERROR.format('!'), tg)
            return True
        return True
    elif (ans == '~'):
        try:
            controller.click_all_results(max_answer_slots, project_type)
        except:
            print_at(config.MESSAGE_BASE_COMMAND_ERROR.format('~'), tg)
            return True
        return True
    elif ans == '[':
        controller.click_previous_btn()
        return True
    else:
        return False # False = continue

def pattern_one(a, num, web_controller, tg=None):
    """
    :param a: ans
    :param num: number of answer slot, sometimes it is empty str
    :param web_controller: object class
    :param tg: object class
    :return: bool
    """
    if web_controller.findElemById('result_validationresult_inappropriate'): # means it is simplest version
        countSlotStr = ''
    else:
        countSlotStr = str(num)
    if (a == 'i'):
        web_controller.click_by_id(
            ("result" + countSlotStr + "_validationresult" + countSlotStr + "_inappropriate"))
    elif (a == 'l'):
        web_controller.click_by_id(
            ("result" + countSlotStr + "_validationresult" + countSlotStr + "_wrong_language"))
    elif (a == 'x'):
        web_controller.click_by_id(
            ("result" + countSlotStr + "_validationresult" + countSlotStr + "_cannot_be_judged"))
    else:
        web_controller.click_by_id(
            ("result" + countSlotStr + "_validationresult" + countSlotStr + "_can_be_judged"))
        if (a == 'e'):
            web_controller.click_by_id(("result" + countSlotStr + "_relevanceexcellent"))
        elif (a == 'g'):
            web_controller.click_by_id(("result" + countSlotStr + "_relevancegood"))
        elif (a == 'f'):
            web_controller.click_by_id(("result" + countSlotStr + "_relevancefair"))
        elif (a == 'b'):
            web_controller.click_by_id(("result" + countSlotStr + "_relevancebad"))
        else:
            print_at(config.MESSAGE_WRONG_ANS, tg)
            return False, countSlotStr
    return True, countSlotStr # if empty means it is only 1 ans slot needed (used in infoModel)

def valid_answer_length(ans, web_controller, max_answer_slots, project_type, tg, print_allowed):
    try:
        links = web_controller.get_result_links(project_type)
    except:
        print_at('Warning: not checking input ans length if valid. Bypassed. ', tg, print_allowed)
        return True
    required_length = min(len(links), max_answer_slots)
    if len(ans) == required_length:
        return True
    else:
        return False

# for sbs project
def _decodeComment(comment, tg):
    results = re.findall(r"-(\d+)", comment)
    for result in results:
        sentId = int(result)
        comment = re.sub(f"-{result}", config.sbsSent[sentId], comment)
    if results: print_at(comment, tg)
    return comment

def grading(ans, web_controller, project_type, tg, auto=False, project_code=None, print_allowed=True):

    if project_type == "standard":

        # check if no project code, return False
        if not project_code:
            print_at(config.MESSAGE_NO_PROJECT_CODE_IN_STANDARD_PROJECT_TYPE, tg)
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
        if not valid_answer_length(ans, web_controller, max_answer_slots, project_type, tg, print_allowed):
            print_at(config.MESSAGE_WRONG_LEN_ANS, tg)
            return False

        # grading answer
        num = 1
        # for spot12, amp ... with yes/no after pattern one
        if project_code['pattern_one_yes_no']:
            for a in ans:
                pattern_ok, countSlotStr = pattern_one(a, num, web_controller, tg)
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
                pattern_ok, countSlotStr = pattern_one(a, num, web_controller, tg)
                if not pattern_ok:
                    print('Pattern one cannot perform')
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
                web_controller.insert_comment(project_type, comment)
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
            print_at(config.MESSAGE_WRONG_ANS, tg)
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
            print_at(config.MESSAGE_WRONG_ANS, tg)
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
                    print_at(config.MESSAGE_WRONG_ANS, tg)
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
        try:
            web_controller.flash_web_search(project_type)
        except:
            print('Cannot flash the web-search')
            pass

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
            print_at(config.MESSAGE_WRONG_ANS, tg)
            return False
        return True

    elif (project_type == 'sbs'):
        # # extract the comment
        command, comment = ans[0], ''
        # is NOT 1-4 or w answer, then do NOT split the ans
        if len(ans) > 1:
            split_list = ans.split(' ', 1)
            if len(split_list) == 1:
                print_at(config.MESSAGE_WRONG_LEN_ANS, tg)
                return False
            command, comment = split_list[0], split_list[1]

        if command == '1':
            web_controller.click_by_id("query_validationno_context")
        elif command == '2':
            web_controller.click_by_id("query_validationno_incomplete")
        elif command == '3':
            web_controller.click_by_id("query_validationno_contradictory")
        elif command == '4':
            web_controller.click_by_id("query_validationno_other")
            # other need comment
            if len(comment) == 0:
                print_at(config.MESSAGE_COMMENTS_NEEDED, tg)
                return False
            # search for keyword command -12
            comment = _decodeComment(comment, tg)
            web_controller.insert_comment(project_type, comment) # insert comment
        # if have sufficient information to judge Siri's responses
        else:
            web_controller.click_by_id("query_validationyes")
            # exact identical results
            if command == 's':
                web_controller.click_by_id("identical_responsesyes")
            # it always need comment at the end
            else:
                web_controller.click_by_id("identical_responsesno")
                js_code = "document.querySelectorAll('li.choice-group')[%s].querySelector('input').click()" # clicking which response better
                # about the same
                if command == 'w':
                    web_controller.browser.execute_script(js_code % 3)
                # they can compare
                else:
                    strength = len(command)
                    if strength <= 3: # when strength larger than 3 is not allowed
                        if command[0] == 'a':
                            web_controller.browser.execute_script(js_code % abs(strength - 3))
                        elif command[0] == 'd':
                            web_controller.browser.execute_script(js_code % (strength + 3))
                        else:
                            print_at(config.MESSAGE_WRONG_ANS, tg)
                            return False
                    else:
                        print_at(config.MESSAGE_WRONG_LEN_ANS, tg)
                        return False
                # insert comment
                if len(comment) == 0:
                    print_at(config.MESSAGE_COMMENTS_NEEDED, tg)
                    return False
                # search for keyword command -12
                comment = _decodeComment(comment, tg)
                web_controller.insert_comment(project_type, comment)
        # flash web search
        web_controller.flash_web_search(project_type)
        return True

    else:
        print_at(config.MESSAGE_NO_PROJECT_TYPE_SET, tg)
        return False

def check_limit_reached(grader):
    # check if the done reached the custom limit
    if (grader.query_done >= grader.done_upper_limit) and (grader.done_upper_limit > 0):
        print_at(config.MESSAGE_LIMIT_REACHED, grader.tg)
        sounds.beep("Times up", grader.tg)
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