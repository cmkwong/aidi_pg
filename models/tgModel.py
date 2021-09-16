from models import infoModel

# for tg_bot.py used
def send_tg_info(grader, old_query_text=None, time_out=10):

    # get query text (plus condition)
    query_text = infoModel.get_query_text(grader.project_type, grader.tg, grader.web_controller, grader.print_allowed,
                                             filter_query=old_query_text, time_out=time_out)
    if not query_text:
        return False
    try:
        # get search date
        search_date = grader.web_controller.get_search_date(grader.project_type)
        # get web search links
        web_search_link = grader.web_controller.get_web_search_link(grader.project_type)
        # get links and its details
        links, link_details = infoModel.get_links_and_details(grader.web_controller, grader.project_type, time_out=10)
    except:
        return False

    max_index = min(len(links), grader.project_code["max_answer_slots"])
    # query and its introduction
    text = search_date + '\n\n' + query_text + '\n' + \
           "web search link: " + web_search_link + '\n' + \
           "No. of Results: " + str(max_index)
    # link details text and links
    for i in range(max_index):
        text += "\n\n-*-*-*-*-*- " + str(i + 1) + " -*-*-*--*-*-"
        text += '\n' + link_details[i][:600] + '\n' + links[i]

    # create javascript code
    text += "\n\n['{}'".format(web_search_link)
    for i in range(max_index):
        text += ",'{}'".format(links[i])
    text += "].forEach(link => window.open(link));"

    # send message to tg
    grader.tg.bot.send_message(grader.tg.chat_id, text)
    return query_text