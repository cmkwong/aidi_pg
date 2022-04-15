
# projects that get query text in inner box
# GET_QUERY_TEXT_PROJS = ["standard", "classify", "valid", "sbs"]

# projects need to access the database
UPDATE_DB_PROJS = ["standard", "classify", "valid", "sbs"]

# projects that auto allowable
AUTO_ALLOWED_PROJS = ["standard", "classify", "valid"]

# sbs = side-by-side project
GET_QUERY_TEXT_COMMAND = {
    "standard": """
        let query_text;
        query_text = document.querySelector('iframe')?.contentDocument?.querySelector('.search input')?.getAttribute('value');
        if (!query_text) {
            query_text = document.getElementById('query-container')?.querySelector('i')?.innerText.trim(); // this is for new interface
        }
        return query_text;
        """,
    "valid": """return document.querySelector('#widget-container h1')?.innerText;""",
    "sbs": """return document.querySelector('.utterance')?.innerText;""",
    "token": """return document.querySelector('#input-field')?.querySelector('input')?.value;""",
    "classify": """return document.querySelector('#display-section')?.querySelector('h1')?.textContent;""",
}

CLICK_WEB_SEARCH_COMMAND = {
    "standard": """
        let clickSearchBtn;
        clickSearchBtn = document.getElementsByClassName(
          'clicked validates-clicked'
        )[0];
        if (!clickSearchBtn) {
          clickSearchBtn = document.querySelector('#html-widget > a');
        }
        clickSearchBtn.click();
    """,
    "valid": """document.getElementsByClassName('clicked validates-clicked')[0].click();""",
    "sbs": """document.querySelector('.punchout-link').click();""",
}

