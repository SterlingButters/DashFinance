from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances

import matplotlib.pyplot as plt
from pprint import pprint
from datetime import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', 500)

import plotly.plotly as py
import plotly.graph_objs as go

# ONLY 5 API CALLS AT A TIME
ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas',) # indexing_type='integer')
ti = TechIndicators(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer')
sp = SectorPerformances(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer')


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - dt.strptime(pivot, '%Y-%m-%d')))

####################################################################
# Intraday
data1, meta_data1 = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
####################################################################
# Daily
# data6, meta_data6 = ts.get_daily(symbol='MSFT', outputsize='full')
# data7, meta_data7 = ts.get_daily_adjusted(symbol='MSFT', outputsize='full')
####################################################################
# Weekly
# data8, meta_data8 = ts.get_weekly(symbol='MSFT')
# data9, meta_data9 = ts.get_weekly_adjusted(symbol='MSFT')
####################################################################
# Monthly
# data10, meta_data10 = ts.get_monthly(symbol='MSFT')
# data11, meta_data11 = ts.get_monthly_adjusted(symbol='MSFT')
####################################################################
# Sector
# data12, meta_data12 = sp.get_sector()
####################################################################

# pprint(data1[data1['date'].str.contains("2019-01-14")])

####################################################################
# data1, meta_data = ti.get_bbands(symbol='MSFT', interval='daily', time_period=20)
# data2, meta_data = ti.get_sma(symbol='MSFT', interval='daily')

####################################################################

earlier = '2010-01-01' # ''1998-01-10'
later = '2018-12-01'

print(data1)

# period = data.loc[(data['date'] >= earlier) & (data['date'] < later)]
# data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d',)

# data1 = data1.loc[(data1['date'] >= earlier) & (data1['date'] < later)]
# data2 = data2.loc[(data2['date'] >= earlier) & (data2['date'] < later)]
#
# period = data1.merge(data2, on='date', how='left')
# print(period)

# trace = go.Scatter(x=period['date'],
#                    y=period['SMA']
#                    )
#
# trace1 = go.Scatter(x=period['date'],
#                    y=period['Real Middle Band']
#                    )
#
# trace2 = go.Scatter(x=period['date'],
#                    y=period['Real Lower Band']
#                    )
#
# trace3 = go.Scatter(x=period['date'],
#                    y=period['Real Upper Band']
#                    )
#
# data = [trace, trace1, trace2, trace3]
# layout = {
#     'title': 'The Great Recession',
#     'yaxis': {'title': 'MSFT Stock'},
# }
# fig = dict(data=data, layout=layout)
# py.iplot(fig, filename='Projection', auto_open=True)
#
#
