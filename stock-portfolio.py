import dash
import sd_material_ui
import dash_core_components as dcc
import dash_table
from dash.exceptions import PreventUpdate
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

# TODO
df_symbol = pd.read_csv('./assets/tickers.csv')

################################################################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([

    html.H2('Virtual Market Portfolio',
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
    html.Div(style=dict(height=75)),
    html.Img(src="",
             style={
                 'height': '100px',
                 'float': 'right'
             }),

    html.P("""The orders table currently only supports evaluation if you upload your orders FIRST,
     i.e. if you add orders manually and then try to upload, it will not work correctly... for now. 
     However, you MAY upload orders and then add additional ones manually"""),

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
             {'id': 'Amount', 'name': 'Amount'},  # TODO: Make numbers only
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
    html.Div(id='debug'),
    dash_table.DataTable(
        id='computed-table',
        columns=[
            {'name': 'Position', 'id': 'Position'},
            {'name': 'Type', 'id': 'Type'},
            {'name': 'Shares', 'id': 'Shares'},
            {'name': 'Value', 'id': 'Value'},
            {'name': 'Basis', 'id': 'Basis'},
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
    dash_table.DataTable(id='hidden-ledger'),
    dcc.Graph(id='asset-distribution'),
    dcc.Graph(id='value-graph')
])


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
    # TODO: Allow upload at any point; currently only supports upload at beginning
    if n_clicks > 0:
        rows.append({'Amount': 0, 'Date': str(date), 'Time': '-'})

    else:
        if contents is not None:
            df = parse_contents(contents, filename)
            rows.extend(df.to_dict('rows'))

    return rows


##########################################
def nearest(items, pivot):
    nearest_date = min(items, key=lambda x: abs(dt.strptime(x, '%Y-%m-%d') - dt.strptime(pivot, '%Y-%m-%d')))
    return nearest_date


@app.callback(
    Output('hidden-ledger', 'data'),
    [Input('order-table', 'data')],
    [State('hidden-ledger', 'data')]
)
def get_holding_times(rows, comp_rows):
    tickers = [row.get('Ticker') for row in rows]
    actions = [row.get('Action') for row in rows]
    units = [row.get('Unit') for row in rows]
    amounts = [float(row.get('Amount')) for row in rows]
    dates = [row.get('Date') for row in rows]

    dict = []
    mass_dict = []
    date_column = None

    if len(tickers) > 0:
        unique_tickers = set(tickers)
        for ticker in unique_tickers:
            idxs = []
            for i in range(len(tickers)):
                if ticker == tickers[i]:
                    idxs.append(i)

            print(idxs)
            for i in idxs:

                if actions[i] == 'SELL':
                    amounts[i] *= -1

                market_data = None
                while market_data is None:
                    try:
                        market_data, meta_data = ts.get_daily_adjusted(symbol='{}'.format(tickers[i]),
                                                                       outputsize='full')
                        # TODO: Once meta_data supports 'type' -> reflect in table
                    except:
                        pass
                        time.sleep(1)
                        # TODO: AlertDialog: "Could not retrieve data"

                market_then = market_data.loc[nearest(market_data.index.get_values(), dates[i])]['4. close']
                now = str(dt.date(dt.now()))
                market_now = market_data.loc[nearest(market_data.index.get_values(), now)]['4. close']

                if units[i] == 'SHARES':
                    value = amounts[i] * market_now
                    shares = amounts[i]
                    basis = amounts[i] * market_then / shares
                else:
                    shares = amounts[i] / market_then
                    value = shares * market_now
                    basis = amounts[i] / shares

                entry = {'date': dates[i], '{} shares'.format(ticker): shares}

                market_data = market_data.reset_index()
                graph_values = market_data['4. close']  # Change column name to {} value

                dict.append(entry)

            date_column = market_data['date']
            mass_dict.append(graph_values)

    df = pd.DataFrame(dict)
    try:
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='ignore')
        print(df.set_index('date').sort_index().fillna(value=0).cumsum())
        print(pd.DataFrame(zip(date_column, *mass_dict)))
    except:
        print('This messages gets rid of pesky panda key error')

    return dict


def get_market(ticker, date):
    data = None
    while data is None:
        try:
            data, meta_data = ts.get_daily_adjusted(symbol='{}'.format(ticker), outputsize='full')
            # TODO: Once meta_data supports 'type' -> reflect in table
        except:
            pass
            time.sleep(1)
            # TODO: AlertDialog: "Could not retrieve data"

    market = (data.loc[nearest(data.index.get_values(), date)]['4. close'])

    return market


