import os
import io
import configparser
import sqlalchemy as sa
import pandas as pd
import redis
import kubernetes
from functools import lru_cache
from typing import Tuple


os.environ["DB_PASS"] = "FscP@2023"
kubernetes.config.load_incluster_config()


class Core:
    _CONFIG_FILE_PATH = f"{os.path.dirname(__file__)}/conf/config.properties"
    _CACHE_POLICY = os.getenv("CACHE_POLICY", "default")

    _config = configparser.ConfigParser()
    _config.read(_CONFIG_FILE_PATH)
    _redis = redis.Redis(
        host=_config.get("CACHING", "REDIS_HOST"),
        port=_config.get("CACHING", "REDIS_PORT"),
    )
    _redis_ttl = _config.get("CACHING", "REDIS_TTL")
    # _kubernetes = kubernetes.client.CoreV1Api()
    # secret = _kubernetes.read_namespaced_secret("timescale-credentials", "fidcuevas")
    _connection_engine = sa.create_engine(
        sa.engine.URL.create(
            "postgresql+psycopg2",
            database=_config.get("MARKET_DATA", "DB_NAME"),
            username=_config.get("MARKET_DATA", "DB_USER"),
            password=os.environ["DB_PASS"],
            host=_config.get("MARKET_DATA", "DB_HOST"),
            port=_config.get("MARKET_DATA", "DB_PORT"),
        )
    )


    @classmethod
    def _format_ticker_tuple(cls, tickers: Tuple = None) -> str:
        return ", ".join([f"'{ticker}'" for ticker in tickers])

    @classmethod
    def _get_date_ranges(
        key: str = None,
        index_col: str = None,
        index: Tuple = None,
        schema: str = None,
        table: str = None,
    ) -> (str, str):
        sd = (
            cls._query(f"SELECT MIN({key}) FROM {schema}.{table} WHERE {index_col} IN ({formatted_tickers})")
            .iat[0, 0]
            .strftime("%Y-%m-%d")
        )
        ed = (
            cls._query(f"SELECT MAX({key}) FROM {schema}.{table} WHERE {index_col} IN ({formatted_tickers})")
            .iat[0, 0]
            .strftime("%Y-%m-%d")
        )
        return sd, ed

    @classmethod
    def _query(
        cls,
        tickers: Tuple = None,
        sd: str = None,
        ed: str = None,
        key: str = None,
        index: str = None,
        schema: str = None,
        table: str = None,
    ):
        tickers = sorted(tickers)
        sql = f"""
        SELECT *
        FROM {schema}.{table}
        WHERE {key} IN ({cls._format_ticker_tuple(tickers=tickers)})
        {"AND {index} BETWEEN '" + sd + "' AND '" + ed + "'" if sd and ed else ''}
        """

        if cls._CACHE_POLICY == "default" and (data := cls._redis.get(sql)):
                return pd.read_parquet(io.BytesIO(data))
        else:
            data = pd.read_sql(sql, con=cls._connection_engine)
            cls._redis.set(sql, data.to_parquet(), ex=cls._redis_ttl)
            return data
