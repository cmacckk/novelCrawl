""" Config file """

import platform

# Crawl novel HTTP request timeout
TIMEOUT = 5
DEFAULT_DOWNLOAD_PATH = './download/'
DEFAULT_DOWNLOAD_PATH_NAME = 'download'


BIGE7_BOOK_URL = 'https://www.bqg70.com/book/'

if platform.system() == 'Windows':
    CHROME_DRIVER_PATH = './driver/chromedriver.exe'
elif platform.system() == 'Linux':
    CHROME_DRIVER_PATH = './driver/chromedriver'
else:
    CHROME_DRIVER_PATH = './driver/chromedriver'

if platform.system() == 'Windows':
    CHROME_EXECUTABLE_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
elif platform.system() == 'Linux':
    CHROME_EXECUTABLE_PATH = '/usr/bin/google-chrome'
else:
    CHROME_EXECUTABLE_PATH = './driver/chromedriver'