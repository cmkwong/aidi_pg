from models import infoModel

def _form_result_text(link_detail, text=''):
    text += "{}({})\n".format(link_detail['title'], link_detail['type'])
    text += "{}\n".format(link_detail['description'][:300])
    text += "{}\n".format(link_detail[link_detail['footnote']])
    text += "{}\n".format(link_detail[link_detail['link']])
    return text

def _form_tg_send_text(search_date, query_text, web_search_link, max_index, link_details):
    # query and its introduction
    text = search_date + '\n\n' + query_text + '\n' + \
           "web search link: " + web_search_link + '\n' + \
           "No. of Results: " + str(max_index)
    # link details text and links
    for i in range(max_index):
        text += "\n\n-*-*-*-*-*- " + str(i + 1) + " -*-*-*--*-*-"
        text += '\n' + _form_result_text(link_details[i], text)

    # create javascript code
    text += "\n\n['{}'".format(web_search_link)
    for i in range(max_index):
        text += ",'{}'".format(link_details[i]['link'])
    text += "].forEach(link => window.open(link));"

# for tg_bot.py used
def send_tg_info(grader, old_query_text=None):

    # get query text (plus condition)
    query_text = grader.get_query_text(filter_query=old_query_text)
    if not query_text:
        return False
    try:
        # get search date
        search_date = grader.web_controller.get_search_date(grader.project_type)
        # get web search links
        web_search_link = grader.web_controller.get_web_search_link(grader.project_type)
        # get links and its details
        link_details = grader.get_links_and_details()
    except:
        return False

    max_index = min(len(link_details), grader.project_code["max_answer_slots"])
    # query and its introduction
    text = _form_tg_send_text(search_date, query_text, web_search_link, max_index, link_details)

    # send message to tg
    grader.tg.bot.send_message(grader.tg.chat_id, text)
    return query_text