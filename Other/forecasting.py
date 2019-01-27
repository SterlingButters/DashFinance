import dash
import sd_material_ui
import dash_core_components as dcc
import dash_table
import dash_html_components as html
from dash.dependencies import Output, State, Input

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances

import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime as dt

ts = TimeSeries(key='9IDB37CDHYIC07UE', output_format='pandas', indexing_type='integer') # indexing_type='integer')

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

data, meta_data = ts.get_daily(symbol='AAPL', outputsize='full')

app.layout = html.Div([
    dcc.Graph(id='forecast'),
    dcc.RangeSlider(id='slider',
                    min=0,
                    max=len(data)-1,
                    value=[100, len(data)/2, len(data)-1],
                    pushable=2),
])


@app.callback(Output('forecast', 'figure'),
              [Input('slider', 'value')])
def forecast(values):
    x1, x2, x3 = values
    y1, y2, y3 = data['4. close'][values]
    horizon = 200
    x = np.arange(0, len(data)+horizon)
    TERM1 = ((x - x2)*(x - x3)) / ((x1 - x2)*(x1 - x3)) * y1
    TERM2 = ((x - x1)*(x - x3)) / ((x2 - x1)*(x2 - x3)) * y2
    TERM3 = ((x - x1)*(x - x2)) / ((x3 - x1)*(x3 - x2)) * y3
    TOTAL = TERM1 + TERM2 + TERM3

    trace1 = go.Scatter(x=data['date'],
                        y=data['4. close'],
                        mode='lines',
                        line=dict(
                            width=1,
                            color='rgb(150, 150, 150)'
                        ),
                        name=''
                        )

    trace2 = go.Scatter(x=data['date'][values],
                        y=[y1, y2, y3],
                        mode='markers',
                        )


    df = pd.to_datetime(data['date'])
    period = pd.Series([(df.iloc[-1] + dt.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, horizon)])
    test = np.array(data['date'].append(period))

    trace3 = go.Scatter(x=test[:x1:-1],
                        y=TOTAL[:x1:-1],
                        mode='lines',
                        line=dict(
                            width=1,
                            color='rgb(150, 150, 150)'
                        ),
                        name=''
                        )
    # https://plot.ly/python/filled-area-plots/
    # trace4 = go.Scatter(x=test[:x1:-1],
    #                     y=,
    #                     mode='lines',
    #                     line=dict(
    #                         width=1,
    #                     ),
    #                     fill='tonexty',
    #                     name=''
    #                     )
    #
    # trace5 = go.Scatter(x=test[:x1:-1],
    #                     y=,
    #                     mode='lines',
    #                     line=dict(
    #                         width=1,
    #                     ),
    #                     fill='tonexty',
    #                     name=''
    #                     )


    layout = go.Layout(
        width=1250,
        height=750,
        yaxis=dict(
            title='',
        ),

    )
    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)