# @app.callback(
#     Output('computed-table', 'data'),
#     [Input('order-table', 'data')],
#     [State('order-table', 'data_previous'),
#      State('computed-table', 'data')])
# def compute_positions(current_data, previous_data, comp_data):
#     tickers = [row.get('Ticker') for row in current_data]
#     actions = [row.get('Action') for row in current_data]
#     units = [row.get('Unit') for row in current_data]
#     amounts = [float(row.get('Amount')) for row in current_data]
#     dates = [row.get('Date') for row in current_data]
#     times = [row.get('Time') for row in current_data]
#
#     positions = [row.get('Position') for row in comp_data]
#     quantity = [row.get('Shares') for row in comp_data]
#     values = [row.get('Value') for row in comp_data]
#     basises = [row.get('Basis') for row in comp_data]
#     gain_losses = [row.get('GainLoss') for row in comp_data]
#
#     # TODO: Update in efficient way by evaluating changed data only (Significant Effort)
#     # if len(current_data) > 0 and previous_data is not None:
#     #     print(current_data)
#     #     for entry in range(len(current_data)):
#     #         if current_data[entry] != previous_data[entry]:
#     #             print(entry)
#
#     # All (slow)
#     temp_data = []
#
#     if len(current_data) > 0:
#         for i in range(len(current_data)):
#             print('Loading Computed Table...')
#             temp_positions = [row.get('Position') for row in temp_data]
#             temp_quantity = [row.get('Shares') for row in temp_data]
#             temp_values = [row.get('Value') for row in temp_data]
#             temp_basises = [row.get('Basis') for row in temp_data]
#             temp_gain_losses = [row.get('GainLoss') for row in temp_data]
#
#             observed = [tickers[i], actions[i], units[i], amounts[i], dates[i]]
#             # Will not evaluate the observed entry if it is missing information
#             if all(e is not None for e in observed) & (amounts[i] != 0):
#
#                 if actions[i] == 'SELL':
#                     amounts[i] *= -1
#
#                 market_then = get_market(tickers[i], dates[i])
#
#                 now = str(dt.date(dt.now()))
#
#                 market_now = get_market(tickers[i], now)
#
#                 if units[i] == 'SHARES':
#                     value = amounts[i] * market_now
#                     shares = amounts[i]
#                     basis = amounts[i] * market_then / shares
#                 else:
#                     shares = amounts[i] / market_then
#                     value = shares * market_now
#                     basis = amounts[i] / shares
#
#                 gain_loss = value - basis
#
#                 if len(positions) > 0:
#                     try:
#                         p = positions.index(tickers[i])
#                         values[p] += value
#                         quantity[p] += shares
#                         basises[p] += basis
#                         gain_losses[p] += gain_loss
#
#                         comp_data[p] = {'Position': positions[p], 'Type': 'Stock', 'Shares': quantity[p],
#                                         'Value': values[p], 'Basis': basis, 'GainLoss': gain_losses[p]}
#                     except:
#                         comp_data.append(
#                             {'Position': tickers[i], 'Type': 'Stock', 'Shares': shares, 'Value': value, 'Basis': basis,
#                              'GainLoss': gain_loss})
#
#                 else:
#                     try:
#                         p = temp_positions.index(tickers[i])
#                         temp_values[p] += value
#                         temp_quantity[p] += shares
#                         temp_basises[p] += basis
#                         temp_gain_losses[p] += gain_loss
#
#                         temp_data[p] = {'Position': temp_positions[p], 'Type': 'Stock', 'Shares': temp_quantity[p],
#                                             'Value': temp_values[p], 'Basis': temp_basises, 'GainLoss': temp_gain_losses[p]}
#                     except:
#                         temp_data.append(
#                             {'Position': tickers[i], 'Type': 'Stock', 'Shares': shares, 'Value': value, 'Basis': basis,
#                              'GainLoss': gain_loss})
#
#     comp_data.extend(temp_data)
#     return comp_data


################################################################################

# @app.callback(
#     Output('asset-distribution', 'figure'),
#     [Input('computed-table', 'data'),
#      Input('asset-distribution', 'hoverData')]
# )
# def update_pie(rows, hoverdata):
#     positions = [row.get('Position') for row in rows]
#     shares = [row.get('Shares') for row in rows]
#     values = [row.get('Value') for row in rows]
#
#     selected_position = None
#     if hoverdata:
#         selected_position = hoverdata['points'][0]['label']
#
#     pull = np.zeros(len(positions))
#     for p in range(len(positions)):
#         if selected_position == positions[p]:
#             pull[p] = .05
#         else:
#             pull[p] = 0
#
#     pie = go.Pie(values=values,
#                  labels=positions,
#                  hoverinfo="label+percent+name",
#                  hole=.5,
#                  pull=pull,
#                  rotation=0  # -360 : +360
#                  )
#
#     layout = go.Layout(title="Asset Distribution",
#                        width=1000,
#                        height=1000,
#                        annotations=[
#                            dict(
#                                font=dict(size=40),
#                                showarrow=False,
#                                text="Total: ${}".format(round(float(np.sum(np.array(values))), 2)),
#                                x=.50,
#                                y=.50,
#                            ), ],
#                        )
#
#     data = [pie]
#     fig = go.Figure(data=data, layout=layout)
#     return fig


if __name__ == '__main__':
    # Production
    # app.server.run(debug=True, threaded=True)

    # Development
    app.run_server(debug=True)
