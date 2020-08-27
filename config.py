graders_info_admin = [
    {
        "_id": 1,
        "name": "Chris Cheung",
        "login": "chris",
        "pw": "!23456Qwerty",
        "level": 's'
    },
    {
        "_id": 2,
        "name": "Tiffany Chui",
        "login": "tiffany",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 3,
        "name": "TowMing Ng",
        "login": "tomming",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 4,
        "name": "Tobby Chan",
        "login": "tobby",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 5,
        "name": "Yau Kuen Choi",
        "login": "raymond",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 6,
        "name": "Nices Lai",
        "login": "nices",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 7,
        "name": "Ian Tsui",
        "login": "ian",
        "pw": "!23456Qwerty"
    },
    {
        "_id": 8,
        "name": "Raymond Ho",
        "login": "phoebe",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 9,
        "name": "Nicole Lee",
        "login": "alan",
        "pw": "!23456Qwerty"
    },
    {
        "_id": 10,
        "name": "Ginny Ng",
        "login": "ginny",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 11,
        "name": "Vianna Tsang",
        "login": "vianna",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 12,
        "name": "PoHong Yan",
        "login": "yan",
        "pw": "!23456Qwerty",
        "level": 'n'
    },
    {
        "_id": 13,
        "name": "common_user",
        "login": "common_user",
        "pw": "!23456Qwerty",
        "level": 'n'
    }
]

# saf spot12 classify eval3 token
projects_info_admin = \
[
    {
    "name": "CEval-random-relevance-saf-2020-08-23",
    "type": "saf",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-saf-2020-08-23/overview"
    },
    {
    "name": "CEval-random-relevance-spot1-2020-08-23",
    "type": "spot12",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-spot1-2020-08-23/overview"
    },
    {
    "name": "CEval-random-relevance-spot2-2020-08-23",
    "type": "spot12",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/CEval-random-relevance-spot2-2020-08-23/overview"
    },
    {
    "name": "CEval-random-query-classification-saf-2020-07-03",
    "type": "classify",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/CEval-random-query-classification-saf-2020-07-03/overview"
    },
    {
    "name": "CEval-random-query-classification-spot1-2020-07-03",
    "type": "classify",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/CEval-random-query-classification-spot1-2020-07-03/overview"
    },
    {
    "name": "CEval-random-query-classification-spot2-2020-07-03",
    "type": "classify",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/CEval-random-query-classification-spot2-2020-07-03/overview"
    },
    {
    "name": "dr-qa-20200817-2",
    "type": "classify",
    "location": "zh_HK",
    "link": "https://crowdcollect2.siri.apple.com/main/project/dr-qa-20200817-2/overview"
    }
]

help_command = {
    "Guide": {
        "1.": "Choose the specific project in Menu",
        "2.": "If project link is outdated, type -l to go to project manually",
        "3.": "Type -p switch to other project (ensure correct project type)",
        "4.": "Thanks"
    },
    "spot12/saf/eval3": {
        "`": "Web Search",
        "~": "Web Search + result links",
        "!": "Close Tabs",
        "i": "Inappropriate",
        "l": "Wrong Language",
        "x": "Cannot be judge / missing info",
        "e": "excellent",
        "g": "good",
        "f": "fair",
        "b": "bad"
    },
    "Control Command": {
        "-l": "go to that website, -l https://google.com",
        "-q": "quit program",
        "-p": "switch to different project type"
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

graders_info = []

projects_info = []