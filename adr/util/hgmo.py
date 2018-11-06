from bs4 import BeautifulSoup

import requests
MOZILLA_CENTRAL_URL = "https://hg.mozilla.org/mozilla-central/file"


def get_directory_list(url=MOZILLA_CENTRAL_URL, list_hidden=False):
    """
    Return the list of all directories that live in mozilla-central
    :param url: link contains list of directories
    :param list_hidden: if True, include hidden directories
    :return: list of all directories that live in mozilla-central
    """
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    result = []

    for link in soup.find_all('a', href=True, text="files"):
        tmp = link.get("href").split("/")
        dir_name = tmp[len(tmp) - 1]
        if list_hidden or (dir_name[0] != "."):
            result.append("{}/".format(dir_name))

    return result
