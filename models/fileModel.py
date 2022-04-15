import re
import os

# update the project list locally
def read_txt_file(path, filename):
    full_path = os.path.join(path, filename)
    with open(full_path, 'r') as f:
        txt = f.read()
    f.close()
    return txt

# for sbs project
def txt2SbsSent(rawText):
    sbsSent = {}
    lines = rawText.split('\n')
    for line in lines:
        num, sent = line.split(' ', 1)
        if not num.isnumeric():
            print(f"{line}: wrong syntax")
            return False
        sbsSent[int(num.strip())] = sent.strip()
    return sbsSent

def find_locale_from_prjName(prjLocale):
    result = re.search(r"[ze][hn]_[HTU][KWS]", prjLocale)
    if result:
        locale = result.group(0)
        prj_name = prjLocale.replace(locale, '')
        return prj_name.strip(), locale.strip()

def txt2prjdict(txt, web_controller):
    prj_list = []
    linkDelimiter = 'http'
    # eliminate all splace and replace last element into overview
    txt = txt.replace('stats/ungradedByLocale', 'overview')
    prjs = txt.split('\n')
    for prj in prjs:
        if len(prj) > 0:
            p_dict = {}
            # find if link exist
            if prj.find(linkDelimiter) > 0:
                prj_locale_str, link = prj.split(linkDelimiter)
                prjName, locale = find_locale_from_prjName(prj_locale_str)
                p_dict['name'] = prjName
                p_dict['location'] = locale
                p_dict['link'] = linkDelimiter + link
            # no link pre-fill, then find on CC
            else:
                prj_locale_str = prj
                prjName, locale = find_locale_from_prjName(prj_locale_str)
                p_dict['name'] = prjName
                p_dict['location'] = locale
                prjLink = web_controller.findProjectLinkByName(prjName, 10000)
                # if cannot get the project link return False
                if not prjLink:
                    print(f'{prjName} cannot get the project link, please check if wrong project name and retry again.')
                    return False
                p_dict['link'] = prjLink
            prj_list.append(p_dict)
    print("Number of projects: {}".format(len(prj_list)))
    return prj_list

def get_projectList_from_txt(web_controller):
    txt = read_txt_file(path="../docs", filename="projects.txt")
    project_list = txt2prjdict(txt, web_controller)
    return project_list