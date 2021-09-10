
# projects that get query text in inner box
GET_QUERY_TEXT_PROJS = ["standard", "sbs"]

# projects need to access the database
UPDATE_DB_PROJS = ["standard", "classify", "valid"]

GET_QUERY_TEXT_COMMAND = {
    "standard": """return document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.getElementsByClassName('search-input form-control')[0].getAttribute('value');""",
    "valid": """return document.querySelector('#widget-container h1').innerText;""",
    "sbs": """return document.querySelector('.utterance').innerText;""",
    "token": """return document.querySelector('#input-field').querySelector('input').value;""",
    "classify": """return document.querySelector('#display-section').querySelector('h1').textContent;""",
}

CLICK_WEB_SEARCH_COMMAND = {
    "standard": """document.getElementsByClassName('clicked validates-clicked')[0].click();""",
    "valid": """document.getElementsByClassName('clicked validates-clicked')[0].click();""",
    "sbs": """document.querySelector('.punchout-link').click();""", # side-by-side project
}

CLICK_NEXT_BTN_COMMAND = {
    "standard": """document.getElementsByClassName('clicked validates-clicked')[0].click();""",
    "valid": """document.getElementsByClassName('clicked validates-clicked')[0].click();""",
    "sbs": """
        const nextWait = setInterval(function() {
            if (!document.getElementsByClassName('forward-btn')[0].querySelector('i.ban')) {
                document.getElementsByClassName('forward-btn')[0].click();
                clearInterval(nextWait);
                return;
            }
        },50)
    """,
}

GET_WEB_SEARCH_LINK_COMMAND = {
    "standard": """return document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href');""",
    "valid": """return document.getElementsByClassName('clicked validates-clicked')[0].getAttribute('href');""",
    "sbs": """return document.querySelector('.punchout-link').getAttribute('href');""",
}

GET_RESULT_LINKS_COMMAND = {
    "standard": """
            const results = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.querySelectorAll("div.parsec-result");
            links = [];
            for (let i=0; i<results.length; i++) {
                if (getComputedStyle(results[i],'::after').content === "counter(section)") {
                    links.push(results[i].querySelector('a').getAttribute('href'));
                }
            }
            return links;
        """,
    "sbs": """
        const links = [];
        document.querySelectorAll('.info-box').forEach(node => {
          node.querySelectorAll('a').forEach(el => links.push(el.href))
        });
        return links;
    """
}

GET_LINK_DETAILS_COMMAND = {
    "standard": """
        const results = document.getElementsByClassName('iframe')[0].getElementsByTagName('iframe').item(0).contentDocument.querySelectorAll("div.parsec-result");
        details = [];
        for (let i=0; i<results.length; i++) {
            let title = '';
            if (results[i].querySelector('.title')) { 
                title = results[i].querySelector('.title').textContent.trim();
            } else {
                title = "Empty Title";
            };
            let description = '';
            let description_list = results[i].querySelectorAll('.description');
            if (description_list.length !== 0) {
                for (let k=0; k < description_list.length; k++) {
                    description += description_list[k].textContent.trim() + '\\n';
                }
            } else {
                description = "Empty Description";
            };
            details.push(title + '\\n' + description);
        }
        return details;
    """,
    "sbs": """
        const details = [];
        let cards = ['L', 'R'];
        let c = 0;
        document.querySelectorAll('.info-box').forEach(node => {
            let card = cards[c];
            let count = 1
            node.querySelectorAll('a').forEach(el => {
              details.push(`${card}${count}: ${el.querySelector('p')?.textContent.trim()}`);
              count++;
              c++;
            })
        });
        return details;
    """
}

GET_SEARCH_DATE_COMMAND = {
    "standard": """
        return document.querySelector(".message.blue").querySelector("p").firstChild.textContent;
    """,
    "sbs": """
        return document.querySelector('.html-widget-wrapper').querySelector('p').textContent;
    """
}

INSERT_COMMENT_COMMAND = {
    "standard": """
        const ta = document.querySelector('textarea');
        ta.value = '%s';
        ta.dispatchEvent(new Event('input'));
    """,
    "classify": """
        const ta = document.querySelector('textarea');
        ta.value = '%s';
        ta.dispatchEvent(new Event('input'));
    """,
    "sbs": """
        const ta = document.querySelector('textarea');
        ta.value = '%s';
        ta.dispatchEvent(new Event('input'));
    """
}

SCROLL_TO_VIEW_COMMAND = {
    "sbs": """document.querySelector('.utterance')?.scrollIntoView();"""
}

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
        "-md": "activate timer",
        "-nd": "de-activate timer",
        "-alarm": "sound on",
        "-nalarm": "sound off",
        "-report/-re": "access the report page",
        "-txt": "print the summary of report(Disabled)"
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

sbs_extra_info_list = [
    "\t1. I need more context on this request (e.g., previous request)",
    "\t2. The request was gibberish or incomplete",
    "\t3. Siri's response was missing or had display error",
    "\t4. Some other reason (fill out comment box)",
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

projects_code = {} # store the project_code with respect to each of project_id

ghost_projects_info = []