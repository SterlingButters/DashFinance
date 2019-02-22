import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import dash_daq as daq

from app import app

layout = html.Div([

    html.H2('Financial Calculators',
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
              html.P('''Below will evaluate a loan and create an amortization
              schedule'''), ]),

    daq.NumericInput(
        id='loan-amount',
        value=10,
        size=120
    ),
    daq.NumericInput(
        id='loan-term',
        value=10,
        size=120
    ),
    dcc.Slider(id='loan-rate'),
    html.Div(style=dict(height=20)),
    dash_table.DataTable(
        id='amortization-schedule',
        columns=[
            {'name': 'Date', 'id': 'Date'},
            {'name': 'Payment', 'id': 'Payment'},
            {'name': 'Principal', 'id': 'Principal'},
            {'name': 'Interest', 'id': 'Interest'},
            {'name': 'Cumulative Interest', 'id': 'CumInterest'},
            {'name': 'Balance', 'id': 'Balance'},
        ],
        data=[],
    ),
])

