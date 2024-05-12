import subprocess
import azure.functions as func
import logging
import datetime as dt
from Source.DBConnectionAzure import DBConnectionAzure


app = func.FunctionApp()


@app.timer_trigger(schedule="0 12 * * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def card(myTimer: func.TimerRequest) -> None:
    next_rd_date = None
    current_time = dt.datetime.now()
    db_connection = DBConnectionAzure()
    next_rd = db_connection.get_next_rd()
    if next_rd is None:
        logging.info('No Race Data Found')
    else:
        next_rd_date, *temp, next_rd_venue = next_rd
    if current_time.date() == next_rd_date - dt.timedelta(days=2):
        script_args = ["3"]
        subprocess.run(["../.venv/Scripts/python.exe", "./Source/main.py"] + script_args)
    if current_time.date() == next_rd_date - dt.timedelta(days=1):
        script_args = ["3"]
        subprocess.run(["../.venv/Scripts/python.exe", "./Source/main.py"] + script_args)
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info('JAPJC Card executed.')
    db_connection.close_connection()


@app.timer_trigger(schedule="0 58,0,2,4 20-23 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def odds_pool(myTimer: func.TimerRequest) -> None:
    next_rd_date = None
    current_time = dt.datetime.now()
    db_connection = DBConnectionAzure()
    next_rd = db_connection.get_next_rd()
    if next_rd is None:
        logging.info('No Race Data Found')
    else:
        next_rd_date, *temp, next_rd_venue = next_rd
    if current_time.date() == next_rd_date - dt.timedelta(days=1):
        script_args = ["3"]
        subprocess.run(["../.venv/Scripts/python.exe", "./Source/main.py"] + script_args)
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info('JAPJC Card executed.')
    db_connection.close_connection()


@app.timer_trigger(schedule="0 58,0,2,4 0-9 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def odds_pool(myTimer: func.TimerRequest) -> None:
    next_rd_date = None
    current_time = dt.datetime.now()
    db_connection = DBConnectionAzure()
    next_rd = db_connection.get_next_rd()
    if next_rd is None:
        logging.info('No Race Data Found')
    else:
        next_rd_date, *temp, next_rd_venue = next_rd
    if current_time.date() == next_rd_date:
        script_args = ["3"]
        subprocess.run(["../.venv/Scripts/python.exe", "./Source/main.py"] + script_args)
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info('JAPJC Card executed.')
    db_connection.close_connection()


@app.timer_trigger(schedule="0 0 10 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def odds_pool(myTimer: func.TimerRequest) -> None:
    current_time = dt.datetime.now()
    db_connection = DBConnectionAzure()
    last_rd_date = db_connection.get_prev_rd()[0]
    if current_time.date() - dt.timedelta(days=1) == last_rd_date:
        script_args = ["5"]
        subprocess.run(["../.venv/Scripts/python.exe", "./Source/main.py"] + script_args)
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info('JAPJC Card executed.')
    db_connection.close_connection()


@app.timer_trigger(schedule="0 5 10 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def odds_pool(myTimer: func.TimerRequest) -> None:
    current_time = dt.datetime.now()
    db_connection = DBConnectionAzure()
    last_rd_date = db_connection.get_prev_rd()[0]
    if current_time.date() - dt.timedelta(days=1) == last_rd_date:
        script_args = ["99"]
        subprocess.run(["../.venv/Scripts/python.exe", "./Source/main.py"] + script_args)
    if myTimer.past_due:
        logging.info('The timer is past due!')
    logging.info('JAPJC Card executed.')
    db_connection.close_connection()
