from zipfile import ZipFile
import os

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
    os.remove(os.path.join(extract_path, file_name))

    # required download link
    download_link = "https://chromedriver.storage.googleapis.com/{}/chromedriver_mac64.zip".format(available_version)
    return download_link

def download_driver(executable_path):
    download_link = get_driver_download_link(executable_path)
    extract_path = os.path.split(executable_path)[0] # '../driver'
    os.system("cd {}; curl -O {}".format(extract_path, download_link))
    zf = ZipFile('{}/chromedriver_mac64.zip'.format(extract_path), 'r')
    zf.extractall(extract_path)
    zf.close()
    os.system('rm {}/chromedriver_mac64.zip'.format(extract_path))