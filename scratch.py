from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.alphavantage import AlphaVantage

import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', 500)

import plotly.plotly as py
import plotly.graph_objs as go

# ONLY 5 API CALLS AT A TIME
ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer')
av = AlphaVantage(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer')

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

# data6['4. close'].plot()
# plt.title('Intraday Times Series for the MSFT stock (5 min)')


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - dt.strptime(pivot, '%Y-%m-%d')))
# dt.strptime(x, '%Y-%m-%d')


data, meta_data = ts.get_daily_adjusted(symbol='MSFT', outputsize='full')

print(data)

earlier = '1998-01-10'
later = '2018-12-01'

# period = data.loc[(data['date'] >= earlier) & (data['date'] < later)]
# data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d',)
#
# trace = go.Ohlc(x=period['date'],
#                 open=period['1. open'],
#                 high=period['2. high'],
#                 low=period['3. low'],
#                 close=period['4. close'])
# data = [trace]
# layout = {
#     'title': 'The Great Recession',
#     'yaxis': {'title': 'MSFT Stock'},
# }
# fig = dict(data=data, layout=layout)
# py.iplot(fig, filename='Candlestick', auto_open=True)


