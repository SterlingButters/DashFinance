import dash
import sd_material_ui
import dash_core_components as dcc
import dash_table
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go
import pandas as pd
pd.set_option('display.max_columns', 500)

from datetime import datetime as dt
from datetime import timedelta

import numpy as np
from random import randint
import time
import base64
import io
import os

import flask

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas')
ti = TechIndicators(key='9IDB37CDHYIC07UE', output_format='pandas')

# from index import app

# TODO
df_symbol = pd.read_csv('tickers.csv')

################################################################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
################################################################################

app.layout = html.Div([

    html.H2('Market Research',
            style={'display': 'inline',
                   'float': 'left',
                   'font-size': '2.65em',
                   'margin-left': '7px',
                   'font-weight': 'bolder',
                   'font-family': 'Product Sans',
                   'color': "rgba(117, 117, 117, 0.95)",
                   'margin-top': '20px',
                   'margin-bottom': '0'
                   }),

    html.Img(src="",
             style={
                 'height': '100px',
                 'float': 'right'
             },),

    html.Div([html.Br(), html.Br(), html.Br(),
    html.P('''Welcome to finance explorer. There is much left to be developed and I very much wish to find a faster API. 
    Unfortunately, it is likely you will notice the amount of time it takes to retreive data... it is EXTREMELY SLOW (~45 s). This could be from limits
    set by the API, current internet connection at time of testing, etc. Please enjoy everything else :)'''),]),

    # dcc.Store(id='ticker-options-memory', storage_type='local'), # For DropDown Options
    # dcc.Store(id='ticker-selection-memory', storage_type='session'), # For DropDown Values
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='stock-ticker-input',
                multi=True,
                style={'height': '52px'}),
        ],
            style=dict(
                width='50%',
                display='table-cell',
                verticalAlign="middle",
            ),
        ),

        html.Div([
            dcc.Input(
                id='keyword',
                placeholder='Search Ticker Database',
                type='text',
                value='',
                style={'height': '52px'}
            ),
        ],
            style=dict(
                width='10%',
                display='table-cell',
                verticalAlign="middle",
            ),
        ),

        html.Div([html.Button('Add Results to Dropdown', id='add-results-button', n_clicks=0,
                              style={'height': '52px'})],
                 style=dict(
                     display='table-cell',
                     verticalAlign="middle",
                 ),
                 ),

        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                max_date_allowed=dt.date(dt.today()),
                start_date=dt.date(dt.today()) - timedelta(days=60),
                end_date=dt.date(dt.today()),
                calendar_orientation='vertical',
            ),
        ],
            style=dict(
                width='20%',
                display='table-cell',
                verticalAlign="middle",
            ),
        ),
    ], style=dict(
        width='100%',
        display='table',
    ),
    ),

    html.Br(),
    html.Div(id='market-graph'),
    html.Div(id='debug')

    # dcc.Checklist(
    #     options=[
    #         {'label': 'Simple Moving Average', 'value': '0'},
    #         {'label': 'Exponential Moving Average', 'value': '1'},
    #         {'label': 'Weighted Moving Average', 'value': '2'},
    #         {'label': 'Double Exponential Moving Average', 'value': '3'},
    #         {'label': 'Triple Exponential Moving Average', 'value': '4'},
    #         {'label': 'Triangular Moving Average', 'value': '5'},
    #         {'label': 'Kaufman Adaptive Moving Average', 'value': '6'},
    #         {'label': 'MESA Adaptive Moving Average', 'value': '7'},
    #         {'label': 'Triple Exponential Moving Average', 'value': '8'},
    #         {'label': 'Moving Average Convergence/Divergence', 'value': '9'},
    #         # {'label': '', 'value': ''}, MACDEXT
    #         {'label': 'Stochastic Oscillator Values', 'value': '10'},
    #         # {'label': '', 'value': ''}, STOCHF
    #         {'label': 'Relative Strength Index', 'value': '11'},
    #         {'label': 'Stochastic Relative Strength Index', 'value': '12'},
    #         {'label': 'Williams %R Values', 'value': '13'},
    #         {'label': 'Average Directional Movement Index', 'value': '14'},
    #         {'label': 'Absolute Price Oscillator Values', 'value': '15'},
    #         {'label': 'Percentage Price Oscillator Values', 'value': '16'},
    #         {'label': 'Momentum Values', 'value': '17'},
    #         {'label': 'Balance of Power Values', 'value': '18'},
    #         {'label': 'Commodity Channel Index', 'value': '19'},
    #         {'label': 'Chande Momentum Oscillator Values', 'value': '20'},
    #         # {'label': 'Rate of Change Values', 'value': ''}, # Save as default indicator
    #         {'label': 'AROON Values', 'value': '21'},
    #         {'label': 'AROON OScillator Values', 'value': '22'},
    #         {'label': 'Money Flow Index', 'value': '23'},
    #         # {'label': '', 'value': ''}, TRIX
    #         {'label': 'Ultimate Oscillator Values', 'value': '24'},
    #         {'label': 'Directional Movement Index', 'value': '25'},
    #         {'label': 'Minus Directional Indicator Values', 'value': '26'},
    #         {'label': 'Plus Directional Indicator Values', 'value': '27'},
    #         {'label': 'Minus Directional Movement Values', 'value': '28'},
    #         {'label': 'Plus Directional Movement Values', 'value': '29'},
    #         # {'label': '', 'value': ''}, # BBands by default
    #         {'label': 'Midpoint Values', 'value': '30'},
    #         {'label': 'Midprice Values', 'value': '31'},
    #         {'label': 'Parabolic SAR Values', 'value': '32'},
    #         {'label': 'True Range Values', 'value': '33'},
    #         {'label': 'Average True Range Values', 'value': '34'},
    #         {'label': 'Normalized Average True Range Values', 'value': '35'},
    #         {'label': 'Chaikin A/D Line Values', 'value': '36'},
    #         {'label': 'Chaikin A/D Oscialltor Values', 'value': '37'},
    #         {'label': 'On-balance Volume Values', 'value': '38'},
    #         {'label': 'Hilbert Transform', 'value': '39'},
    #         {'label': 'Hilbert Transform: Sine Wave', 'value': '40'},
    #         {'label': 'Hilbert Transform: Trend vs Cycle', 'value': '41'},
    #         {'label': 'Hilbert Transform: Dominant Cycle Period', 'value': '42'},
    #         {'label': 'Hilbert Transform: Dominant Cycle Phase', 'value': '43'},
    #         {'label': 'Hilbert Transform: Phasor Components', 'value': '44'},
    #     ],
    #     values=['32', '1', '10'],
    #     style={'vertical-align': 'right'}
    # )
])


