from ..views.prints import *

def output_popular_ans_dist(ans_dist):
    ans_dist_text = ''
    for number, value in ans_dist.items():
        ans_dist_text += "Result" + str(number) + ':\t'
        for ans, freq in value.items():
            ans_dist_text += ans + ':' + str(freq) + '\t'
        ans_dist_text += '\n'
    return ans_dist_text

def output_popular_detail(detail):
    grader_list_text = ''
    for grader_name, value in detail.items():
        grader_list_text += "{:<30} {:<4} {:<40}\n".format(grader_name, value['ans'], str(value["time"]))
    grader_list_text += '\n'
    return grader_list_text