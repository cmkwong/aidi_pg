import time
import config
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