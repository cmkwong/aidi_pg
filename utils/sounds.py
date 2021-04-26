import os

def beep(text, tg):
    if not tg:
        sound = "say " + text
        os.system(sound)