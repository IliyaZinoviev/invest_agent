from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from source.app import start_analyze
from components.trade import start_trade


def schedule():
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    # TODO add dynamic cron kwargs values
    scheduler.add_job(start_analyze, 'cron', day_of_week='mon-fri', hour='5-9')
    scheduler.add_job(start_trade, 'cron', day_of_week='mon-fri', hour='0-1,10-23', minute='0-59')
    scheduler.start()
    print('Press Ctrl+C to exit')
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    schedule()
