from typing import Dict, List, Any

import dash
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
import time
import base64
import io

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas')
ti = TechIndicators(key='9IDB37CDHYIC07UE', output_format='pandas')


# TODO
df_symbol = pd.read_csv('tickers.csv')

################################################################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([

    html.H2('Custom Finance Explorer',
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

    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Research', value='tab-1'),
        dcc.Tab(label='Activity/Performance', value='tab-2'),
        dcc.Tab(label='Loan Calculator', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([

            # dcc.Store(id='ticker-options-memory', storage_type='local'), # For DropDown Options
            # dcc.Store(id='ticker-selection-memory', storage_type='session'), # For DropDown Values

            dcc.Dropdown(
                id='stock-ticker-input',
                multi=True,
            ),

            dcc.Input(
                id='keyword',
                placeholder='Search Ticker Database',
                type='text',
                value=''
            ),

            html.Button('Add Results to Dropdown', id='add-results-button', n_clicks=0),
            html.Br(),

            dcc.DatePickerRange(
                id='date-picker-range',
                # start_date_placeholder_text= ,
                max_date_allowed=dt.date(dt.today()),
                start_date=dt.date(dt.today()) - timedelta(days=30),
                end_date=dt.date(dt.today()),
                calendar_orientation='vertical',
            ),

            html.Div(id='debug'),

            html.Br(),

            html.Div(id='market-graph'),
        ])

    elif tab == 'tab-2':
        return html.Div([

            # dcc.Store(id='order-table-memory', storage_type='local'),  # For Order Table Entries
            # dcc.Store(id='computed-table-entry', storage_type='session'),  # For Computed Table Entries

            dcc.Upload(
                id='orders-upload',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed',
                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                },
            ),

            dash_table.DataTable(
                id='order-table',
                columns=(
                    [{'id': 'Ticker', 'name': 'Ticker', 'type': 'dropdown'},
                     {'id': 'Action', 'name': 'Action', 'type': 'dropdown'},
                     {'id': 'Unit', 'name': 'Unit', 'type': 'dropdown'},
                     {'id': 'Amount', 'name': 'Amount'},    # TODO: Make numbers only
                     {'id': 'Date', 'name': 'Date'},
                     {'id': 'Time', 'name': 'Time'}]
                ),
                data=[],
                editable=True,
                sorting=True,
                filtering=True,
                row_deletable=True,
                row_selectable=True,

                column_static_dropdown=[
                    {
                        'id': 'Ticker',
                        'dropdown': [
                            {'label': i, 'value': i}
                            # TODO:
                            for i in df_symbol.Symbol.unique()
                        ]
                    },
                    {
                        'id': 'Action',
                        'dropdown': [
                            {'label': 'Buy', 'value': 'BUY'},
                            {'label': 'Sell', 'value': 'SELL'},
                        ]
                    },
                    {
                        'id': 'Unit',
                        'dropdown': [
                            {'label': 'Shares', 'value': 'SHARES'},
                            {'label': 'Value', 'value': 'VALUE'},
                        ]
                    },
                ]
            ),

            dcc.DatePickerSingle(
                id='order-date',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=dt.date(dt.today()),
                date=dt.date(dt.today()),
                with_portal=False,
                calendar_orientation='vertical'
            ),

            html.Button('Add Order', id='add-order-button', n_clicks=0),
            html.Br(),

            ####################################

            dash_table.DataTable(
                id='computed-table',
                columns=[
                    {'name': 'Position', 'id': 'Position'},
                    {'name': 'Type', 'id': 'Type'},
                    {'name': 'Shares', 'id': 'Shares'},
                    {'name': 'Value', 'id': 'Value'},
                    {'name': 'Equity', 'id': 'Equity'},
                    {'name': 'Est Gain/Loss', 'id': 'GainLoss'},
                ],
                data=[],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },
                    {
                        'if': {
                            'column_id': 'GainLoss',
                            'filter': 'GainLoss > num(0.0)'
                        },
                        'backgroundColor': '#3D9970',
                        'color': 'white',
                    },
                    {
                        'if': {
                            'column_id': 'GainLoss',
                            'filter': 'GainLoss < num(0.0)'
                        },
                        'backgroundColor': '#F55C57',
                        'color': 'white',
                    },
                ]
            ),

            dcc.Graph(
                id='asset-distribution',
            ),

        ])

    elif tab == 'tab-3':
        return html.Div([
            dcc.Input(
                id='',
                placeholder='Enter Loan Amount',
                type='text',
                value=''
            ),
            dcc.Input(
                id='',
                placeholder='Enter Down Payment',
                type='text',
                value=''
            ),
            html.P("APR %"),
            dcc.Slider(
                id='apr-rate',
                min=0,
                max=25,
                value=5,
            )
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
        results.columns = ['label', 'value']

        list.extend(results.to_dict('rows'))

    return list


@app.callback(
    Output('market-graph', 'children'),
   [Input('stock-ticker-input', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
])
def update_graph(tickers, startdate, enddate):

    graphs = []

    if tickers is not None:
        for ticker in tickers:
            data1 = None
            data2 = None
            while data1 is None:
                try:
                    data1, meta1 = ts.get_daily_adjusted(symbol='{}'.format(ticker), outputsize='full')

                except:
                    pass
                    time.sleep(5)

            while data2 is None:
                try:
                    data2, meta2 = ti.get_bbands(symbol='{}'.format(ticker), interval='daily', time_period=60,
                                             series_type='close',
                                             nbdevup=None, nbdevdn=None, matype=None)
                except:
                    pass
                    time.sleep(5)

            data1 = data1.reset_index()
            data2 = data2.reset_index()

            data1 = data1.loc[(data1['date'] >= startdate) & (data1['date'] < enddate)]
            data2 = data2.loc[(data2['date'] >= startdate) & (data2['date'] < enddate)]

            period = data1.merge(data2, on='date', how='left')

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
            # TODO: Bug here
            fig = go.Figure(data=[bband_mid, bband_low, bband_high, candlesticks, volume], layout=layout)

            graphs.append(dcc.Graph(figure=fig))

    return graphs


################################################################################
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))


@app.callback(
    Output('order-table', 'data'),
    [Input('add-order-button', 'n_clicks'),
     Input('orders-upload', 'contents')],
    [State('order-table', 'data'),
     State('order-date', 'date'),
     State('orders-upload', 'filename')])
def add_row(n_clicks, contents, rows, date, filename):
    # TODO: Allow upload at any point
    if n_clicks > 0:
        rows.append({'Amount': 0, 'Date': str(date), 'Time': '-'})

    else:
        if contents is not None:
            df = parse_contents(contents, filename)
            rows.extend(df.to_dict('rows'))

    return rows

##########################################


# TODO: Update in efficient way preferably with timestamps
@app.callback(
    Output('computed-table', 'data'),
    [Input('order-table', 'data'),],
    [State('computed-table', 'data')])
def compute_positions(rows, comp_rows):

    tickers = [row.get('Ticker') for row in rows]
    actions = [row.get('Action') for row in rows]
    units = [row.get('Unit') for row in rows]
    amounts = [float(row.get('Amount')) for row in rows]
    dates = [row.get('Date') for row in rows]
    times = [row.get('Time') for row in rows]

    positions = [row.get('Position') for row in comp_rows]
    quantity = [row.get('Shares') for row in comp_rows]
    values = [row.get('Value') for row in comp_rows]
    basises = [row.get('Equity') for row in comp_rows]
    gain_losses = [row.get('GainLoss') for row in comp_rows]

    if len(tickers) > 0:
        latest = [tickers[-1], actions[-1], units[-1], amounts[-1], dates[-1]]
        if all(e is not None for e in latest) & (amounts[-1]!=0):
            print(latest)

            def get_market(ticker, date):

                def nearest(items, pivot):
                    nearest_date = min(items, key=lambda x: abs(dt.strptime(x, '%Y-%m-%d') - dt.strptime(pivot, '%Y-%m-%d')))
                    return nearest_date

                data = None
                while data is None:
                    try:
                        data, meta_data = ts.get_daily_adjusted(symbol='{}'.format(ticker), outputsize='full')

                    except:
                        pass
                        time.sleep(5)
                        # return html.P("Could Not Retrieve Data")

                market = (data.loc[nearest(data.index.get_values(), date)]['4. close'])

                return market

            if actions[-1] == 'SELL':
                amounts[-1] *= -1

            market_then = get_market(tickers[-1], dates[-1])

            now = str(dt.date(dt.now()))

            market_now = get_market(tickers[-1], now)

            if units[-1] == 'SHARES':
                basis = amounts[-1]*market_then
                value = amounts[-1]*market_now
                shares = amounts[-1]
            else:
                basis = amounts[-1]
                shares = amounts[-1]/market_then
                value = shares*market_now

            gain_loss = value - basis

            if len(positions) > 0:
                try:
                    p = positions.index(tickers[-1])

                    values[p] += value
                    quantity[p] += shares
                    basises[p] += basis
                    gain_losses[p] += gain_loss

                    comp_rows[p] = {'Position': positions[p], 'Type': 'Stock', 'Shares': quantity[p], 'Value': values[p], 'Basis': basis, 'GainLoss': gain_losses[p]}
                except:
                    comp_rows.append(
                        {'Position': tickers[-1], 'Type': 'Stock', 'Shares': shares, 'Value': value, 'Basis': basis,
                         'GainLoss': gain_loss})

            else:
                comp_rows.append({'Position': tickers[-1], 'Type': 'Stock', 'Shares': shares, 'Value': value, 'Basis': basis, 'GainLoss': gain_loss})

    return comp_rows


################################################################################


@app.callback(
    Output('asset-distribution', 'figure'),
   [Input('computed-table', 'data'),
    Input('asset-distribution', 'hoverData')]
)
def update_pie(rows, hoverdata):
    positions = [row.get('Position') for row in rows]
    shares = [row.get('Shares') for row in rows]
    values = [row.get('Value') for row in rows]

    selected_position = None
    if hoverdata:
        selected_position = hoverdata['points'][0]['label']

    pull = np.zeros(len(positions))
    for p in range(len(positions)):
        if selected_position == positions[p]:
            pull[p]=.05
        else:
            pull[p]=0

    pie=go.Pie(values=values,
               labels=positions,
               hoverinfo="label+percent+name",
               hole=.5,
               pull=pull,
               rotation=0  # -360 : +360
               )

    layout=go.Layout(title="Asset Distribution",
                     width=1000,
                     height=1000,
                     annotations=[
                         dict(
                             font=dict(size=40),
                             showarrow=False,
                             text="Total: ${}".format(round(float(np.sum(np.array(values))), 2)),
                             x=.50,
                             y=.50,
                         ),],
                     )

    data=[pie]

    fig = go.Figure(data=data, layout=layout)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)