# notInsert is for checking if answers allowed to insert to DB. If auto, forbidden, if manual, allowed.
CLICK_NEXT_BTN_COMMAND = {
    "standard": """
        let next_btn = document.getElementsByClassName("forward-btn")[0];
        '%s' === '1' ? next_btn.classList.add('notInsert') : next_btn.classList.remove('notInsert');
        next_btn.click();
    """,
    "valid": """
        let next_btn = document.getElementsByClassName("forward-btn")[0];
        '%s' === '1' ? next_btn.classList.add('notInsert') : next_btn.classList.remove('notInsert');
        next_btn.click();
    """,
    "sbs": """
        let next_btn = document.getElementsByClassName('forward-btn')[0];
        let nextWait = setInterval(function() {
            if (!next_btn.querySelector('i.ban')) {
                '%s' === '1' ? next_btn.classList.add('notInsert') : next_btn.classList.remove('notInsert');
                next_btn.click();
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

CLICK_ALL_RESULTS_COMMAND = {
    "standard": """
        function click_all_results(max_length) {
          let all_parsecResult;
          // for new version (usually in this form)
          all_parsecResult = document
            .querySelector('iframe')
            ?.contentDocument?.querySelectorAll('.result');
          // for old version
          if (!all_parsecResult) {
            all_parsecResult = document
              .getElementsByClassName('iframe')[0]
              ?.getElementsByTagName('iframe')
              ?.item(0)
              ?.contentDocument?.querySelectorAll('.parsec-result');
          }
          // for more new version 220404
          if (!all_parsecResult) {
            all_parsecResult = document.querySelectorAll('.result');
          }
          // click the link
          if (all_parsecResult) {
            [...all_parsecResult].slice(0, max_length).forEach((el) => {
              el.querySelector('a')?.click();
            });
          }
        }
        const max_len = Number('%s');
        click_all_results(max_len);
    """,
    "sbs": ""
}

GET_RESULT_LINKS_COMMAND = {
    "standard": """
            let all_parsecResult = [
              ...document
                .querySelector("iframe")
                .contentDocument.querySelectorAll(".result"),
            ];
            all_parsecResult.length !== 0
              ? all_parsecResult
              : (all_parsecResult = [
                  ...document
                    .getElementsByClassName("iframe")[0]
                    .getElementsByTagName("iframe")
                    .item(0)
                    .contentDocument.querySelectorAll(".parsec-result"),
                ]);
            let resultLinkArray = [];
            all_parsecResult.forEach((parsecResult) => {
              let link = parsecResult.querySelector("a")?.getAttribute("href");
              resultLinkArray.push(link ? link : "NO LINK");
            });
            return resultLinkArray;
        """,
    "sbs": """
        const links = [];
        document.querySelectorAll('.info-box').forEach(node => {
          node.querySelectorAll('a').forEach(el => links.push(el.href))
        });
        return links;
    """
}

GET_RESULT_LINK_DETAILS_COMMAND = {
    "standard": """
        function _get_result_title(result) {
          const filters = {
            v1: ".title",
            v2: ".result-card-title",
          };
          let title;
          for (const version in filters) {
            title = result.querySelector(filters[version])?.innerText;
            if (title) break;
          }
          return title;
        }
        
        function _get_result_description(result) {
          const filters = {
            v1: ".description",
            v2: ".result-card-description",
          };
          let description;
          for (const version in filters) {
            description = [...result.querySelectorAll(filters[version])]
              ?.map((des) => des.innerText.substring(0, 200))
              .join("\\n");
            if (description) break;
          }
          return description;
        }
        
        function _get_result_footnote(result) {
          const filters = {
            v1: ".footnote",
            v2: ".result-card-footnote",
          };
          let footnote;
          for (const version in filters) {
            footnote = result.querySelector(filters[version])?.innerText;
            if (footnote) break;
          }
          return footnote;
        }
        
        function getResults() {
          let all_resultDict;
            let all_parsecResult = [
              ...document
                .querySelector("iframe")
                .contentDocument.querySelectorAll(".result"),
            ];
            all_parsecResult.length !== 0
              ? all_parsecResult
              : (all_parsecResult = [
                  ...document
                    .getElementsByClassName("iframe")[0]
                    .getElementsByTagName("iframe")
                    .item(0)
                    .contentDocument.querySelectorAll(".parsec-result"),
                ]);
            all_resultDict = all_parsecResult.map((parsecResult) => {
              let type = parsecResult.parentNode.className.split(" ")[1];
              let title = _get_result_title(parsecResult);
              let description = _get_result_description(parsecResult);
              let footnote = _get_result_footnote(parsecResult);
              let link = parsecResult.querySelector("a")?.getAttribute("href");
              let resultDict = {
                type: type ? type : "",
                title: title ? title : "",
                description: description ? description : "",
                footnote: footnote ? footnote : "",
                link: link ? link : "",
              };
              return resultDict;
            });
          return all_resultDict;
        }
        let link_details = getResults();
        return link_details ? link_details : []
    """,
    "sbs": """
        function getSideResult() {
          let sideResults = {};
          // LHS
          sideResults['LHS'] = Array.from(
            document
              .querySelector('.side-by-side')
              .children[0].querySelectorAll('.summary')
          ).map((el) => {
            return el.innerText;
          });
          // RHS
          sideResults['RHS'] = Array.from(
            document
              .querySelector('.side-by-side')
              .children[1].querySelectorAll('.summary')
          ).map((el) => {
            return el.innerText;
          });
          return sideResults;
        }
        
        function getResults() {
          let all_resultDict = [];
          let sideResults = getSideResult();
          for (const key in sideResults) {
            let sideResult = sideResults[key]; // key = LHS/RHS
            sideResult.forEach((text) => {
              let resultDict = {
                type: key,
                title: '',
                description: text,
                footnote: '',
                link: '',
              };
              all_resultDict.push(resultDict);
            });
          }
          return all_resultDict;
        }
        return getResults();
    """
}

GET_QUERY_ANSWER_COMMAND = {
    "standard": """
        const MAX_STANDARD_ANSWER_LEN = 6;
        
        function _get_result_title(result) {
          const filters = {
            v1: ".title",
            v2: ".result-card-title",
          };
          let title;
          for (const version in filters) {
            title = result.querySelector(filters[version])?.innerText;
            if (title) break;
          }
          return title;
        }
        
        function _get_result_description(result) {
          const filters = {
            v1: ".description",
            v2: ".result-card-description",
          };
          let description;
          for (const version in filters) {
            description = [...result.querySelectorAll(filters[version])]
              ?.map((des) => des.innerText.substring(0, 200))
              .join("\\n");
            if (description) break;
          }
          return description;
        }
        
        function _get_result_footnote(result) {
          const filters = {
            v1: ".footnote",
            v2: ".result-card-footnote",
          };
          let footnote;
          for (const version in filters) {
            footnote = result.querySelector(filters[version])?.innerText;
            if (footnote) break;
          }
          return footnote;
        }
        
        function getProjectLink_Id_Locale_Querycode() {
          const url = window.location["href"];
          const re_id_locale = /\/project\/(\S+?)\/grading\/(\S+?)\/s\/(\S+?)\//;
          const matched_array = url.match(re_id_locale);
          if (matched_array) {
            return [url, matched_array[1], matched_array[2], matched_array[3]];
          }
          return ["", "", "", ""];
        }
        
        function getProjectType(project_id) {
          // return project type: sbs, standard
          const re_sbs = /(sbs)/;
          const result = project_id.match(re_sbs);
          if (result) {
            return "sbs";
          } else return "standard";
        }
        
        function getSearchDateLocation(project_type) {
          if (project_type === "standard") {
            const re_date = /from (.+?)\./;
            return document
              .querySelector(".message.blue")
              .querySelector("p")
              .firstChild.textContent.match(re_date)[1];
          } else if (project_type === "sbs") {
            return document.querySelector(".html-widget-wrapper").querySelector("p")
              .textContent;
          }
        }
        
        function getAnswer(project_type) {
          if (project_type === "standard") {
            let _ans = [];
            [...Array(MAX_STANDARD_ANSWER_LEN).keys()].forEach((el) => {
              if (
                document.getElementById(
                  `result${el}_validationresult${el}_inappropriate`
                )?.checked
              ) {
                _ans.push("i");
                return;
              }
              if (
                document.getElementById(
                  `result${el}_validationresult${el}_wrong_language`
                )?.checked
              ) {
                _ans.push("l");
                return;
              }
              if (
                document.getElementById(
                  `result${el}_validationresult${el}_cannot_be_judged`
                )?.checked
              ) {
                _ans.push("x");
                return;
              }
              if (document.getElementById(`result${el}_relevanceexcellent`)?.checked) {
                _ans.push("e");
                return;
              }
              if (document.getElementById(`result${el}_relevancegood`)?.checked) {
                _ans.push("g");
                return;
              }
              if (document.getElementById(`result${el}_relevancefair`)?.checked) {
                _ans.push("f");
                return;
              }
              if (document.getElementById(`result${el}_relevancebad`)?.checked) {
                _ans.push("b");
                return;
              }
            });
            const ans_str = _ans.join("");
            return ans_str;
          }
        }
        
        function getGrader() {
          return document
            .querySelector("#dd-menu__shared_component__-1-item0")
            .innerText.trim()
            .replace(/ /g, "");
        }
        
        function getResults(project_type) {
          let all_resultDict;
          if (project_type === "standard") {
            let all_parsecResult = [
              ...document
                .querySelector("iframe")
                .contentDocument.querySelectorAll(".result"),
            ];
            all_parsecResult.length !== 0
              ? all_parsecResult
              : (all_parsecResult = [
                  ...document
                    .getElementsByClassName("iframe")[0]
                    .getElementsByTagName("iframe")
                    .item(0)
                    .contentDocument.querySelectorAll(".parsec-result"),
                ]);
            all_resultDict = all_parsecResult.map((parsecResult) => {
              let type = parsecResult.parentNode.className.split(" ")[1];
              let title = _get_result_title(parsecResult);
              let description = _get_result_description(parsecResult);
              let footnote = _get_result_footnote(parsecResult);
              let link = parsecResult.querySelector("a")?.getAttribute("href");
              let resultDict = {
                type: type ? type : "",
                title: title ? title : "",
                description: description ? description : "",
                footnote: footnote ? footnote : "",
                link: link ? link : "",
              };
              return resultDict;
            });
          } else if (project_type === "sbs") {
            all_resultDict = [];
          }
          return all_resultDict;
        }
        
        function getQueryText(project_type) {
          if (project_type === "standard") {
            return document
              .querySelector("iframe")
              .contentDocument.querySelector(".search input")
              .getAttribute("value");
          } else if (project_type === "valid") {
            return document.querySelector("#widget-container h1").innerText;
          } else if (project_type === "sbs") {
            return document.querySelector(".utterance").innerText;
          } else if (project_type === "token") {
            return document.querySelector("#input-field").querySelector("input").value;
          } else if (project_type === "classify") {
            return document.querySelector("#display-section").querySelector("h1")
              .textContent;
          }
        }
        
        function getInsertedAllowed(nextBtn) {
          try {
            if (nextBtn.classList.contains("notInsert")) {
              return "false";
            }
            return "true";
          } catch {
            (err) => {
              console.log(err);
            };
          }
        }
    
        function getQueryPostData() {
          try {
            let [query_link, project_id, locale, query_code] =
              getProjectLink_Id_Locale_Querycode();
            let project_type = getProjectType(project_id);
            let searchDateLocation = getSearchDateLocation(project_type);
            let query_text = getQueryText(project_type);
            let grader_ans = getAnswer(project_type);
            let grader = getGrader();
            let results = getResults(project_type);
            let data = {
              searchDateLocation: searchDateLocation,
              query_text: query_text,
              query_link: query_link,
              grader_ans: grader_ans,
              grader: grader,
              project_id: project_id,
              locale: locale,
              query_code: query_code,
              results: results,
            };
            return data;
          } catch {
            (err) => {
              console.log(err);
            };
          }
        }
        
        return getQueryPostData();
    
    """,
    "sbs": ""
}

GET_SEARCH_DATE_COMMAND = {
    "standard": """
        const re_date = /from (.+?)\./;
        return document.querySelector(".message.blue").querySelector("p").firstChild.textContent.match(re_date)[1]
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
    "sbs": """
        let timeWas = new Date();
        let timeoutMs = 5000;
        const interval = setInterval(() => {
          try {
            if (document.querySelector(".utterance")) {
              document.querySelector(".utterance").scrollIntoView();
              clearInterval(interval);
            } else if (new Date() - timeWas > timeoutMs) {
              clearInterval(interval);
            }
          } catch {}
        }, 50);
    """
}

