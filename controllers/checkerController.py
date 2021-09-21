import config
import re
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
        txt += "\u001b[1m\n\u001b[34m{}\u001b[0m\u001b[0m\n".format(project_id)
        txt += "\u001b[4m{:<20}{:<10}{:<10}{:<10}\u001b[0m\n".format("Grader", "mins", "prj id", "locale")
        for name, mins in sorted_project_status_container.items():
            mins = round(mins, 2)
            if mins == self._empty:
                txt += "{:<20}{:<10}\n".format(name, '--')
            else:
                txt += "{:<20}{:<10}\u001b[32;1m{:<10}{:<10}\u001b[0m\n".format(name, mins, 'matched', 'matched')
        print(txt)

    def update_project_from_txt(self):
        pass