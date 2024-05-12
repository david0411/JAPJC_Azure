import logging
import datetime as dt
from sys import platform
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class HKJCLivePool:
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
        self.url_prefix = 'https://bet.hkjc.com/racing/pages/odds_turnover.aspx?lang=ch&'
        self.race_date_short = str(rc.strftime("%Y")) + str(rc.strftime("%m")) + str(rc.strftime("%d"))
        self.race_date = str(rc.strftime("%Y")) + "-" + str(rc.strftime("%m")) + "-" + str(rc.strftime("%d"))
        self.race_date_url = "date=" + str(self.race_date)
        self.race_course = str(course)
        self.race_course_url = "&venue=" + str(self.race_course)
        self.url = None
        self.soup = None
        self.server_time = None
        self.pool2win = None
        self.pool2pla = None
        self.pool2qin = None
        self.pool2qpl = None
        self.pool2fct = None
        self.pool2tce = None
        self.pool2tri = None
        self.pool2f_f = None
        self.pool2dbl = None
        self.pool2tbl = None
        self.pool2d_t = None
        self.pool2t_t = None
        self.pool26up = None

    def process(self, race_num):
        for i in range(race_num):
            num = i + 1
            self.open_live_pool(race_no=num)
            self.get_live_pool(race_no=num)
            self.soup = None
        self.driver.quit()

    def open_live_pool(self, race_no):
        self.url = self.url_prefix + self.race_date_url + self.race_course_url + "&raceno=" + str(race_no)
        self.driver.get(self.url)
        while self.soup is None:
            sleep(2)
            self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            if self.soup.find("span", {"id": "poolInvPoolTotWIN"}) is None:
                self.soup = None
                self.driver.get(self.url)
                sleep(3)

    def get_live_pool(self, race_no):
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
            if self.db_cursor.get_last_pool_time(
                    race_date=self.race_date_short, server_time=self.server_time, race_num=race_no) == 0:
                print("Getting Race " + str(race_no) + " Pool at " + self.server_time.strftime('%Y-%m-%d %H:%M:%S'))
                # 單場賽事彩池
                self.pool2win = (self.soup.find("span", {"id": "poolInvPoolTotWIN"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                self.pool2pla = (self.soup.find("span", {"id": "poolInvPoolTotPLA"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                self.pool2qin = (self.soup.find("span", {"id": "poolInvPoolTotQIN"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                self.pool2qpl = self.soup.find("span", {"id": "poolInvPoolTotQPL"})
                if self.pool2qpl is not None:
                    self.pool2qpl = (self.pool2qpl.get_text().lstrip("$ ").replace(",", ""))
                self.pool2fct = (self.soup.find("span", {"id": "poolInvPoolTotFCT"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                self.pool2tce = (self.soup.find("span", {"id": "poolInvPoolTotTCE"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                self.pool2tri = (self.soup.find("span", {"id": "poolInvPoolTotTRI"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                self.pool2f_f = (self.soup.find("span", {"id": "poolInvPoolTotF-F"}).
                                 get_text().lstrip("$ ").replace(",", ""))
                # 多場賽事彩池
                self.pool2dbl = self.soup.find("span", {"id": "poolInvPoolTotDBL"})
                if self.pool2dbl is not None:
                    self.pool2dbl = self.pool2dbl.get_text().lstrip("$ ").replace(",", "")
                self.pool2tbl = self.soup.find("span", {"id": "poolInvPoolTotTBL"})
                if self.pool2tbl is not None:
                    self.pool2tbl = self.pool2tbl.get_text().lstrip("$ ").replace(",", "")
                self.pool2d_t = self.soup.find("span", {"id": "poolInvPoolTotD-T"})
                if self.pool2d_t is not None:
                    self.pool2d_t = self.pool2d_t.get_text().lstrip("$ ").replace(",", "")
                self.pool2t_t = self.soup.find("span", {"id": "poolInvPoolTotT-T"})
                if self.pool2t_t is not None:
                    self.pool2t_t = self.pool2t_t.get_text().lstrip("$ ").replace(",", "")
                self.pool26up = self.soup.find("span", {"id": "poolInvPoolTot6UP"})
                if self.pool26up is not None:
                    self.pool26up = self.pool26up.get_text().lstrip("$ ").replace(",", "")
                data_row = [self.race_date, race_no, self.server_time,
                            self.pool2win, self.pool2pla, self.pool2qin, self.pool2qpl,
                            self.pool2fct, self.pool2tce, self.pool2tri, self.pool2f_f,
                            self.pool2dbl, self.pool2tbl, self.pool2d_t, self.pool2t_t,
                            self.pool26up]
                self.db_cursor.import_data(data_format='row', data_type='jcpool', data=data_row)
            else:
                print("Race " + str(race_no) + " Pool at " +
                      self.server_time.strftime('%Y-%m-%d %H:%M:%S') + "already exist!")
        except ValueError as e:
            logging.error(e)
            self.driver.quit()
            exit()
