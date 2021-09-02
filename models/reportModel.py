import os
from datetime import datetime

def print_report(report):
    print("\n{:>96}\n".format("-*-*-*-*-*-*-*-*-*- Summary *-*-*-*-*-*-*-*-*-*-*-*-"))
    print("{:>60}{:>12}{:>12}{:>12}{:>12}\n".format("Project Name", "Locale", "Done", "WH", "BH"))
    TD, TWH, TBH = 0,0.0,0.0
    for key, value in report.items():
        TD = TD + value[0]
        TWH = TWH + value[1]
        TBH = TBH + value[2]
        print("{:>60}{:>12}{:>12}{:>12}{:>12}".format(key[0], key[1], value[0], value[1], value[2]))
    print("\n{:>96}".format("===================================================="))
    print("{:>60}{:>12}{:>12}{:>12}{:>12}".format("Total:", str(len(report)), str(TD), "{:.1f}".format(TWH), "{:.1f}".format(TBH)))

def print_screen(web_controller, saved=False):
    web_controller.back_tag_one()
    saved_dir = 'clipboard'
    if saved:
        saved_dir = "~/Downloads/{}.png".format(datetime.now().strftime('Screenshot %Y-%m-%d at %I.%M.%S %p'))
        os.system('screencapture -R240,150,1193,660 {}'.format(saved_dir))
    else:
        os.system('screencapture -c -R240,150,1193,660')
    return saved_dir
