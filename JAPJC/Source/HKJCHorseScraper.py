import sys
import pandas as pd
from io import StringIO
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service


class HKJCHorseScraper:
    def __init__(self, url, db_cursor):
        self.db_cursor = db_cursor
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(5)
        self.horse_url_prefix = 'https://racing.hkjc.com'
        self.horse_url_suffix = '&Option=1'
        self.url = self.horse_url_prefix + url + self.horse_url_suffix
        self.horse_id = url.split('_')[-1]
        self.soup = None
        self.horse_profile_table = None
        self.horse_info_table = None
        self.horse_name = None

    def process(self):
        self.open_horse_info()
        self.get_horse_info()
        self.driver.quit()

    def open_horse_info(self):
        while self.soup is None:
            try:
                self.driver.get(self.url)
                sleep(2)
                self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            except TimeoutException:
                pass
            except Exception as e:
                sys.stdout.write(str(e) + ' ')

    def get_horse_profile(self):
        self.horse_profile_table = self.soup.find("table", {"class": "horseProfile"})
        result_df = pd.read_html(StringIO(str(self.horse_profile_table)))[0]
        info_list = []
        for _, info_row in result_df.iterrows():
            if info_row.iloc[1] == ':':
                info_list.append((info_row.iloc[0], info_row.iloc[2]))

    def get_horse_info(self):
        try:
            self.horse_name = self.soup.find("title").getText().split(" - ")[0]
            self.db_cursor.import_data(data_format='row', data_type='horse', data=(self.horse_id, self.horse_name))
            self.horse_info_table = self.soup.find("table", {"class": "bigborder"})
            result_df = pd.read_html(StringIO(str(self.horse_info_table)))[0].fillna('')
            result_df.insert(0, column="horse_id", value=f'{self.horse_id}')
            self.db_cursor.import_data(data_format='horse_result', data_type='horse_result', data=result_df)
            print('Done')
        except Exception as e:
            print(e)
