import config
from utils.inputs import *

def print_ghost_proj_list():
    print("\n")
    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    print("Please choose the required project Number: ")
    for index, project in enumerate(config.ghost_projects_info):
        print("{}: {} ({})".format(str(index+1), project["name"], project["type"]))

# for tg project list
def get_project_list_text():
    txt = ''
    txt += "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n"
    txt += "Please choose the required project Number: \n"
    for index, project in enumerate(config.projects_info):
        txt += "{}: {} ({})\n".format(str(index+1), project["name"], project["type"])
    return txt

def print_proj_list():
    proj_txt = get_project_list_text()
    print(proj_txt)

def menu_choice():
    max_proj_num = len(config.projects_info)
    project_index = None
    project_type = None
    while(project_index==None):
        print_proj_list()
        project_index = num_check()
        if project_index == None:
            continue
        if (project_index <= 0 or project_index > max_proj_num):
            print("Invalid range of Number.")
            project_index = None
            continue
        project_index = project_index - 1
        project_type = config.projects_info[project_index]["type"]
    print("Type of Project:", project_type)
    return project_index

def ghost_menu_choice():
    max_proj_num = len(config.ghost_projects_info)
    project_index = None
    project_type = None
    while(project_index==None):
        print_ghost_proj_list()
        project_index = num_check()
        if project_index == None:
            continue
        if (project_index <= 0 or project_index > max_proj_num):
            print("Invalid range of Number.")
            project_index = None
            continue
        project_index = project_index - 1
        project_type = config.ghost_projects_info[project_index]["type"]
    print("Type of Project: ", project_type)
    return project_index
