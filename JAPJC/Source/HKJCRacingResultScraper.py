import sys
import pandas as pd
from io import StringIO
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service


class HKJCRacingResultScraper:
    def __init__(self, db_cursor):
        self.db_cursor = db_cursor
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.horse_url_prefix = 'https://racing.hkjc.com/racing/information/Chinese/Racing/LocalResults.aspx?'
        self.url = None
        self.soup = None
        self.race_tab = None
        self.performance_table = None

    def process(self, race_date, race_course, race_num):
        for i in range(race_num):
            self.open_race_info(race_date.strftime("%Y/%m/%d"), race_course, i + 1)
            self.get_race_tab(race_date.strftime("%Y-%m-%d"), i + 1)
            self.get_race_performance(race_date.strftime("%Y-%m-%d"), i + 1)
        self.driver.quit()

    def open_race_info(self, race_date, race_course, race_no):
        self.soup = None
        while self.soup is None:
            try:
                self.url = (self.horse_url_prefix + "RaceDate=" + race_date +
                            "&Racecourse=" + race_course + "&RaceNo=" + str(race_no))
                self.driver.get(self.url)
                sleep(2)
                self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            except TimeoutException:
                sys.stdout.write('Timeout ')
                continue
            except Exception as e:
                sys.stdout.write(str(e) + ' ')
                continue

    def get_race_tab(self, race_date, race_no):
        result = [race_date, race_no]
        time1 = False
        time2 = False
        time_list1 = []
        time_list2 = []
        time_list3 = []
        result.append(self.soup.find("tr", {"class": "bg_blue color_w font_wb"}).find("td").get_text())
        self.race_tab = self.soup.find("tbody", {"class": "f_fs13"}).find_all("td")
        for tag in self.race_tab:
            if len(tag.get_text().split(" - ")) > 1:
                result.append(tag.get_text().split(" - ")[0])
                if tag.get_text().split(" - ")[1].find('米') != -1:
                    result.append(tag.get_text().split(" - ")[1].rstrip().rstrip('米'))
                else:
                    result.append(tag.get_text().split(" - ")[1])
                continue
            if tag.get_text() == "時間 :":
                time1 = True
                continue
            if tag.get_text() == "分段時間 :":
                time1 = False
                time2 = True
                continue
            if tag.get_text().find(" :") != -1 or tag.get_text().find("$") != -1:
                continue
            if time1:
                while len(result) < 9:
                    result.append('')
                if tag.get_text() != '':
                    temp = tag.get_text().lstrip('(').rstrip(')')
                    if len(temp) < 6:
                        temp = '0:' + temp
                    time_list1.append(temp)
                continue
            if time2:
                temp = tag.get_text().replace('\n', '').replace('\xa0\xa0', ',').strip().split()
                if len(temp[0]) < 6:
                    temp[0] = '0:' + temp[0]
                time_list2.append(temp[0])
                if len(temp) > 1:
                    for data in temp[-1].split(','):
                        if len(data) < 6:
                            data = '0:' + data
                        time_list3.append(data)
                continue
            if tag.get_text() != '':
                result.append(tag.get_text().lstrip().rstrip())
        while len(time_list1) < 6:
            time_list1.append('0:00.00')
        while len(time_list2) < 6:
            time_list2.append('0:00.00')
        while len(time_list3) < 4:
            time_list3.append('0:00.00')
        for data in time_list1:
            result.append(data)
        for data in time_list2:
            result.append(data)
        for data in time_list3:
            result.append(data)
        print(result)
        self.db_cursor.import_data(data_format='row', data_type='result1', data=result)

    def get_race_performance(self, race_date, race_no):
        if self.soup.find("div", {"class": "performance"}) is not None:
            self.performance_table = (self.soup.find("div", {"class": "performance"}).
                                      find('table').prettify(formatter=lambda s: s.replace(u'\xa0', ' ')))
            result_df = pd.read_html(StringIO(str(self.performance_table)))[0].fillna('')
            result_df.insert(0, column="場次", value=f'{race_no}')
            result_df.insert(0, column="日期", value=f'{race_date}')
            self.db_cursor.import_data(data_format='df', data_type='result2', data=result_df)
