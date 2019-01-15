from typing import Dict, List, Any

import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go
import pandas as pd
# pd.set_option('display.max_columns', 500)

from datetime import datetime as dt
import numpy as np
import random
import time

import json

from alpha_vantage.timeseries import TimeSeries
ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas')

# TODO
df_symbol = pd.read_csv('tickers.csv')

################################################################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.layout = html.Div([

    # Title
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
        start_date_placeholder_text='Start Date',
        max_date_allowed=dt.date(dt.today()),
        end_date=dt.date(dt.today()),
        calendar_orientation='vertical',
    ),

    html.Div(id='debug'),

    html.Br(),

    html.Div(id='market-graph'),

    dash_table.DataTable(
        id='order-table',
        columns=(
            [{'id': 'Ticker', 'name': 'Ticker', 'type': 'dropdown'},
             {'id': 'Action', 'name': 'Action', 'type': 'dropdown'},
             {'id': 'Unit', 'name': 'Unit', 'type': 'dropdown'}, # Check 'number'
             {'id': 'Amount', 'name': 'Amount'},
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
            {'name': 'Est Gain/Loss', 'id': 'Gain-Loss'},
        ],
        data=[],
    ),

    dcc.Graph(
        id='asset-distribution',
    ),

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

    for ticker in tickers:
        data = None
        while data is None:
            try:
                data, meta_data = ts.get_daily_adjusted(symbol='{}'.format(ticker), outputsize='full')

            except:
                pass
                time.sleep(5)

        data = data.reset_index()

        period = data.loc[(data['date'] >= startdate) & (data['date'] < enddate)]
        data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d', )

        candlesticks = go.Ohlc(x=period['date'],
                        open=period['1. open'],
                        high=period['2. high'],
                        low=period['3. low'],
                        close=period['4. close'])

        volume = go.Bar(x=period['date'],
                        y=period['6. volume'],
                        yaxis='y2',
                        marker=dict(
                            color='rgb(204,204,204)'),
                        opacity=.3)

        layout = go.Layout(
                title='{}'.format(ticker),
                width=1250,
                height=750,
                xaxis = dict(),
                yaxis=dict(
                    title='Value $',
                    # anchor='free'
                ),
                yaxis2=dict(
                    title='Volume',
                    # titlefont=dict(
                    #     color='rgb(148, 103, 189)'
                    # ),
                    # tickfont=dict(
                    #     color='rgb(148, 103, 189)'
                    # ),
                    overlaying='y',
                    side='right'
                )
            )

        fig = go.Figure(data=[candlesticks, volume], layout=layout)

        graphs.append(dcc.Graph(figure=fig))

    return graphs


################################################################################
@app.callback(
    Output('order-table', 'data'),
    [Input('add-order-button', 'n_clicks')],
    [State('order-table', 'data'),
     State('order-table', 'columns'),
     State('order-date', 'date')])
def add_row(n_clicks, rows, columns, date):

    if n_clicks > 0:
        rows.append({'Amount': 0, 'Date': str(date), 'Time': '-'})

    return rows

##########################################


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
    equities = [row.get('Equity') for row in comp_rows]
    gain_losses = [row.get('Gain-Loss') for row in comp_rows]

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
                equity = amounts[-1]*market_then
                value = amounts[-1]*market_now
                shares = amounts[-1]
            else:
                equity = amounts[-1]
                shares = amounts[-1]/market_then
                value = shares*market_now

            gain_loss = value - equity

            if len(positions) > 0:
                for p in range(len(positions)):
                    if positions[p] == tickers[-1]:
                        values[p] += value
                        quantity[p] += shares
                        equities[p] += equity
                        gain_losses[p] += gain_loss

                        comp_rows[p] = {'Position': positions[p], 'Type': 'Stock', 'Shares': quantity[p], 'Value': values[p], 'Equity': equity, 'Gain-Loss': gain_losses[p]}

                    # TODO: Appending for p in range... find idx of position and change that way i.e. no need to cycle thru
                    else:
                        comp_rows.append({'Position': tickers[-1], 'Type': 'Stock', 'Shares': shares, 'Value': value, 'Equity': equity, 'Gain-Loss': gain_loss})
            else:
                comp_rows.append({'Position': tickers[-1], 'Type': 'Stock', 'Shares': shares, 'Value': value, 'Equity': equity, 'Gain-Loss': gain_loss})

    return comp_rows


################################################################################



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
               name="Institution",
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
                             text="Institution",
                             x=.50,
                             y=.50,
                         ),],
                     )

    data=[pie]

    fig = go.Figure(data=data, layout=layout)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)