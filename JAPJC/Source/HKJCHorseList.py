import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class HKJCHorseList:
    def __init__(self):
        self.horse_info_url_dict = {}
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.trainer_url_prefix = 'https://racing.hkjc.com/racing/information/Chinese/Horse/ListByStable.aspx?'
        self.trainer_url = None
        self.trainer_id = None
        self.soup = None

    def process(self, trainer_url_list):
        horse_info_url_list = []
        for trainer_url in trainer_url_list:
            self.trainer_url = trainer_url
            self.trainer_id = trainer_url.split('=')[-1]
            self.open_horse_info()
            self.get_horse_info()
        for key, values in self.horse_info_url_dict.items():
            for url in values:
                horse_info_url_list.append((key, url))
        return pd.DataFrame(horse_info_url_list, columns=['Trainer', 'URL'])

    def open_horse_info(self):
        self.driver.get(self.trainer_url_prefix + self.trainer_url)
        sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def get_horse_info(self):
        horse_info_table = self.soup.find("table", {"class": "bigborder"})
        self.horse_info_url_dict[self.trainer_id] = [x['href'] for x in horse_info_table.find_all('a')]
