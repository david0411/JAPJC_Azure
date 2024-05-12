import logging
import sys
import psutil
import pathlib
import datetime as dt
from sys import platform
from DBConnectionAzure import DBConnectionAzure
from HKJCFixtures import HKJCFixtures
from HKJCHorseList import HKJCHorseList
from HKJCHorseScraper import HKJCHorseScraper
from HKJCLiveOdds import HKJCLiveOdds
from HKJCLivePool import HKJCLivePool
from HKJCRaceCard import HKJCRaceCard
from HKJCRacingResultScraper import HKJCRacingResultScraper
from HKJCTrainerScraper import HKJCTrainerScraper
# from CreateSchedule import CreateSchedule


def get_next_month(target_date):
    if target_date.month == 12:
        return dt.date(target_date.year + 1, 1, 1)
    else:
        return dt.date(target_date.year, target_date.month + 1, 1)


def scrap_fixture(forced):
    if latest_fixture is None:
        temp_date = fixture_start_date
    else:
        temp_date = latest_fixture
    if forced:
        db_connection.delete_fixture(temp_date)
    while temp_date < get_next_month(current_time.date()):
        if temp_date.month != 8:
            temp_date = get_next_month(temp_date)
            fixture_scraper = HKJCFixtures(today_date=temp_date, db_cursor=db_connection)
            fixture_scraper.process()


def scrap_result(target_date, current_date):
    date_list = db_connection.get_next_rd2(target_date=target_date)
    result_scraper = HKJCRacingResultScraper(db_cursor=db_connection)
    for date in date_list:
        if date <= current_date:
            no_of_race2 = db_connection.get_race_num2(date)
            result_scraper.process(race_date=date, race_course=db_connection.get_next_venue2(date), race_num=no_of_race2)


def reset_action():
    if len(sys.argv) > 1:
        return '0'
    else:
        return None


