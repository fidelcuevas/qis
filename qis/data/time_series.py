import pandas as pd
import numpy as np
from functools import lru_cache
from typing import List
from qis.core import Core
from qis.data.analysis import TSA


class TimeSeries(Core):
    @classmethod
    @lru_cache(maxsize=16)
    def ohlc(cls, tickers: tuple = None, sd: str = None, ed: str = None) -> pd.DataFrame:
        """
        Fetch OHLC data for >=1 tickers and for specified dates. Default start and end dates are
        max values in the table for the specified tickers.
        """
        return cls._query(
            tickers=tickers,
            sd=sd,
            ed=ed,
            key="ticker",
            index="date",
            schema="sharadar",
            table="ohlc",
        )

    @classmethod
    @lru_cache(maxsize=16)
    def fundamental(cls, tickers: tuple = None, sd: str = None, ed: str = None) -> pd.DataFrame:
        """
        :tickers list:
        :sd str:
        :ed str:
        """
        return cls._query(
            tickers=tickers,
            sd=sd,
            ed=ed,
            key="ticker",
            index="datekey",
            schema="sharadar",
            table="fundamental",
        ).set_index(['ticker', 'datekey'])

    @classmethod
    @lru_cache(maxsize=16)
    def valuations(cls, tickers: tuple = None, sd: str = None, ed: str = None) -> pd.DataFrame:
        """
        :tickers list:
        :sd str:
        :ed str:
        """
        data = cls._query(
            tickers=tickers,
            sd=sd,
            ed=ed,
            key="ticker",
            index="date",
            schema="sharadar",
            table="ratios",
        )
        data = data.ffill(axis=0).dropna(axis=0).set_index(["ticker", "date"])
        data = data.apply(lambda x: (data["closeadj"] * data["shareswa"]) / x, axis=0).replace(np.inf, 0)
        data = data.drop(labels=["closeadj", "sharesbas", "shareswa", "shareswadil"], axis=1)
        return data

    @classmethod
    @lru_cache(maxsize=16)
    def ratios(
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
        return TSA._ratios(data)

    @classmethod
    @lru_cache(maxsize=16)
    def signals(
            cls, 
            tickers: tuple = None, 
            sd: str = None, 
            ed: str = None, 
            neutralize: bool = False,
            frequency: 'str' = 'B',
    ) -> pd.DataFrame:
        data = cls.ratios(tickers=tickers, sd=sd, ed=ed)
        data = (
            data.groupby(level=0, axis=0)
            .apply(lambda x: TSA._rolling_zscore(x, window=3))
            .droplevel(0)
            .unstack(level=0)
            .ffill()
            .asfreq(frequency, method='ffill')
        )

        if neutralize:
            return data.subtract(data.groupby(level=0, axis=1).mean(), axis=1, level=0)
        else:
            return data