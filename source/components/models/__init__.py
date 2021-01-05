from sqlalchemy import Column, Integer, JSON, Table, MetaData

metadata = MetaData()

StockAnalytics = Table('stock_analytics', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('data', JSON))

DailyResult = Table('daily_result', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('data', JSON))

Stock = Table('stock', metadata,
              Column('id', Integer, primary_key=True),
              Column('data', JSON))

Portfolio = Table('portfolio', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('data', JSON))
