import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from apps import bank_accounts, market_research, virtual_portfolio, financial_calculators
from app import app

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
    # elif pathname == '/apps/financial_calculators':
    #     return financial_calculators.layout
    else:
        return html.H1('404 Page Not Found')


if __name__ == '__main__':
    # Production
    # app.server.run(debug=True, threaded=True)

    # Development
    app.run_server(debug=True)
