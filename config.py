# # s = super user; a = auto user; n = no access;
# graders_info_admin = [
#
# ]
#
# # saf spot12 amp classify eval3 token
# projects_info_admin = [
#
# ]
#
# # saf spot12 amp classify eval3 token
# ghost_projects_info_admin = [
#
# ]
#
# # control version
# version_admin = {
#     "version": "0.0.1"
# }

# projects that get query text in inner box
GET_QUERY_TEXT_PROJS = ["spot12", "saf", "eval3", "amp", "deepscrape"]

# projects need to access the database
UPDATE_DB_PROJS = ["spot12", "saf", "eval3", "classify", "amp", "deepscrape"]

# projects that need to open 10 results webpages
MAX_TEN_RESULTS_PROJS = ["amp", "deepscrape"]
MAX_ONE_RESULTS_PROJS = ["saf"]

help_command = {

    "spot12/saf/eval3": {
        "`": "Web Search",
        "~": "Web Search + result links",
        "!": "Close Tabs",
        "n": "Inappropriate query (added before the answer eg: nffg)",
        "i": "Inappropriate result",
        "l": "Wrong Language",
        "x": "Cannot be judge / missing info",
        "e": "excellent",
        "g": "good",
        "f": "fair",
        "b": "bad"
    },
    "Mac Control Command": {
        "-q": "quit program",
        "-p": "update and show project menu",
        "-done": "set done counter manually",
        "-t": "set delay time (seconds)",
        "-md/-nd": "activate timer / de-activate timer",
        "-alarm/-nalarm": "sound on / sound off",
        "-report": "access the current report",
        "-text": "print the summary of report"
    },
    "Telegram Control Command": {
        "/status": "check done count",
        "/p": "switch to project menu",
        "/done": "set done count manually",
        "/stop": "interrupt the timer (= Ctrl+C)",
        "/t": "set delay time (seconds)",
        "/md /nd": "activate timer / de-activate timer",
        "/mute": "silence on",
        "/nmute": "silence off",
        "/q": "turn off telegram"
    }
}

classify_extra_info_list = [
    "\nClassify Menu:",
    "\t",
    "\t1. Arts and Entertainment \t\t\t\t\t\t1. Learn About",
    "\t2. Food and Drink \t\t\t\t\t\t\t2. Learn Answer",
    "\t3. Sports \t\t\t\t\t\t\t\t3. E-shop",
    "\t4. Health, Fitness, Medicine and Science \t\t\t\t4. Locate",
    "\t5. General Retailers and Marketplaces \t\t\t\t\t5. Be Entertained",
    "\t6. Business, Industry, Economics and Finance \t\t\t\t6. Launch/download",
    "\t7. Computing, Technology, Telecommunications and Internet Use \t\t7. Find Online Service",
    "\t8. Life \t\t\t\t\t\t\t\t8. Navigate",
    "\t9. Places, Travel, Cars and Transportation \t\t\t\t9. Other",
    "\ta. Society, Education, Gov, Religion, Hist ",
    "\tb. Other \t\t\t\t\t\t\t\t",
    "\t",
    "\ta. Answer(simple)\tb. Answer(text)\t\tc. APP\t\t\td. Book",
    "\te. Dictionary\t\tf. Flight Status\tg. Home Page\t\th. Image",
    "\ti. Map\t\t\tj. Movie\t\tk. Music\t\tl. News",
    "\tm. Podcast\t\tn. Sports\t\to. Stocks\t\tp. TV show",
    "\tq. Video\t\tr. Weather\t\ts. Wiki\t\t\tt. Other",
    "\tu. None",
    "\t"
]

MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

graders_info = []

projects_info = []

ghost_projects_info = []