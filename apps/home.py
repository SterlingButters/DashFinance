import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import sd_material_ui

from app import app

layout = html.Div([
    html.H1('Welcome Home'),
    sd_material_ui.FlatButton(id='open-left-drawer', label='Navigate'),
    sd_material_ui.Drawer(id='left-drawer', width='40%', docked=False,
                          children=html.Div([
                                dcc.Link('Bank Accounts', href='/apps/bank_accounts'),
                                html.Div(style={'height': 20}),
                                dcc.Link('Market Research', href='/apps/market_research'),
                                html.Div(style={'height': 20}),
                                dcc.Link('Virtual Portfolio', href='/apps/virtual_portfolio'),
                                html.Div(style={'height': 20}),

                              # sd_material_ui.FlatButton(
                                #     id='bank-link', labelPosition='before', fullWidth=True,
                                #     label='Bank Accounts',
                                #     href='/apps/bank_accounts',
                                #     style={'height': '80'},
                                #     ),
                                # sd_material_ui.FlatButton(
                                #     id='research-link', labelPosition='before', fullWidth=True,
                                #     label='Market Research',
                                #     href='/apps/market_research',
                                #     style={'height': '80'},
                                #     ),
                                # sd_material_ui.FlatButton(
                                #     id='portfolio-link', labelPosition='before', fullWidth=True,
                                #     label='Virtual Portfolio',
                                #     href='/apps/virtual_portfolio',
                                #     style={'height': '80'},
                                #     ),
                                # sd_material_ui.FlatButton(
                                #     id='calculatos-link', labelPosition='before', fullWidth=True,
                                #     label='Financial Calculators',
                                #     href='/apps/calculators',
                                #     style={'height': '100'},
                                #     ),
                          ])),
])


@app.callback(
     Output('left-drawer', 'open'),
    [Input('open-left-drawer', 'n_clicks')], )
def display_clicks_flat(open_clicks: int):
    if open_clicks is not None:
        if open_clicks % 2 == 0:
            return False
        else:
            return True
