from zipfile import ZipFile
import config
import os
import csv
import threading

def get_required_file_name_startWith(path, startwith):
    for filename in os.listdir(path):
        root, _ = os.path.splitext(filename)
        if root.startswith(startwith):
            return filename

def get_driver_download_link(executable_path):
    extract_path = os.path.split(executable_path)[0]  # '../driver'

    # get the current chrome version: '93.0.4577.63'
    chrome_version = os.popen('/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version').read().split(' ')[2]

    # extract the required version text: '93.0.4577'
    version_text = '.'.join(chrome_version.split('.')[0:-1])

    # download the file which contain the required version number for download
    os.system("cd {}; curl -O https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}".format(extract_path, version_text))

    # get the available version from file then delete the file after usage
    file_name = get_required_file_name_startWith(extract_path, 'LATEST_RELEASE')
    f = open(os.path.join(extract_path, file_name), 'r')
    available_version = f.read()
    f.close()
    os.system('rm {}/{}'.format(extract_path, file_name))

    # required download link
    download_link = "https://chromedriver.storage.googleapis.com/{}/chromedriver_mac64.zip".format(available_version)
    return download_link

def download_driver(executable_path):   # '../driver/chromedriver'
    download_link = get_driver_download_link(executable_path)
    extract_path = os.path.split(executable_path)[0] # '../driver'
    os.system("cd {}; curl -O {}".format(extract_path, download_link))
    zf = ZipFile('{}/chromedriver_mac64.zip'.format(extract_path), 'r')
    zf.extractall(extract_path)
    zf.close()
    os.system('rm {}/chromedriver_mac64.zip'.format(extract_path))

def show_img(path):
    os.system('open {}'.format(path))

def openFile(path, fileName):
    fullPath = os.path.join(path, fileName)
    with open(fullPath, 'w+'): # create file
        pass
    os.system('open -e {}'.format(fullPath))

def read_cheat_sheet(path, file_name):
    config.cheat_sheet = set()
    total_line = 0
    with open(os.path.join(path, file_name), 'r') as f:
        reader = csv.reader(f)
        for (query_text, _, project_id, query_code) in reader:
            config.cheat_sheet.add((query_text, project_id, query_code))
            total_line += 1
    print("Total read: {}".format(total_line))
    print("Local: {}".format(len(config.cheat_sheet)))

def output_cheat_sheet(path, file_name):
    # read the MAC cheatsheet if existed
    if (os.path.isfile(os.path.join(path, file_name))):
        read_cheat_sheet(path, file_name)
        os.remove(os.path.join(path, file_name))
        print("Removed file: {}".format(file_name))
    URL = "https://crowdcollect2.siri.apple.com/main/project/{}/browsing/s/{}/r/{}"
    total_line = 0
    with open(os.path.join(path, file_name), 'a') as f:
        writer = csv.writer(f)
        # loop for files
        for (query_text, project_id, query_code) in config.cheat_sheet:
            url = URL.format(project_id, query_code, query_code)
            writer.writerow([query_text, url, project_id, query_code])
            total_line += 1
        f.close()
    print("Total write: {}".format(total_line))
    config.cheat_sheet = set()
    print("Local cleaned")

def thread_start(fn, *args):
    thread = threading.Thread(target=fn, args=args)
    thread.start()