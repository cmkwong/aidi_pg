from models import infoModel

def _build_dummy_link_details():
    link_details = []
    for i in range(5):
        link_details.append({
            'type': 'type_na',
            'title': 'title_na',
            'description': 'description_na',
            'footnote': 'footnote_na',
            'link': 'http://na'
        })
    return link_details

def _form_result_text(link_detail):
    text = ''
    text += "type: {}:\n{}\n".format(link_detail['type'], link_detail['title'])
    text += "{}\n".format(link_detail['description'][:200])
    text += "footnote: {}\n".format(link_detail['footnote'])
    text += "link: {}\n".format(link_detail['link'])
    return text

def _form_tg_send_text(search_date, query_text, web_search_link, max_index, link_details):
    # query and its introduction
    text = search_date + '\n\n' + query_text + '\n' + \
           "web search link: " + web_search_link + '\n' + \
           "No. of Results: " + str(max_index)
    # link details text and links
    for i in range(max_index):
        text += "\n\n-*-*-*-*-*- " + str(i + 1) + " -*-*-*--*-*-"
        text += '\n' + _form_result_text(link_details[i])

    # create javascript code
    text += "\n\n['{}'".format(web_search_link)
    for i in range(max_index):
        text += ",'{}'".format(link_details[i]['link'])
    text += "].forEach(link => window.open(link));"
    return text

# for tg_bot.py used
def send_tg_info(grader):

    # get query text (plus condition)
    grader.query_prepare(auto=False)
    query_text = grader.query_text
    if not query_text:
        return False
    try:
        # get search date
        search_date = grader.web_controller.get_search_date(grader.project_type)
    except:
        search_date = 'search_date'
    try:
        # get web search links
        web_search_link = grader.web_controller.get_web_search_link(grader.project_type)
    except:
        web_search_link = 'https://www.google.com.hk/'
    try:
        # get links and its details
        link_details = grader.get_links_and_details()
        if not link_details:
            link_details = _build_dummy_link_details()
    except:
        link_details = _build_dummy_link_details()

    max_index = min(len(link_details), grader.project_code["max_answer_slots"])
    # query and its introduction
    text = _form_tg_send_text(search_date, query_text, web_search_link, max_index, link_details)

    # send message to tg
    grader.tg.bot.send_message(grader.tg.chat_id, text)
    return query_text