import os
import sys

import selenium.webdriver.support.expected_conditions as EC

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *



DEFAULT_WAIT_TIME = 365 * 24 * 60 * 60  # 1 year


# https://selenium-python.readthedocs.io/api.html
# https://www.selenium.dev/documentation
class Browser:
    def __init__ (self, url=None):
        self.driver = None

        if url:
            self.open(url)

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self, url):
        if not self.driver:
            # https://selenium-python.readthedocs.io/api.html#selenium.webdriver.chrome.service.Service
            # service = ChromeService(executable_path=r'...')

            options = Options()
            options.page_load_strategy = 'eager'

            self.driver = Chrome(options=options)
            
        self.driver.get(url)

    def close (self):
        try:
            self.driver.close()  # close current window
            # self.driver.quit()  # quit browser
        except:
            pass

        self.driver = None

    def getUrl (self):
        try:
            return self.driver.current_url
        except:
            return None

    def getWindows (self):
        try:
            return self.driver.window_handles
        except:
            return None

    def isOpen (self):
        return bool(self.getWindows())

    # https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.support.wait
    # https://selenium-python.readthedocs.io/api.html#selenium.webdriver.support.expected_conditions.url_matches
    def waitUrl (self, pattern, timeout=DEFAULT_WAIT_TIME):
        if not self.driver:
            raise Exception('No driver')

        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.url_matches(pattern))
        except:
            pass

        return self.getUrl()



def _test_ ():
    with Browser('https://www.google.ru') as browser:
        response = browser.waitUrl(rf'\/search\?')

        # browser.close()

        print(response)



__all__ = [
    'Browser'
]



if __name__ == '__main__':
    _test_()
