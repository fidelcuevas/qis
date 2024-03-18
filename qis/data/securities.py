import inspect
import sys
from functools import lru_cache
from qis.core import Core


securities = Core._query(tickers=('SEP',), key='"table"', schema='sharadar', table='tickers')


    # @classmethod
    # @lru_cache
    # def _sic_map(cls):
    #     return (
    #         cls._securities_map().loc[:, ['siccode', 'sicsector', 'sicindustry']]
    #         .sort_values(by=['siccode', 'sicsector', 'sicindustry'])
    #         .dropna()
    #         .drop_duplicates()
    #         .set_index('siccode')
    #     )

# for column in Securities._securities_map().columns:
#     setattr(Securities, column, Securities._securities_map().loc[:, column].drop_duplicates())

    # @classmethod
    # def sic_codes(cls):
    #     return cls._sic_map().index.tolist()

    # @classmethod
    # def sic_sectors(cls):
    #     return cls._sic_map().loc[:, 'sicsector'].drop_duplicates()

    # @classmethod
    # def sic_industries(cls):
    #     return cls._sic_map().loc[:, 'sicindustry'].drop_duplicates()
