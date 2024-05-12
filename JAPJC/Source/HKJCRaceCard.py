import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class HKJCRaceCard:
    def __init__(self, rc, course, db_cursor):
        self.db_cursor = db_cursor
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.url_prefix = 'https://racing.hkjc.com/racing/information/Chinese/racing/RaceCard.aspx?'
        self.race_date_short = rc.strftime("%Y-%m-%d")
        self.race_date = str(rc.strftime("%Y")) + "/" + str(rc.strftime("%m")) + "/" + str(rc.strftime("%d"))
        self.race_date_url = "RaceDate=" + self.race_date
        self.race_course = course
        self.race_course_url = "&Racecourse=" + course
        self.url = None
        self.soup = None
        self.race_details = None
        self.race_card_table = None

    def process(self):
        for i in range(20):
            num = i + 1
            self.open_race_card(race_no=num)
            try:
                self.get_race_card(race_no=num)
            except ValueError:
                break
        self.driver.quit()

    def open_race_card(self, race_no):
        self.url = self.url_prefix + self.race_date_url + self.race_course_url + "&RaceNo=" + str(race_no)
        self.driver.get(self.url)
        sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def get_race_card(self, race_no):
        if self.db_cursor.check_card(target_date=self.race_date_short, race_num=race_no) == 0:
            self.race_details = str(self.soup.find("div", {"class": "f_fs13"})).split('<br/>')
            if len(self.race_details) >= 4:
                print(self.race_date_short + ' ' +
                      self.race_details[1].split(',')[-1].lstrip(),
                      self.race_details[2].split(',')[-1].lstrip().rstrip("米"),
                      self.race_details[3].split(',')[-1].lstrip().rstrip("</div>"))
            self.race_card_table = self.soup.find("table", {"class": "starter f_tac f_fs13 draggable hiddenable"})
            result_df = pd.read_html(StringIO(str(self.race_card_table)))[0].fillna('')
            result_df.insert(0, column="RaceNo", value=f'{race_no}')
            result_df.insert(0, column="Date", value=f'{self.race_date_short}')
            self.db_cursor.import_data(data_format='df', data_type='card', data=result_df)
