from crontab import CronTab
# python3 /home/binance/stock-navigator/test_job.py
'''
Инструкции по использованию CronTab
https://pypi.org/project/python-crontab/
'''

# кронтаб текущего юзера
cron = CronTab(user=True)
# отчистка кронтаба
cron.remove_all()

# past
daily = cron.new(command="python3 ~/parse_future.py")
daily.setall("0 5 * * *")

# future
monthly = cron.new(command="python3 ~/parse_future.py")
monthly.setall("0 6 1 * *")


cron.write()

for item in cron:
    print(item)
