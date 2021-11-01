from controllers import gradingController, dbController, webController

command = False
VERSION = "0.0.18"

default_url = "https://crowdcollect2.siri.apple.com/main/project/"
db_controller = dbController.Database()
db_controller.get_graders_info()
web_controller = webController.Web(init_url=default_url)
web_controller.open_chrome()
web_controller.init_working_tag()
graders = gradingController.Graders(web_controller, db_controller, VERSION)

MAIN_LOOP_COUNT = 0

while (not (command == "quit")):

    command = graders.run(command)

    MAIN_LOOP_COUNT += 1

web_controller.quite_driver()