CLICK_START_PRJ_COMMAND = """
    let timeWas = new Date();
    let timeoutMs = +'%s';
    const interval = setInterval(() => {
      try {
        let locale_els = document
          .querySelector(".selection")
          .querySelector(".menu")
          .querySelectorAll("div");
        if (locale_els.length > 0) {
          locale_els.forEach((el) => {
            if (el.dataset.value === "%s") {
              el.click();
              document.querySelector("#start").click();
              clearInterval(interval);
            }
          });
        }
        if (new Date() - timeWas > timeoutMs) {
          clearInterval(interval);
        }
      } catch {}
    }, 100);
"""

GET_CHEAT_QUERY_CODE = """
    function get_all_query_code_inPage() {
      const query_codes = [...document.querySelectorAll("#request-wrapper")].map(
        (request) => {
          const query_code_text = request.querySelector("#request-id").innerText;
          const rg = /[a-zA-Z0-9]+/;
          const result = query_code_text.match(rg);
          if (result) {
            return result[0];
          }
        }
      );
      return query_codes;
    }
    return get_all_query_code_inPage()
"""

GET_CHEAT_QUERY_TEXT = """
    function get_query_text() {
      return [...document.querySelectorAll("#description-field")].map((el) => {
        return el.innerText;
      });
    }
    return get_query_text()
"""

