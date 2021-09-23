import config
import re
import os
from datetime import datetime

class Checker:
    def __init__(self, db_controller, version):
        self.db_controller = db_controller
        self.prev_project_index = -1
        self.version = version
        self._empty = 99999

    def check_version(self):
        if self.db_controller.get_most_updated_version() != self.version:
            raise Exception("Outdated Version, re-open program.")

    def init_project_status_container(self):
        project_status_container = {}
        for i in range(len(config.graders_info)):
            if config.graders_info[i]['name'] != "common_user":
                project_status_container[config.graders_info[i]['name']] = self._empty
        return project_status_container

    def get_projectId_from_config(self, project_index):
        project_link = config.projects_info[project_index]["link"]
        result = re.search(r"/project/(\S+?)/", project_link)
        project_id = None
        if result:
            project_id = result.group(1)
        return project_id

    def print_project_status(self, project_index):
        # set previous project index
        self.prev_project_index = project_index
        # get current UTC timestamp
        current_utc = datetime.utcnow().timestamp()
        # get the project ID and its locale from current config file
        project_id = self.get_projectId_from_config(project_index)
        locale = config.projects_info[project_index]["location"]
        # get the project status from database
        project_status = self.db_controller.get_project_status(project_id, locale)
        # check if there is project
        if not project_status:
            print("No graders update this project yet")
            return False
        # get the init container and assign the value into the container
        project_status_container = self.init_project_status_container()
        for name, time in project_status.items():
            project_status_container[name] = (current_utc - time) / 60
        # sorted the dictionary
        sorted_project_status_container = {k: v for k, v in sorted(project_status_container.items(), key=lambda item: item[1])}
        # print status
        txt = ''
        txt += "\u001b[1m\n\u001b[34m{}\u001b[0m\u001b[0m\n\n".format(project_id)
        txt += "{:<8}\u001b[4m{:<20}{:<10}{:<10}{:<10}{:<10}\u001b[0m\n".format('', "Grader", "mins", "pop-up", "prj id", "locale")
        for name, mins in sorted_project_status_container.items():
            mins = round(mins, 2)
            if mins == self._empty:
                txt += "{:<8}{:<20}{:<10}\u001b[31;1m{:<10}\u001b[0m\n".format('', name, '--', 'NO')
            else:
                txt += "{:<8}{:<20}{:<10}\u001b[32;1m{:<10}{:<10}{:<10}\u001b[0m\n".format('', name, mins, 'OK', 'OK', 'OK')
        print(txt)

    def read_txt_file(self, path, filename):
        full_path = os.path.join(path, filename)
        with open(full_path, 'r') as f:
            txt = f.read()
        f.close()
        return txt

    def find_locale_from_prjName(self, name):
        result = re.search(r"[a-z][a-z]_[A-Z][A-Z]", name)
        if result:
            return result.group(0)

    def txt2prjdict(self, txt):
        prj_list = []
        delimiter = 'http'
        # eliminate all splace and replace last element into overview
        txt = txt.replace(' ', '').replace('\t', '').replace('\xa0', '').replace('stats/ungradedByLocale', 'overview')
        prjs = txt.split('\n')
        for prj in prjs:
            if len(prj) > 0:
                name, link = prj.split(delimiter)
                p_dict = {}
                p_dict['name'] = name
                p_dict['location'] = self.find_locale_from_prjName(name)
                p_dict['link'] = delimiter + link
                prj_list.append(p_dict)
        print("Number of projects: {}".format(len(prj_list)))
        return prj_list

    def print_projectList_confirm(self, prj_list):
        txt = ''
        txt += "{:<4}\u001b[4m{:<80}{:<10}{:<50}\u001b[0m\n".format('', "Project", "Locale", "Link")
        for idx, p in enumerate(prj_list):
            txt += "{:<4}{:<80}{:<10}{:<50}\n".format(idx, p['name'][-80:], p['location'], p['link'][-50:])
        print(txt)

    def get_projectList_from_txt(self):
        txt = self.read_txt_file(path="../docs", filename="projects.txt")
        project_list = self.txt2prjdict(txt)
        return project_list
