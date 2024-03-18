import pandas as pd
from functools import lru_cache


class TSA:
    
    @classmethod
    def _winsorize(cls, df) -> pd.DataFrame:
        df = df.fillna(0)
        df = df.clip(lower=df.quantile(0.05), upper=df.quantile(0.95), axis=0)
        return df

    @classmethod
    def _rolling_zscore(cls, x, window):
        r = x.rolling(window = window)
        m = r.mean().shift(1)
        s = r.std(ddof=1).shift(1)
        z = (x - m) / s
        return z

    @classmethod
    def _ewma_zscore(cls, x, window):
        raise NotImplementedError('Feature is in development.')

    @classmethod
    def _factorize(cls, df):
        pass

    @classmethod
    def _ratios(cls, df):

        def time_index_mean(series: str = None, window=2):
            return series.groupby(level=0, axis=0).rolling(window=2).mean().droplevel(0)

        ratios = pd.DataFrame(index=df.index)
        ratios["current_ratio"] = df["assets"].divide(df["liabilities"])
        ratios["quick_ratio"] = (df["cashnequsd"].add(df["receivables"])).divide(df["liabilitiesc"])
        ratios["cash_ratio"] = df["cashnequsd"].divide(df["liabilitiesc"])
        # ratios["defensive_interval_ratio"] = 
        ratios['receivables_turnover'] = df["revenue"].divide(time_index_mean(df['receivables']))
        ratios['dso'] = ratios.index.to_series().str[1].diff().dt.days.divide(ratios['receivables_turnover'])
        ratios["inventory_turnover"] = (df["revenue"].subtract(df["gp"])).divide(time_index_mean(df['inventory']))
        ratios['doh'] = ratios.index.to_series().str[1].diff().dt.days.divide(ratios['inventory_turnover'])
        # ratios['payables_turnover'] = 
        # ratios['days_of_payables'] = 
        # ratios['cash_conversion_cycle'] = 
        ratios['wc_turnover'] = df['revenue'].divide(time_index_mean(df['workingcapital']))
        # ratios['fixed_asset_turnover'] = 
        ratios['asset_turnover'] = df['revenue'].divide(time_index_mean(df['assets']))
        ratios['gp_margin'] = df['gp'].divide(df['revenue'])
        ratios['ebit_margin'] = df['ebitda'].divide(df['revenue'])
        ratios['pretax_margin'] = df['ebt'].divide(df['revenue'])
        ratios['np_margin'] = df['netinc'].divide(df['revenue'])
        #ratios['operating_roa'] = 

        return ratios