GET_CHEAT_PROJECT_NAME = """
    function get_project_name() {
      return document.querySelector(".title-bar").innerText;
    }
    return get_project_name();
"""

GET_CHEAT_PROJECT_ID = """
    function get_project_id() {
      const link = window.location["href"];
      const rg = /\/project\/(\S+?)\//;
      const result = link.match(rg);
      if (result) {
        return result[1];
      }
    }
    return get_project_id();
"""

WAIT_PRJECT_SEARCH_BAR = """
    function checkPrjSearchBar(timeoutMs) {
      let timeWas = new Date();
      const interval = setInterval(() => {
        let barEl = document.getElementById('workflows-header-search-input');
        if (barEl) {
          clearInterval(interval);
          return barEl;
        }
        if (new Date() - timeWas > timeoutMs) {
          clearInterval(interval);
          return false;
        }
      }, 500);
    }
    let timeoutMs = +'%s';
    let barEl = checkPrjSearchBar(timeoutMs); // find until 5s
    return barEl;
"""

CHECK_SEARCH_BAR_READY = """
    function checkPrjSearchBar(timeoutMs) {
      let timeWas = new Date();
      let ready = false;
      while (!ready) {
        // search bar found
        if (document.getElementById('workflows-header-search-input')) {
          ready = true;
        }
        if (new Date() - timeWas > timeoutMs) {
          ready = false;
          break;
        }
      }
      return ready;
    }
    let timeoutMs = +'%s';
    return checkPrjSearchBar(timeoutMs);
"""
ENTER_PRJ_NAME = """
    function enterPrjName(prjName) {
      document.getElementById('workflows-header-search-input').value = prjName;
      // fire the change event
      let event = new Event('change');
      document.getElementById('workflows-header-search-input').dispatchEvent(event);
      // console.log('event dispatch');
    }
    let prjName = '%s';
    enterPrjName(prjName);
"""

