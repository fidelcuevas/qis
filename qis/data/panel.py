import pandas as pd
from functools import lru_cache
from qis.core import Core


class Panel(Core):
    
    @classmethod
    @lru_cache(maxsize=16)
    def ohlc(cls, tickers: tuple = None, sd: str = None, ed: str = None):
        # """
        # :tickers list:
        # :sd str:
        # :ed str:
        # """
        # d = super()._ohlc(tickers=tickers, sd=sd, ed=ed)
        # return d.drop('date', axis=1).groupby(['ticker']).agg('mean')
        raise NotImplementedError('Feature is in development.')

    @classmethod
    @lru_cache(maxsize=16)
    def fundamental(cls, tickers: tuple = None, sd: str = None, ed: str = None):
        # """
        # :tickers list:
        # :sd str:
        # :ed str:
        # """
        # d = super()._fundamental(tickers=tickers, sd=sd, ed=ed)
        # return d.drop('datekey', axis=1).groupby(['ticker']).agg('mean')
        raise NotImplementedError('Feature is in development.')

    @classmethod
    @lru_cache(maxsize=16)
    def signals(
            cls, 
            tickers: tuple = None, 
            sd: str = None, 
            ed: str = None,
    ) -> pd.DataFrame:
        data = cls._query(
            tickers=tickers,
            sd=sd,
            ed=ed,
            key="ticker",
            index="datekey",
            schema="sharadar",
            table="fundamental",
        ).set_index(['ticker', 'datekey'])
        return signals(data)
