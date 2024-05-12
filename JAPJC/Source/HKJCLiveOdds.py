import datetime as dt
import logging
import pandas as pd
from sys import platform
from io import StringIO
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class HKJCLiveOdds:
    def __init__(self, rc, course, db_cursor):
        if platform == "linux" or platform == "linux2":
            logging.basicConfig(filename='/home/ubuntu/Lambda/log/Lambda.log', encoding='utf-8', level='ERROR')
        elif platform == "win32" or platform == "win":
            logging.basicConfig(filename='lambda.log', encoding='utf-8')
        self.db_cursor = db_cursor
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(120)
        self.url_prefix = 'https://bet.hkjc.com/racing/pages/odds_wp.aspx?lang=ch&'
        self.race_date_short = rc.strftime("%Y-%m-%d")
        self.race_date = str(rc.strftime("%Y")) + "-" + str(rc.strftime("%m")) + "-" + str(rc.strftime("%d"))
        self.race_date_url = "date=" + str(self.race_date)
        self.race_course = str(course)
        self.race_course_url = "&venue=" + str(self.race_course)
        self.url = None
        self.soup = None
        self.server_time = None
        self.race_card_table = None

    def process(self, race_num):
        for i in range(race_num):
            num = i + 1
            self.open_live_odds(race_no=num)
            self.get_live_odds(race_no=num)
            self.soup = None
        self.driver.quit()

    def open_live_odds(self, race_no):
        self.url = self.url_prefix + self.race_date_url + self.race_course_url + "&raceno=" + str(race_no)
        self.driver.get(self.url)
        while self.soup is None:
            sleep(2)
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            if self.soup.find("table", {"id": "horseTable"}) is None:
                self.soup = None
                self.driver.get(self.url)
                sleep(3)

    def get_live_odds(self, race_no):
        try:
            if dt.datetime.now().astimezone().utcoffset() == dt.timedelta(hours=8):
                current_datetime = dt.datetime.today()
                current_date = dt.date.today()
            else:
                current_datetime = (dt.datetime.today()
                                    - dt.datetime.now().astimezone().utcoffset()
                                    + dt.timedelta(hours=8))
                current_date = current_datetime.date()
            self.server_time = dt.datetime.combine(
                current_date, dt.datetime.strptime(
                    self.soup.find("span", {"id": "oddsRefreshTime"}).get_text(), '%H:%M'
                ).time()
            )
            if abs(self.server_time - current_datetime) > dt.timedelta(minutes=15):
                self.server_time -= dt.timedelta(days=1)
            if self.db_cursor.get_last_odds_time(
                    race_date=self.race_date_short, server_time=self.server_time, race_num=race_no) == 0:
                print("Getting Race " + str(race_no) + " Odds at " + self.server_time.strftime('%Y-%m-%d %H:%M:%S'))
                self.race_card_table = self.soup.find("table", {"id": "horseTable"})
                result_df = pd.read_html(StringIO(str(self.race_card_table)))[0].fillna('').iloc[:-1, :]
                result_df.insert(0, column="RaceNo", value=f'{race_no}')
                result_df.insert(0, column="Time", value=f'{self.server_time}')
                result_df.insert(0, column="Date", value=f'{self.race_date_short}')
                self.db_cursor.import_data(data_format='df', data_type='jcodds', data=result_df)
            else:
                print("Race " + str(race_no) + " Odds at " +
                      self.server_time.strftime('%Y-%m-%d %H:%M:%S') + "already exist!")
        except ValueError as e:
            logging.error(e)
            self.driver.quit()
            exit()
