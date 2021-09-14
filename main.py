from controllers import dbController, checkerController
from models import answerModel

command = False
VERSION = "0.0.1"

db_controller = dbController.Database()
checker = checkerController.Checker(db_controller, VERSION)

MAIN_LOOP_COUNT = 0

while (not (command == "quit")):

    # ask user to input
    command = answerModel.enter(checker)
    MAIN_LOOP_COUNT += 1