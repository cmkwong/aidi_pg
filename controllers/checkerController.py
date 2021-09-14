import config
import re
from datetime import datetime
class Checker:
    def __init__(self, db_controller, version):
        self.db_controller = db_controller
        self.version = version

    def check_version(self):
        if self.db_controller.get_most_updated_version != self.version:
            return False

    def get_project_status_container(self):
        project_status_container = {}
        for i in range(len(config.graders_info)):
            if config.graders_info[i]['name'] != "common_user":
                project_status_container[config.graders_info[i]['name']] = 99999
        return project_status_container

    def get_projectId_from_config(self, project_index):
        project_link = config.projects_info[project_index]["link"]
        result = re.search(r"/project/(\S+?)/", project_link)
        project_id = None
        if result:
            project_id = result.group(1)
        return project_id

    def print_project_status(self, project_index):
        # get current UTC timestamp
        current_utc = datetime.utcnow().timestamp()
        # get the project ID and its locale from current config file
        project_id = self.get_projectId_from_config(project_index)
        locale = config.projects_info[project_index]["location"]
        # get the project status from database
        project_status = self.db_controller.get_project_status(project_id, locale)
        # check if there is project
        if not project_status:
            print("No member update this project yet")
            return False
        # get the init container and assign the value into the container
        project_status_container = self.get_project_status_container()
        for name, time in project_status.items():
            project_status_container[name] = (current_utc - time) / 60
        # sorted the dictionary
        sorted_project_status_container = {k: v for k, v in sorted(project_status_container.items(), key=lambda item: item[1])}
        for k, v in sorted_project_status_container.items():
            print("{:<20}{:<6}mins".format(k, round(v, 1)))

    def update_project_from_txt(self):
        pass