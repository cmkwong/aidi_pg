def print_report(report):
    print("\n{:>96}\n".format("-*-*-*-*-*-*-*-*-*- Summary *-*-*-*-*-*-*-*-*-*-*-*-"))
    print("{:>60}{:>12}{:>12}{:>12}\n".format("Project Name", "Done", "WH", "BH"))
    TD, TWH, TBH = 0,0.0,0.0
    for key, value in report.items():
        TD = TD + value[0]
        TWH = TWH + value[1]
        TBH = TBH + value[2]
        print("{:>60}{:>12}{:>12}{:>12}".format(key, value[0], value[1], value[2]))
    print("\n{:>96}".format("===================================================="))
    print("{:>60}{:>12}{:>12}{:>12}".format("Total:", str(TD), "{:.1f}".format(TWH), "{:.1f}".format(TBH)))