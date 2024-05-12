from crontab import CronTab
import datetime as dt


class CreateSchedule:
    def __init__(self, last_rd_date, next_rd_date, current_time):
        cron = CronTab(user='ubuntu')
        cron.remove_all()
        command1 = 'python3 /home/ubuntu/Lambda/main.py 6 >> /home/ubuntu/Lambda/log/Lambda.log 2>&1'
        job1 = cron.new(command=command1)
        job1.setall('0 0 * * *')
        if current_time.date() == next_rd_date - dt.timedelta(days=2):
            command2 = 'python3 /home/ubuntu/Lambda/main.py 3 >> /home/ubuntu/Lambda/log/Lambda.log 2>&1'
            job2 = cron.new(command=command2)
            job2.setall('0 1 * * *')
        if current_time.date() == next_rd_date - dt.timedelta(days=1):
            command2 = 'python3 /home/ubuntu/Lambda/main.py 3 >> /home/ubuntu/Lambda/log/Lambda.log 2>&1'
            job2 = cron.new(command=command2)
            job2.setall('0 1 * * *')
            command3 = 'python3 /home/ubuntu/Lambda/main.py 4 >> /home/ubuntu/Lambda/log/Lambda.log 2>&1'
            job3 = cron.new(command=command3)
            job3.setall('58,0,2,4 * * * *')
            command4 = 'python3 /home/ubuntu/Export/main.py >> /home/ubuntu/Export/log/Export.log 2>&1'
            job4 = cron.new(command=command4)
            job4.setall('30 23 * * *')
        if current_time.date() - dt.timedelta(days=1) == last_rd_date:
            command5 = 'python3 /home/ubuntu/Lambda/main.py 5 >> /home/ubuntu/Lambda/log/Lambda.log 2>&1'
            job5 = cron.new(command=command5)
            job5.setall('0 2 * * *')
            command6 = 'python3 /home/ubuntu/Lambda/main.py 99 >> /home/ubuntu/Lambda/log/Lambda.log 2>&1'
            job6 = cron.new(command=command6)
            job6.setall('5 2 * * *')
        cron.write()
