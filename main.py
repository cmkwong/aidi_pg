from controllers import dbController, checkerController
from models import answerModel

command = False
VERSION = "0.0.1"

db_controller = dbController.Database()
checker = checkerController.Checker(db_controller)

FIRST_TIME = True
MAIN_LOOP_COUNT = 0

while (not (command == "quit")):

    if FIRST_TIME:
        # update the file from project text file
        FIRST_TIME = False

    # ask user to input
    command = answerModel.enter(checker)
    MAIN_LOOP_COUNT += 1