FIND_PRJLINK_BY_NAME = """
    // https://stackoverflow.com/questions/11055530/wait-until-setinterval-is-done
    function getPrjLink(prjName, timeoutMs) {
      return new Promise((resolve, reject) => {
        let link;
        let timeWas = new Date();
        const prjLinkInterval = setInterval(() => {
          let noResultEl =
            document.getElementsByClassName('projects__no-results').length > 0
              ? true
              : false;
          let resultFoundPrjName = document
            .querySelector('.projects-table')
            ?.querySelector('a')
            ?.innerText.trim();
          // found result
          if (resultFoundPrjName === prjName) {
            link = document
              .querySelector('.projects-table')
              .querySelector('a').href;
            clearInterval(prjLinkInterval);
            resolve(link);
          }
          // no result search
          if (noResultEl) {
            console.log('no result');
            clearInterval(prjLinkInterval);
            reject(link);
          }
          if (new Date() - timeWas > timeoutMs) {
            console.log('timeout');
            clearInterval(prjLinkInterval);
            reject(link);
          }
        }, 200);
      });
    }
    let prjName = '%s';
    let timeoutMs = +'%s';
    return getPrjLink(prjName, timeoutMs).then((link) => {
        return link;
      })
      .catch(() => {
        return false;
      });
"""


# --------------------------------- MESSAGE ------------------------------ #
class bcolor:
    WARNING = '\u001b[38;5;196m{}\u001b[0m'
    OKGREEN = '\u001b[38;5;40m{}\u001b[0m'
    BLINK = '\u001b[5;30;43m{}\u001b[0m'
    STAR = '**{}**'
