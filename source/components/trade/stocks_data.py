import json
from operator import itemgetter

from components.models import Stock
from core.config import config
from core.extentions import db_engine_provider


async def get_sorted_stocks() -> list:
    engine = db_engine_provider[0]
    async with engine.acquire() as conn:
        json_data = (await (await conn.execute(Stock.select(Stock.c.id == 1))).first())['data']
    stocks_data = json.loads(json_data)
    filtered_stocks_data = {k: v for k, v in stocks_data.items() if k in config.TICKERS}
    stock_data_list = list(map(lambda el: {**{'ticker': el[0]}, **el[1]}, filtered_stocks_data.items()))
    return sorted(stock_data_list, key=itemgetter('possible_profit'), reverse=True)
