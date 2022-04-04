import config
from utils.inputs import *

# for tg project list
def get_project_list_text(prev_project_index, projects_info, tg=False):
    # build the text menu
    txt = ''
    txt += "-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n"
    txt += "Please choose the required project Number: \n"
    for index, project in enumerate(projects_info):
        if index == prev_project_index:
            # define highlight text (tg or non-tg)
            if not tg:
                txt += config.bcolor.OKGREEN.format(f"{str(index + 1)}: [{project['location']}]{project['name']}\n")
            else:
                txt += config.bcolor.STAR.format(f"{str(index + 1)}: [{project['location']}]{project['name']}\n")
        else:
            txt += f"{str(index + 1)}: [{project['location']}]{project['name']}\n"
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
        project_index = int_input()
        if project_index == None:
            continue
        if (project_index <= 0 or project_index > max_proj_num):
            print("Invalid range of Number.")
            project_index = None
            continue
        project_index = project_index - 1 # 0 base
    return project_index
