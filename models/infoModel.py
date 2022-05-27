from models import gradingModel

# def get_query_text(project_type, tg, web_controller, print_allowed, filter_query=None, time_out=10):
#     query_text, filter_query = filter_query, filter_query
#     if project_type in config.GET_QUERY_TEXT_COMMAND.keys():
#         js_code = config.GET_QUERY_TEXT_COMMAND[project_type]
#     else:
#         print_at("project type in renew function not set yet", tg)
#         return None
#     refer_time = time.time()
#     print_at("Loading...", tg, print_allowed=print_allowed)
#     while (query_text==filter_query):
#         try:
#             if (time.time() - refer_time) > time_out:
#                 print_at("Time Out", tg)
#                 return None
#             query_text = web_controller.browser.execute_script(js_code)
#             time.sleep(0.5)
#         except:
#             continue # continue looping
#     return query_text

# def get_links_and_details(web_controller, project_type, time_out=10):
#     refer_time = time.time()
#     links = []
#     link_details = []
#     while (len(links) == 0):
#         try:
#             if (time.time() - refer_time) > time_out:
#                 return None
#             # get links
#             links = web_controller.get_result_links(project_type)
#             # get links text
#             link_details = web_controller.get_link_details(project_type)
#             time.sleep(0.5)
#         except:
#             continue  # continue looping
#     return links, link_details

def get_project_code(web_controller):
    project_id = web_controller.get_projectId_from_url()
    prj_code = {
        'project_type': None,
        'vague': 0,
        'appropriate_query': 0,
        'max_answer_slots': 3,
        'pattern_one_yes_no': 0,
        }
    # ----------------- check for standard -----------------
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
        for num in range(1, 15):    # max 15 answer slow
            # check if need pattern_one format
            gradingModel.pattern_one('g', num, web_controller)
            prj_code['project_type'] = 'standard' # if pattern_one exist, that is standard
            prj_code['max_answer_slots'] = num
            try:
                web_controller.click_by_id(("result" + str(num + 1) + "_shownno"))
                web_controller.click_by_id(("result" + str(num + 1) + "_shownyes"))
                prj_code['pattern_one_yes_no'] = 1
            except:
                pass
    except:
        pass

    # ----------------- check for sbs -----------------
    # check the url has 'sbs' keyword
    index = project_id.find('sbs')
    if index > 0:
        prj_code['project_type'] = 'sbs'
        prj_code['max_answer_slots'] = 15   # ~ is available for clicking the link

    # ---------------- check for validation spot ----------------
    # check the project id has validation plus spot keyword
    validation_index = project_id.find('validation')
    spot_index = project_id.find('spot')
    saf_index = project_id.find('saf')
    if (validation_index > 0 and spot_index > 0) or (validation_index > 0 and saf_index > 0):
        prj_code['project_type'] = 'valid'
    return prj_code

