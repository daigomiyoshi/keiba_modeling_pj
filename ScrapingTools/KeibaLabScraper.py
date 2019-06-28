# import glob
# import os
# import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class KeibaLabScraper(object):

    def __init__(self, driver, parameters):
        self.driver = driver
        self.parameters = parameters

    def load_target_url_page(self, target_datetime_str):
        target_url = self.parameters['TARGET_URL'] + target_datetime_str

        try:
            self.driver.get(target_url)
            print('We can load the URL:', self.driver.current_url)
        except:
            print("The page load was time out")


