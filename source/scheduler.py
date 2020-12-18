from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from source.app import main


def schedule():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, 'cron', day_of_week='mon-fri', hour=9, minute=45)
    scheduler.start()
    print('Press Ctrl+C to exit')
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    schedule()