if __name__ == '__main__':
    if platform == "linux" or platform == "linux2":
        logging.basicConfig(filename='/home/ubuntu/Lambda/log/Lambda.log', encoding='utf-8', level='ERROR')
    elif platform == "win32" or platform == "win":
        logging.basicConfig(filename='Lambda.log', encoding='utf-8')
    # Initialize
    action = None
    next_rd = None
    next_rd_date = None
    next_rd_venue = None
    next_rd_course = None
    current_time = None
    fixture_start_date = dt.date(2020, 1, 1)
    result_start_date = dt.date(2020, 1, 1)
    if len(sys.argv) > 1:
        action = str(sys.argv[1])
    # must include
    db_connection = DBConnectionAzure()
    next_rd = db_connection.get_next_rd()
    if dt.datetime.now().astimezone().utcoffset() == dt.timedelta(hours=8):
        current_time = dt.datetime.now()
    else:
        current_time = (dt.datetime.now()
                        - dt.datetime.now().astimezone().utcoffset()
                        + dt.timedelta(hours=8))
    if next_rd is None:
        print('No Race Data Found')
    else:
        next_rd_date, *temp, next_rd_venue = next_rd
        next_rd_course = str(next_rd_venue).split(' ')[0]
        print('Current Time: ' + current_time.strftime('%Y-%m-%d %H:%M:%S') +
              ' Memory Usage: ' + str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total) +
              ' Next Race Date: ' + str(next_rd_date.strftime("%Y-%m-%d")) +
              ' Next Race Venue: ' + next_rd_venue)
    while action != '0':
        if action is None:
            action = input('1.更新馬匹賽績 2.更新賽期表 3.更新排位表 4.即時賠率&投注額 5.更新賽果 0.Quit\nInput: ')
        if action == '1':
            # 練馬師+馬匹列表
            trainer_scraper = HKJCTrainerScraper()
            horse_list_scraper = HKJCHorseList()
            horse_df = horse_list_scraper.process(trainer_url_list=trainer_scraper.process())
            # 馬匹賽績
            scraped_horse_list = db_connection.get_horse_list()
            for index, row in horse_df.iterrows():
                horse_url = row['URL']
                horse_id = horse_url[-4:]
                if horse_id not in scraped_horse_list:
                    sys.stdout.write('Processing ' + horse_id + ": ")
                    scraper = HKJCHorseScraper(url=horse_url, db_cursor=db_connection)
                    scraper.process()
            action = reset_action()
        elif action == '2':
            # 賽期表
            first_fixture = db_connection.get_first_fixture()
            latest_fixture = db_connection.get_last_fixture()
            if latest_fixture is None:
                print('No fixture data found, scraping from: ' + fixture_start_date.strftime("%Y/%m/%d"))
                scrap_fixture(0)
            else:
                print('Data found from ' + first_fixture.strftime("%Y/%m/%d") +
                      ' to ' + latest_fixture.strftime("%Y/%m/%d"))
                if len(sys.argv) > 2:
                    action_fixture = str(sys.argv[2])
                else:
                    action_fixture = input('Force update fixture: 1.Yes 2.No:\nInput: ')
                if action_fixture == '1':
                    scrap_fixture(1)
                else:
                    scrap_fixture(0)
            action = reset_action()
        elif action == '3':
            # 排位表
            if next_rd_date is not None and next_rd_course is not None:
                race_card_scraper = HKJCRaceCard(rc=next_rd_date, course=next_rd_course, db_cursor=db_connection)
                race_card_scraper.process()
            else:
                print("No next Race Data!")
            action = reset_action()
        elif action == '4':
            # 即時賠率+即時投注額
            no_of_race = db_connection.get_race_num()
            if next_rd_date is not None and next_rd_venue is not None:
                jcodds_scraper = HKJCLiveOdds(rc=next_rd_date, course=next_rd_course, db_cursor=db_connection)
                jcodds_scraper.process(race_num=no_of_race)
                jcpool_scraper = HKJCLivePool(rc=next_rd_date, course=next_rd_course, db_cursor=db_connection)
                jcpool_scraper.process(race_num=no_of_race)
            else:
                print("No next Race Data!")
            action = reset_action()
        elif action == '5':
            # 賽果
            first_race_result_date = db_connection.get_first_race_result_date()
            latest_race_result_date = db_connection.get_last_race_result_date()
            if latest_race_result_date is None:
                print('No result data found, scraping from: ' + result_start_date.strftime("%Y/%m/%d"))
                scrap_result(target_date=result_start_date,
                             current_date=current_time.date())
            elif latest_race_result_date < db_connection.get_prev_rd()[0]:
                print('Data found from ' + first_race_result_date.strftime("%Y/%m/%d") +
                      ' to ' + latest_race_result_date.strftime("%Y/%m/%d"))
                scrap_result(target_date=latest_race_result_date + dt.timedelta(days=1),
                             current_date=current_time.date())
            else:
                print('Data found from ' + first_race_result_date.strftime("%Y/%m/%d") +
                      ' to ' + latest_race_result_date.strftime("%Y/%m/%d") + '\n' +
                      'Data Completed')
            action = reset_action()
        elif action == '6':
            # Create Schedule
            # if platform == "linux" or platform == "linux2":
            #     logging.info('Create schedules')
            #     scheduler = CreateSchedule(last_rd_date=db_connection.get_prev_rd()[0],
            #                                next_rd_date=next_rd_date,
            #                                current_time=current_time)
            action = reset_action()
        elif action == '99':
            # Maintenance
            db_connection.delete_pool()
            db_connection.delete_odds()
            if platform == "linux" or platform == "linux2":
                remove_log = pathlib.Path("/home/ubuntu/Lambda/log/Lambda.log")
                remove_log.unlink(missing_ok=True)
            action = reset_action()
    db_connection.close_connection()
    logging.info('Done & Exit')
