import config
import re
from datetime import datetime
class Checker:
    def __init__(self, db_controller):
        self.db_controller = db_controller

    def get_project_status_format(self):
        project_status_format = {}
        for i in range(len(config.graders_info)):
            project_status_format[config.graders_info[i]['name']] = -1
        return project_status_format

    def get_projectId_by_project_index(self, project_index):
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
        project_id = self.get_projectId_by_project_index(project_index)
        locale = config.projects_info[project_index]["location"]
        # get the project status from database
        project_status = self.db_controller.get_project_status(project_id, locale)
        # get the init format
        project_status_format = self.get_project_status_format()
        for name, time in project_status.items():
            project_status_format[name] = (current_utc - time) / 60
        # sorted the dictionary
        sorted_project_status_format = {k: v for k, v in sorted(project_status_format.items(), key=lambda item: item[1])}
        for k, v in sorted_project_status_format.items():
            print("{}: {} mins".format(k,v))

    def update_project_from_txt(self):
        pass