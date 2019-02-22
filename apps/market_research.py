import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input
import dash_daq as daq
import sd_material_ui
import plotly.graph_objs as go
import pandas as pd

pd.set_option('display.max_columns', 500)

from datetime import datetime as dt
from datetime import timedelta
import time

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas')
ti = TechIndicators(key='9IDB37CDHYIC07UE', output_format='pandas')

from app import app

layout = html.Div([

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

    html.Div([html.Br(), html.Br(), html.Br(),
              html.P('''Greeting Message'''), ]),

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
    html.Button('Show Indicators', id='show-indicators-btn'),
    sd_material_ui.Drawer(id='indicators-drawer', width='20%', docked=False, openSecondary=True,
                          children=sd_material_ui.Paper([
                              daq.BooleanSwitch(label='Simple Moving Average', id='0', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Exponential Moving Average', id='1', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Weighted Moving Average', id='2', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Double Exponential Moving Average', id='3', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Triple Exponential Moving Average', id='4', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Triangular Moving Average', id='5', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Kaufman Adaptive Moving Average', id='6', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='MESA Adaptive Moving Average', id='7', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Triple Exponential Moving Average', id='8', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Moving Average Convergence/Divergence', id='9', on=False,
                                                labelPosition='right'),
                              # {'daq.BooleanSwitch(label'='', id='', on=False, labelPosition='right'), MACDEXT
                              daq.BooleanSwitch(label='Stochastic Oscillator Values', id='10', on=False,
                                                labelPosition='right'),
                              # {'daq.BooleanSwitch(label'='', id='', on=False, labelPosition='right'), STOCHF
                              daq.BooleanSwitch(label='Relative Strength Index', id='11', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Stochastic Relative Strength Index', id='12', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Williams %R Values', id='13', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Average Directional Movement Index', id='14', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Absolute Price Oscillator Values', id='15', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Percentage Price Oscillator Values', id='16', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Momentum Values', id='17', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Balance of Power Values', id='18', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Commodity Channel Index', id='19', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Chande Momentum Oscillator Values', id='20', on=False,
                                                labelPosition='right'),
                              # {'daq.BooleanSwitch(label'='Rate of Change Values', id='', on=False, labelPosition='right'), # Save as default indicator
                              daq.BooleanSwitch(label='AROON Values', id='21', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='AROON OScillator Values', id='22', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Money Flow Index', id='23', on=False, labelPosition='right'),
                              # {'daq.BooleanSwitch(label'='', id='', on=False, labelPosition='right'), TRIX
                              daq.BooleanSwitch(label='Ultimate Oscillator Values', id='24', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Directional Movement Index', id='25', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Minus Directional Indicator Values', id='26', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Plus Directional Indicator Values', id='27', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Minus Directional Movement Values', id='28', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Plus Directional Movement Values', id='29', on=False,
                                                labelPosition='right'),
                              # {'daq.BooleanSwitch(label'='', id='', on=False, labelPosition='right'), # BBands by default
                              daq.BooleanSwitch(label='Midpoint Values', id='30', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Midprice Values', id='31', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Parabolic SAR Values', id='32', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='True Range Values', id='33', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Average True Range Values', id='34', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Normalized Average True Range Values', id='35', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Chaikin A/D Line Values', id='36', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Chaikin A/D Oscialltor Values', id='37', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='On-balance Volume Values', id='38', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Hilbert Transform', id='39', on=False, labelPosition='right'),
                              daq.BooleanSwitch(label='Hilbert Transform: Sine Wave', id='40', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Hilbert Transform: Trend vs Cycle', id='41', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Hilbert Transform: Dominant Cycle Period', id='42', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Hilbert Transform: Dominant Cycle Phase', id='43', on=False,
                                                labelPosition='right'),
                              daq.BooleanSwitch(label='Hilbert Transform: Phasor Components', id='44', on=False,
                                                labelPosition='right'),
                          ])),
    html.Div(id='market-graph'),

])

# TODO: LiveUpdate
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
    Output('indicators-drawer', 'open'),
    [Input('show-indicators-btn', 'n_clicks')],
    [State('indicators-drawer', 'open')]
)
def display_clicks_flat(open_clicks: int, state):
    if open_clicks:
        if not state:
            return True


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
                    data3, meta3 = ts.get_intraday(symbol='{}'.format(ticker), interval='1min', outputsize='full')
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

            candlesticks = go.Candlestick(x=period['date'],  # or go.Ohlc
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
                xaxis=dict(type='category'),
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
