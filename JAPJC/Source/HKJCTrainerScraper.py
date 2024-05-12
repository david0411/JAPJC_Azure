from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class HKJCTrainerScraper:
    def __init__(self):
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.url = 'https://racing.hkjc.com/racing/information/Chinese/Trainers/TrainerRanking.aspx'
        self.soup = None

    def process(self):
        self.open_trainer_info()
        return self.get_trainer_info()

    def open_trainer_info(self):
        self.driver.get(self.url)
        sleep(2)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def get_trainer_info(self):
        trainer_table = self.soup.find("tbody", {"class": "f_fs12"})
        return [x['href'].split('?')[-1].split('&')[0] for x in trainer_table.find_all('a')]
