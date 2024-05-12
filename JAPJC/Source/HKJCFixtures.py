import datetime
import os
import sys
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service


class HKJCFixtures:
    def __init__(self, today_date, db_cursor):
        self.db_cursor = db_cursor
        self.alt = ""
        self.ft_date = ""
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.horse_url_prefix = 'https://racing.hkjc.com/racing/information/Chinese/Racing/Fixture.aspx?'
        self.today = today_date
        self.year = self.today.year
        self.month = self.today.strftime("%m")
        self.yearmonth = str(self.year) + str(self.month)
        self.url = self.horse_url_prefix + 'CalYear=' + str(self.year) + '&CalMonth=' + self.month
        self.soup = None
        self.fixture_table1 = None
        self.fixture_table2 = None

    def process(self):
        self.open_fixture(url=self.url)
        self.get_fixture(year=self.year, month=self.month)
        self.driver.quit()

    def open_fixture(self, url):
        self.soup = None
        while self.soup is None:
            try:
                self.driver.get(url)
                sleep(2)
                self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            except TimeoutException:
                sys.stdout.write('Timeout ')
            except Exception as e:
                sys.stdout.write(str(e) + ' ')

    def get_fixture(self, year, month):
        try:
            self.fixture_table1 = self.soup.find_all("span", {"class": "f_fl f_fs14"})
            self.fixture_table2 = self.soup.find_all("span", {"class": "f_fr"})
            for tag in self.fixture_table2:
                for tag2 in tag.find_all("img"):
                    self.alt = self.alt + tag2['alt'] + " "
                self.alt = self.alt.rstrip()
                self.alt = self.alt + ","
            self.alt = self.alt.rstrip(",")
            result1 = self.alt.split(",")
            for tag in self.fixture_table1:
                self.ft_date = self.ft_date + str(datetime.datetime(int(year), int(month), int(tag.string))) + ","
            self.ft_date = self.ft_date.rstrip(",")
            result2 = self.ft_date.split(",")
            data_row = list(zip(result2, result1))
            for row in data_row:
                self.db_cursor.import_data(data_format='row', data_type='fixtures', data=row)
            self.alt = ""
            self.ft_date = ""
        except ValueError as e:
            print(e)
