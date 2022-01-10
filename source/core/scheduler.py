import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from components.trade import start_trade
from pytz import timezone

from source.app import start_analyze


def is_appropriate_time():
    now = datetime.now(tz=timezone('Europe/Moscow'))
    w = now.weekday()
    h = now.hour
    m = now.minute
    night_interval_time = h == 0 or (h == 1 and m < 45)
    return (w < 5 and (h > 10 or night_interval_time)) or (w == 6 and night_interval_time)


def schedule():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(start_analyze, 'cron', day_of_week='mon-fri', hour='4')
    scheduler.add_job(start_trade, 'cron', day_of_week='mon-fri', hour='10')
    scheduler.start()
    print('Press Ctrl+C to exit')
    try:
        loop = asyncio.get_event_loop()
        if is_appropriate_time():
            loop.run_until_complete(start_trade())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    schedule()