################################################################################

# TODO: Consider adding results to text file
@app.callback(
    Output('stock-ticker-input', 'options'),
    [Input('add-results-button', 'n_clicks')],
    [State('keyword', 'value'),
     State('stock-ticker-input', 'options')])
def create_dropdown(n_clicks, keyword, options):
    list = []
    if n_clicks > 0:
        list.extend(options)

        results = pd.DataFrame(ts.get_symbol_search('{}'.format(keyword))[0][['2. name', '1. symbol']])  # '3. type'
        results['2. name'] = results[['1. symbol', '2. name']].apply(lambda x: ' - '.join(x), axis=1)
        results.columns = ['label', 'value']

        list.extend(results.to_dict('rows'))

    return list


@app.callback(
    Output('market-graph', 'children'),
   [Input('stock-ticker-input', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
])
def update_graph(tickers, startdate, enddate):

    graphs = []

    if tickers is not None:
        for ticker in tickers:
            data1 = None
            data2 = None
            data3 = None

            while data1 is None:
                try:
                    data1, meta1 = ts.get_daily_adjusted(symbol='{}'.format(ticker), outputsize='full')
                except:
                    pass
                    time.sleep(3)

            while data2 is None:
                try:
                    data2, meta2 = ti.get_bbands(symbol='{}'.format(ticker), interval='daily', time_period=60,
                                             series_type='close',
                                             nbdevup=None, nbdevdn=None, matype=None)
                except:
                    pass
                    time.sleep(3)

            while data3 is None:
                try:
                    data3, meta3 = ts.get_intraday(symbol='{}'.format(ticker),interval='1min', outputsize='full')
                except:
                    pass
                    time.sleep(3)

            data1 = data1.reset_index()
            data2 = data2.reset_index()

            data1 = data1.loc[(data1['date'] >= startdate) & (data1['date'] < enddate)]
            data2 = data2.loc[(data2['date'] >= startdate) & (data2['date'] < enddate)]

            period = data1.merge(data2, on='date', how='left')

            data3 = data3.reset_index()

            bband_mid = go.Scatter(x=period['date'],
                                   y=period['Real Middle Band'],
                                   mode='lines',
                                   line=dict(
                                       width=1,
                                       color='rgb(150, 150, 150)'
                                       ),
                                   name='Real Middle Band'
                                )

            bband_low = go.Scatter(x=period['date'],
                                   y=period['Real Upper Band'],
                                   mode='lines',
                                   line=dict(
                                       width=1,
                                       color='rgb(150, 150, 150)'
                                   ),
                                   name='Real Upper Band'
                                )

            bband_high = go.Scatter(x=period['date'],
                                   y=period['Real Lower Band'],
                                   mode='lines',
                                   line=dict(
                                       width=1,
                                       color='rgb(150, 150, 150)'
                                   ),
                                   name='Real Lower Band'
                                )

            candlesticks = go.Candlestick(x=period['date'], # or go.Ohlc
                                          open=period['1. open'],
                                          high=period['2. high'],
                                          low=period['3. low'],
                                          close=period['4. close'],
                                          name='Candlestick')

            volume = go.Bar(x=period['date'],
                            y=period['6. volume'],
                            yaxis='y2',
                            marker=dict(
                                color='rgb(204,204,204)'),
                            opacity=.3,
                            name='Volume')

            can = go.Candlestick(x=data3['date'],  # or go.Ohlc
                                          open=data3['1. open'],
                                          high=data3['2. high'],
                                          low=data3['3. low'],
                                          close=data3['4. close'],
                                          name='Candlestick')

            vol = go.Bar(x=data3['date'],
                            y=data3['5. volume'],
                            yaxis='y2',
                            marker=dict(
                                color='rgb(204,204,204)'),
                            opacity=.3,
                            name='Volume')

            layout = go.Layout(
                    title='{}'.format(ticker),
                    width=1250,
                    height=750,
                    xaxis=dict(),
                    yaxis=dict(
                        title='Value $USD',
                    ),
                    yaxis2=dict(
                        title='Volume',
                        overlaying='y',
                        side='right',
                        # anchor='free'
                    )
                )
            fig = go.Figure(data=[bband_mid, bband_low, bband_high, candlesticks, volume], layout=layout)
            fig2 = go.Figure(data=[can, vol], layout=layout)

            graphs.append(dcc.Graph(figure=fig))
            graphs.append(dcc.Graph(figure=fig2))

    return graphs

################################################################################
if __name__ == '__main__':
    # Production
    # app.server.run(debug=True, threaded=True)

    # Development
    app.run_server(debug=True)