MESSAGE_DUE_DATE_MESSAGE =                              bcolor.WARNING.format("Due date alert.")
MESSAGE_WRONG_ANS =                                     bcolor.WARNING.format("Wrong ans.")
MESSAGE_NO_PROJECT_CODE_IN_STANDARD_PROJECT_TYPE =      bcolor.WARNING.format("No project code in standard project type.")
MESSAGE_WRONG_LEN_ANS =                                 bcolor.WARNING.format("Wrong length of answer.")
MESSAGE_COMMENTS_NEEDED =                               bcolor.WARNING.format("Comments needed.")
MESSAGE_NO_PROJECT_TYPE_SET =                           bcolor.WARNING.format("Project type not setup correctly.")
MESSAGE_BASE_COMMAND_ERROR =                            bcolor.WARNING.format("Error on '{}', please operating manually.")
MESSAGE_PERMISSION_DENIED =                             bcolor.WARNING.format("Permission denied or try again later.")
MESSAGE_INVALID_GRADING_PAGE =                          bcolor.WARNING.format("Invalid grading in this page.")
MESSAGE_PROJECT_TYPE_NOT_FOUND_IN_RENEW =               bcolor.WARNING.format("project type in renew function not set yet")
MESSAGE_TIMEOUT =                                       bcolor.WARNING.format("Time Out")
MESSAGE_NO_FINISHED_POP =                               bcolor.WARNING.format("No Finished Pop-up")
MESSAGE_NOT_SUCCESS =                                   bcolor.WARNING.format("Unsuccessful.")
MESSAGE_CLOSE_TAGS_ERROR =                              bcolor.WARNING.format("Close tags error, reopen...")
MESSAGE_CANCEL =                                        bcolor.OKGREEN.format("Cancelled.")
MESSAGE_NO_CONFLICT =                                   bcolor.OKGREEN.format("No Conflict")
MESSAGE_SUCCESS =                                       bcolor.OKGREEN.format("Successful.")
MESSAGE_ERROR_PAGE_SENT =                               "{}({})\n {}.".format({}, {}, bcolor.OKGREEN.format('Error Page Sent'))
MESSAGE_PROMOTE_MESSAGE =                               f"\n\n************************\n  PLAN A: $249/1m (STANDARD)\n  PLAN B: $598/3m {bcolor.BLINK.format('(20% OFF)')}\n  {bcolor.OKGREEN.format('-pay')}\n************************\n\n"

MESSAGE_OPENING_PRJ =                                   "Opening the project ... "
MESSAGE_LOADING =                                       "Loading..."
MESSAGE_DELAY =                                         "Delay..."
MESSAGE_FINDING_ANS_DELAY =                             "Finding Ans Delay ... Max: {}"
MESSAGE_INPUT_MANUALLY =                                "Please input manually."
MESSAGE_AUTO_NOT_ALLOWED =                              "This project not allowed to auto."
MESSAGE_NOT_FOUND =                                     "Not Found!"
MESSAGE_LIMIT_REACHED =                                 "Limit Reached."


# --------------------------------- HELPER ------------------------------ #
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
    "Control Command": {
        "-q": "quit program",
        "-p": "update and show project menu",
        "-done": "set done counter manually",
        "-t": "set delay time (seconds)",
        "-md": "activate timer",
        "-nd": "de-activate timer",
        "-alarm": "sound on",
        "-nalarm": "sound off",
        "-report/-re": "access the report page",
        "-text": "print the summary of report"
    },
    "sbs": {
        "`": "Web Search",
        "!": "Close Tabs",
        "a": "\n  left is better\n  then [SPACE] to write comment\n  number of 'a' means how much better, maximun is 3 times",
        "d": "\n  right is better\n  then [SPACE] to write comment\n  number of 'd' means how much better, maximun is 3 times",
        "w": "\n  about the same\n  then [SPACE] to write comment",
        "s": "\n  They are identical",
        "1": "I need more context on this request (e.g., previous request)",
        "2": "The request was gibberish or incomplete",
        "3": "Siri's response was missing or had display error",
        "4": "Some other reason (fill out comment box)\n  then [SPACE] to write comment",
        "example A": "aaa Left is much better because ... ",
        "example B": "dd Right is better because ... ",
        "example C": "w They are about the same because ... ",
        "example D": "4 They are inappropriate ... ",
        "example E": "s",
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

cheat_sheet = set()

sbsSent = {} # storage of usually used sentence for SBS project