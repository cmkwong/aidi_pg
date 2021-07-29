import time
import config
from models import gradingModel
from views.prints import *

def get_query_text(project_type, tg, web_controller, print_allowed, filter_query=None, time_out=10):
    query_text, filter_query = filter_query, filter_query
    if project_type in config.GET_QUERY_TEXT_PROJS:
        js_code = """
            var query_text = document.getElementsByClassName("iframe")[0].getElementsByTagName("iframe").item(0).contentDocument.getElementsByClassName("search-input form-control")[0].getAttribute("value");
            return query_text;
        """
    elif project_type == "valid":
        js_code = """
            var query_text = document.querySelector("#widget-container h1").innerText;
            return query_text;
        """
    elif project_type == "token":
        js_code = """
            var query_text = document.querySelector("#input-field").querySelector("input").value;
            return query_text;
        """
    elif project_type == "classify":
        js_code = """
            var query_text = document.querySelector('#display-section').querySelector('h1').textContent;
            return query_text;
        """
    else:
        print_at("project type in renew function not set yet", tg)
        return None
    refer_time = time.time()
    print_at("Loading...", tg, print_allowed=print_allowed)
    while (query_text==filter_query):
        try:
            if (time.time() - refer_time) > time_out:
                print_at("Time Out", tg)
                return None
            query_text = web_controller.browser.execute_script(js_code)
            time.sleep(0.5)
        except:
            continue # continue looping
    return query_text

def get_links_and_details(web_controller, time_out=10):
    refer_time = time.time()
    links = []
    link_details = []
    while (len(links) == 0):
        try:
            if (time.time() - refer_time) > time_out:
                return None
            # get links
            links = web_controller.get_links()
            # get links text
            link_details = web_controller.get_link_details()
            time.sleep(0.5)
        except:
            continue  # continue looping
    return links, link_details

def get_query_url(web_controller):
    js_code = "document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href')"
    query_web_search_url = web_controller.browser.execute_script(js_code)
    return query_web_search_url

def get_project_code(web_controller):
    prj_code = {
        'vague': 0,
        'appropriate_query': 0,
        'max_answer_slots': 0,
        'pattern_one': 0,
        'pattern_one_yes_no': 0,
        'special_type': '',
    }
    # check if need vague
    try:
        web_controller.click_by_id("query_vagueno")
        web_controller.click_by_id("query_vagueyes_vague")
        prj_code['vague'] = 1
    except:
        pass

    # check if need query appropriate
    try:
        web_controller.click_by_id("query_appropriatefalse")
        web_controller.click_by_id("query_appropriatetrue")
        prj_code['appropriate_query'] = 1
    except:
        pass

    # check if it is pattern_one + if yes/no after right after the pattern_one
    try:
        for num in range(1, 15):
            # check if need pattern_one format
            gradingModel.pattern_one('g', num, web_controller)
            prj_code['pattern_one'] = 1
            prj_code['max_answer_slots'] = num
            try:
                web_controller.click_by_id(("result" + str(num + 1) + "_shownno"))
                web_controller.click_by_id(("result" + str(num + 1) + "_shownyes"))
                prj_code['pattern_one_yes_no'] = 1
            except:
                pass
    except:
        pass
    return prj_code