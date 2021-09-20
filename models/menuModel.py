import config
from utils.inputs import *

# def print_ghost_proj_list():
#     print("\n")
#     print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
#     print("Please choose the required project Number: ")
#     for index, project in enumerate(config.ghost_projects_info):
#         print("{}: {} ({})".format(str(index+1), project["name"], project["type"]))

# for tg project list
def get_project_list_text(prev_project_index, projects_info):
    txt = ''
    txt += "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n"
    txt += "Please choose the required project Number: \n"
    for index, project in enumerate(projects_info):
        if index == prev_project_index:
            txt += "\u001b[32;1m{}: {})\u001b[0m\n".format(str(index+1), project["name"])
        else:
            txt += "{}: {})\n".format(str(index + 1), project["name"])
    return txt

# def print_proj_list(pre_project_index, projects_info):
#     proj_txt = get_project_list_text(pre_project_index, projects_info)
#     print(proj_txt)

def menu_choice(prev_project_index, ghost=False):
    if not ghost:
        projects_info = config.projects_info
    else:
        projects_info = config.ghost_projects_info
    max_proj_num = len(projects_info)
    project_index = None
    while(project_index==None):
        print(get_project_list_text(prev_project_index, projects_info))
        project_index = num_input()
        if project_index == None:
            continue
        if (project_index <= 0 or project_index > max_proj_num):
            print("Invalid range of Number.")
            project_index = None
            continue
        project_index = project_index - 1 # 0 base
    return project_index

# def ghost_menu_choice():
#     max_proj_num = len(config.ghost_projects_info)
#     project_index = None
#     while(project_index==None):
#         print_ghost_proj_list()
#         project_index = num_input()
#         if project_index == None:
#             continue
#         if (project_index <= 0 or project_index > max_proj_num):
#             print("Invalid range of Number.")
#             project_index = None
#             continue
#         project_index = project_index - 1
#     return project_index
