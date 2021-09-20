import config
from utils.inputs import *

# for tg project list
def get_project_list_text(prev_project_index, projects_info, tg=False):
    # define highlight text (tg or non-tg)
    if not tg:
        hl_start, hl_end = "\u001b[32;1m", "\u001b[0m"
    else:
        hl_start, hl_end = "**", "**"

    # build the text menu
    txt = ''
    txt += "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n"
    txt += "Please choose the required project Number: \n"
    for index, project in enumerate(projects_info):
        if index == prev_project_index:
            txt += "{}{}: {}{})\u001b[0m\n".format(hl_start, str(index+1), project["name"], hl_end)
        else:
            txt += "{}: {})\n".format(str(index + 1), project["name"])
    return txt

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
