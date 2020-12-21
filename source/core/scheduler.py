from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from source.app import start_analyze
from components.trade import start_trade


def schedule():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(start_analyze, 'cron', day_of_week='mon-fri', hour=9, minute=0)
    scheduler.add_job(start_trade, 'cron', day_of_week='mon-fri', hour=9, minute=59, second=58)
    scheduler.start()
    print('Press Ctrl+C to exit')
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    schedule()
