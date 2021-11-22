from models import conflictModel


def print_list(grader, str_list):
    for string in str_list:
        print_at(string, grader.tg, grader.print_allowed)

def print_at(txt, tg=None, print_allowed=True):
    if print_allowed:
        if tg == None:
            print(txt)
        else:
            tg.bot.send_message(tg.chat_id, txt)

def print_conflict(conflict, tg):
    print_text = ''
    for i in range(conflict.total):
        ans_dist_text = conflictModel.output_popular_ans_dist(conflict.ans_dists[i])
        print_text += ans_dist_text
        print_text += "{}\nAns: {}: Your Ans: {}\nlink: {}\n\n".format(
            conflict.texts[i], conflict.anss[i], conflict.usr_anss[i], conflict.links[i])
    print_text += "Total conflict: {}".format(conflict.total)
    print_at(print_text, tg)

def print_popular_ans_detail(Answer, tg):
    print_text = ''
    grader_list_text = conflictModel.output_popular_detail(Answer.detail)
    ans_dist_text = conflictModel.output_popular_ans_dist(Answer.ans_dist)
    print_text += grader_list_text + ans_dist_text
    print_text += "Final Ans: " + Answer.ans + "\n"
    print_at(print_text, tg)

def print_status(grader):
    done = str(grader.query_done).strip()
    delays = str(grader.time_delay).strip()
    md = str(grader.manual_timer).strip()
    print_at("Done: {} t-{} MD-{}\n".format(done, delays, md), grader.tg, grader.print_allowed)

def print_projectList_confirm(prj_list):
    txt = ''
    txt += "{:<3}\u001b[4m{:<50}{:<10}{:<50}\u001b[0m\n".format('', "Project (Head 45 char)", "Locale", "Link (Tail 50 char)")
    for idx, p in enumerate(prj_list):
        txt += "{:<3}{:<50}{:<10}{:<50}\n".format(idx + 1, p['name'][:45], p['location'], p['link'][-50:])
    print(txt)