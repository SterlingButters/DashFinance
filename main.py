import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask
import os
from random import randint

from apps import bank_accounts, market_research, virtual_portfolio, financial_calculators

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/bank_accounts':
        return bank_accounts.layout
    elif pathname == '/apps/market_research':
        return market_research.layout
    elif pathname == '/apps/virtual_portfolio':
        return virtual_portfolio.layout
    elif pathname == '/apps/financial_calculators':
        return financial_calculators.layout
    else:
        return '404'


if __name__ == '__main__':
    # Production
    # app.server.run(debug=True, threaded=True)

    # Development
    app.run_server(debug=True)
