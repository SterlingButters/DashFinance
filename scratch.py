from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', 500)

import plotly.plotly as py
import plotly.graph_objs as go

# ONLY 5 API CALLS AT A TIME
ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer')
ti = TechIndicators(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer')

# data1, meta_data1 = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
# data2, meta_data2 = ts.get_intraday(symbol='MSFT',interval='5min', outputsize='full')
# data3, meta_data3 = ts.get_intraday(symbol='MSFT',interval='15min', outputsize='full')
# data4, meta_data4 = ts.get_intraday(symbol='MSFT',interval='30min', outputsize='full')
# data5, meta_data5 = ts.get_intraday(symbol='MSFT',interval='60min', outputsize='full')

# data6, meta_data6 = ts.get_daily(symbol='MSFT', outputsize='full')
# data7, meta_data7 = ts.get_daily_adjusted(symbol='MSFT', outputsize='full')

# data8, meta_data8 = ts.get_weekly(symbol='MSFT')
# data9, meta_data9 = ts.get_weekly_adjusted(symbol='MSFT')

# data10, meta_data10 = ts.get_monthly(symbol='MSFT')
# data11, meta_data11 = ts.get_monthly_adjusted(symbol='MSFT')

# pprint(meta_data6)
# pprint(data6)
# pprint(data1[data1['date'].str.contains("2019-01-14")])

# get_bbands(self, symbol, interval='daily', time_period=20, series_type='close',
#                nbdevup=None, nbdevdn=None, matype=None):
#
#  """ Return the bollinger bands values in two
#     json objects as data and meta_data. It raises ValueError when problems
#     arise
#     Keyword Arguments:
#         symbol:  the symbol for the equity we want to get its data
#         interval:  time interval between two consecutive values,
#             supported values are '1min', '5min', '15min', '30min', '60min', 'daily',
#             'weekly', 'monthly' (default 'daily'
#         time_period: Number of data points used to calculate each BBANDS value.
#             Positive integers are accepted (e.g., time_period=60, time_period=200)
#         series_type:  The desired price type in the time series. Four types
#             are supported: 'close', 'open', 'high', 'low' (default 'close')
#         nbdevup:  The standard deviation multiplier of the upper band. Positive
#             integers are accepted as default (default=2)
#         nbdevdn:  The standard deviation multiplier of the lower band. Positive
#             integers are accepted as default (default=2)
#         matype :  Moving average type. By default, matype=0.
#             Integers 0 - 8 are accepted (check  down the mappings) or the string
#             containing the math type can also be used.
#             * 0 = Simple Moving Average (SMA),
#             * 1 = Exponential Moving Average (EMA),
#             * 2 = Weighted Moving Average (WMA),
#             * 3 = Double Exponential Moving Average (DEMA),
#             * 4 = Triple Exponential Moving Average (TEMA),
#             * 5 = Triangular Moving Average (TRIMA),
#             * 6 = T3 Moving Average,
#             * 7 = Kaufman Adaptive Moving Average (KAMA),
#             * 8 = MESA Adaptive Moving Average (MAMA)
#     """


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - dt.strptime(pivot, '%Y-%m-%d')))

symbols = ['AAPL', 'GOOG', 'MSFT', 'AMZN']
quotes = ts.get_quote_endpoint('AAPL')
print(quotes)

# earlier = '1998-01-10'
# later = '2018-12-01'
#
# period = data.loc[(data['date'] >= earlier) & (data['date'] < later)]
# data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d',)

# trace = go.Scatter(x=period['date'],
#                    y=period[''])
# data = [trace]
# layout = {
#     'title': 'The Great Recession',
#     'yaxis': {'title': 'MSFT Stock'},
# }
# fig = dict(data=data, layout=layout)
# py.iplot(fig, filename='Candlestick', auto_open=True)


