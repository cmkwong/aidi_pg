import re
import os

# update the project list locally
def read_txt_file(path, filename):
    full_path = os.path.join(path, filename)
    with open(full_path, 'r') as f:
        txt = f.read()
    f.close()
    return txt

def find_locale_from_prjName(name):
    result = re.search(r"[a-z][a-z]_[A-Z][A-Z]", name)
    if result:
        return result.group(0)

def txt2prjdict(txt, web_controller):
    prj_list = []
    linkDelimiter = 'http'
    # eliminate all splace and replace last element into overview
    txt = txt.replace(' ', '').replace('\t', '').replace('\xa0', '').replace('stats/ungradedByLocale', 'overview')
    prjs = txt.split('\n')
    for prj in prjs:
        if len(prj) > 0:
            p_dict = {}
            # find if link exist
            if prj.find(linkDelimiter) > 0:
                prjLocale, link = prj.split(linkDelimiter)
                prjName, locale = find_locale_from_prjName(prjLocale)
                p_dict['name'] = prjName
                p_dict['location'] = locale
                p_dict['link'] = linkDelimiter + link
                prj_list.append(p_dict)
            # no link pre-fill, then find on CC
            else:
                prjLocale = prj
                prjName, locale = find_locale_from_prjName(prjLocale)
                p_dict['name'] = prjName
                p_dict['location'] = locale
                p_dict['link'] = web_controller.findProjectLinkByName(prjName, 5000)
    print("Number of projects: {}".format(len(prj_list)))
    return prj_list

def get_projectList_from_txt(web_controller):
    txt = read_txt_file(path="../docs", filename="projects.txt")
    project_list = txt2prjdict(txt, web_controller)
    return project_list