# https://plaid.com/docs/#exchange-token-flow
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
import dash
import json
import plaid
import sd_material_ui
from pdf2image import convert_from_bytes

import os
from flask import jsonify
import base64
import plaidash
import datetime
import time

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=stylesheet)
app.config['suppress_callback_exceptions'] = True

with open('/Users/sterlingbutters/.plaid/.credentials.json') as CREDENTIALS:
    KEYS = json.load(CREDENTIALS)
    print(json.dumps(KEYS, indent=2))

    PLAID_CLIENT_ID = KEYS['client_id']
    PLAID_PUBLIC_KEY = KEYS['public_key']
    ENV = 'sandbox'
    if ENV == 'development':
        PLAID_SECRET = KEYS['development_secret']
    else:
        PLAID_SECRET = KEYS['sandbox_secret']
    PLAID_ENV = os.getenv('PLAID_ENV', ENV)
    PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', ['auth', 'transactions', 'assets', 'income'])
    # 'identity` premium only / 'balance' & 'credit_details' deprecated?


def pretty_response(response):
    return json.dumps(response, indent=2, sort_keys=True)


def format_error(e):
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type} }


app.layout = html.Div([
    # Will lose the data when browser/tab closes.
    dcc.Store(id='public-tokens', storage_type='session', data={'tokens': []}),
    # TODO: Handle Expired Tokens (30 min)
    # TODO: Save credentials and LiveUpdate
    dcc.Dropdown(id='institution-dropdown'),
    plaidash.LoginForm(
                      id='plaid-link',
                      clientName='Butters',
                      env=PLAID_ENV,
                      publicKey=PLAID_PUBLIC_KEY,
                      product=PLAID_PRODUCTS,
                      # institution=)
            ),
    html.Button('Store current token', id='store-button'), # TODO: Disable until token available
    sd_material_ui.Snackbar(id='token-alert', open=False, message='Token Added to Dropdown', action='Select It'),
    sd_material_ui.Paper([html.Div(id='transaction-table')])
])

client = plaid.Client(client_id=PLAID_CLIENT_ID,
                      secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY,
                      environment=PLAID_ENV,
                      api_version='2018-05-22')


##################################################################
# Commit to Memory
@app.callback(Output('public-tokens', 'data'),
              [Input('store-button', 'n_clicks')],
              [State('plaid-link', 'public_token'),
               State('public-tokens', 'data')])
def on_click(clicks, public_token, data):
    if clicks is None:
        raise PreventUpdate

    stored_tokens = data['tokens'] or []
    if public_token is not None and public_token not in stored_tokens:
        stored_tokens.append(public_token)
    data = {'tokens': stored_tokens}

    return data


# Alert User of new Token in Snackbar
@app.callback(
    Output('token-alert', 'open'),
    [Input('store-button', 'n_clicks')],
    [State('public-tokens', 'data')])
def open_snackbar(click: int, data):
    stored_tokens = data['tokens']
    if click is not None and click > 0 and len(stored_tokens)>=1:
        return True
    else:
        return False


# Select newest token in DropDown for user
@app.callback(
    Output('institution-dropdown', 'value'),
    [Input('token-alert', 'n_clicks')],
    [State('public-tokens', 'data')])
def click_snackbar(snackbar_click: int, data):
    stored_tokens = data['tokens']
    if snackbar_click is not None and snackbar_click > 0:
        return stored_tokens[-1]


##################################################################
# Create Options
@app.callback(Output('institution-dropdown', 'options'),
              [Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data')])
def create_dropdown(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    data = data or {}
    STORED_TOKENS = data.get('tokens')

    options = []
    for token in STORED_TOKENS:
        options.append({'label': '{}'.format(token), 'value': '{}'.format(token)})

    return options


# Display Transactions from Token Memory
@app.callback(Output('transaction-table', 'children'),
              [Input('institution-dropdown', 'value')],
)
def display_transactions(public_token):
    if public_token is None:
        return "Navigate Plaid Link to Obtain Token"
    else:
        ######################### Tokens #############################
        access_token = client.Item.public_token.exchange(public_token)['access_token']
        print("Public Token '{}' was exchanged for Access Token '{}'".format(public_token, access_token))

        ######################### Tokens #############################

        ######################### Transactions #############################
        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

        try:
            transaction_response = client.Transactions.get(
                access_token=access_token, start_date=start_date, end_date=end_date)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        # print(pretty_response(transaction_response))

        transactions = transaction_response.get('transactions')

        names = [transaction['name'] for transaction in transactions]
        categories = [transaction['category'] for transaction in transactions]
        locations = [transaction['location'] for transaction in transactions]
        statuses = [transaction['pending'] for transaction in transactions]
        amounts = [transaction['amount'] for transaction in transactions]
        # Payment Method: payment_meta
        dates = [transaction['date'] for transaction in transactions]
        id = [transaction['transaction_id'] for transaction in transactions]

        TRANSACTION_MEAT = []
        for b in range(len(transactions)):
            TRANSACTION_MEAT.append(html.Tr([html.Td(names[b]), html.Td(amounts[b]),
                                             html.Td(dates[b]), html.Td(categories[b]),
                                             html.Td(statuses[b]),
                                             # html.Td(locations[b],
                                            ]))

        TRANSACTIONS = html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th('Name'),
                            html.Th('Amount'),
                            html.Th('Date'),
                            html.Th('Category'),
                            # html.Th('Location'),
                            html.Th('Pending')
                        ])
                    ]),
                    html.Tbody([
                        *TRANSACTION_MEAT,
                    ])
                ])
            ])
        ######################### Transactions #############################

        ######################### CreditDetails #############################
        try:
            credit_response = client.CreditDetails.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        print(pretty_response(credit_response))

        credit_details = credit_response.get('credit_details')[0] # TODO: Will list ever contain 2nd dict?
        credits = credit_details.get('aprs')

        balance_transfers = credits.get('balance_transfers')

        cash_advances = credits.get('cash_advances')
        purchases = credits.get('purchases')

        balance_transfer_aprs = [balance_transfer['apr'] for balance_transfer in balance_transfers] if type(balance_transfers)==list else balance_transfers['apr']
        balance_transfer_subject_to_apr = [balance_transfer['balance_subject_to_apr'] for balance_transfer in
                                           balance_transfers] if type(balance_transfers)==list else balance_transfers['balance_subject_to_apr']
        balance_transfer_interests = [balance_transfer['interest_charge_amount'] for balance_transfer in
                                      balance_transfers] if type(balance_transfers)==list else balance_transfers['interest_charge_amount']

        cash_advance_aprs = [cash_advance['apr'] for cash_advance in cash_advances] if type(cash_advances)==list else cash_advances['apr']
        cash_advance_subject_to_apr = [cash_advance['balance_subject_to_apr'] for cash_advance in cash_advances] if type(cash_advances)==list else cash_advances['balance_subject_to_apr']
        cash_advance_interests = [cash_advance['interest_charge_amount'] for cash_advance in cash_advances] if type(cash_advances)==list else cash_advances['balance_subject_to_apr']

        purchase_aprs = [purchase['apr'] for purchase in purchases] if type(purchases)==list else purchases['apr']
        purchase_subject_to_apr = [purchase['balance_subject_to_apr'] for purchase in purchases] if type(purchases)==list else purchases['balance_subject_to_apr']
        purchase_interests = [purchase['interest_charge_amount'] for purchase in purchases] if type(purchases)==list else purchases['interest_charge_amount']

        last_payment_amount = credit_details.get('last_payment_amount')
        last_payment_date = credit_details.get('last_payment_date')
        last_statement_balance = credit_details.get('last_statement_balance')
        last_statement_date = credit_details.get('last_statement_date')
        minimum_payment_amount = credit_details.get('minimum_payment_amount')
        next_bill_due_date = credit_details.get('next_bill_due_date')

        TRANSFER_MEAT = []
        if type(balance_transfers) == list:
            for d in range(len(balance_transfers)):
                TRANSFER_MEAT.append(html.Tr([html.Td(balance_transfer_aprs[d]),
                                              html.Td(balance_transfer_subject_to_apr[d]),
                                              html.Td(balance_transfer_interests[d])]))
        else:
            TRANSFER_MEAT.append(html.Tr([html.Td(balance_transfer_aprs),
                                          html.Td(balance_transfer_subject_to_apr),
                                          html.Td(balance_transfer_interests)]))

        ADVANCE_MEAT = []
        if type(cash_advances) == list:
            for e in range(len(cash_advances)):
                ADVANCE_MEAT.append(html.Tr([html.Td(cash_advance_aprs[e]),
                                             html.Td(cash_advance_subject_to_apr[e]),
                                             html.Td(cash_advance_interests[e])]))
        else:
            ADVANCE_MEAT.append(html.Tr([html.Td(cash_advance_aprs),
                                         html.Td(cash_advance_subject_to_apr),
                                         html.Td(cash_advance_interests)]))

        PURCHASE_MEAT = []
        if type(purchases) == list:
            for f in range(len(purchases)):
                PURCHASE_MEAT.append(html.Tr([html.Td(purchase_aprs[f]),
                                              html.Td(purchase_subject_to_apr[f]),
                                              html.Td(purchase_interests[f])]))
        else:
            PURCHASE_MEAT.append(html.Tr([html.Td(purchase_aprs),
                                              html.Td(purchase_subject_to_apr),
                                              html.Td(purchase_interests)]))

        CREDITS = html.Div([
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Balance Transfer APR %\'s'),
                        html.Th('Balance Transfer Amount Subject to APR'),
                        html.Th('Balance Transfer Interest Amount'),
                    ])
                ]),
                html.Tbody([
                    *TRANSFER_MEAT,
                ])
            ]),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Cash Advance APR %\'s'),
                        html.Th('Cash Advance Amount Subject to APR'),
                        html.Th('Cash Advance Interest Amount'),
                    ])
                ]),
                html.Tbody([
                    *ADVANCE_MEAT,
                ])
            ]),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Purchase APR %\'s'),
                        html.Th('Purchase Amount Subject to APR'),
                        html.Th('Purchase Interest Amount'),
                    ])
                ]),
                html.Tbody([
                    *PURCHASE_MEAT,
                ])
            ]),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Amount of Last Payment'),
                        html.Th('Date of Last Payment'),
                        html.Th('Last Statement Balance'),
                        html.Th('Last Statement Date'),
                        html.Th('Minimum Payment Due'),
                        html.Th('Next Bill Due Date'),
                    ])
                ]),
                html.Tbody([
                    html.Td(last_payment_amount),
                    html.Td(last_payment_date),
                    html.Td(last_statement_balance),
                    html.Td(last_statement_date),
                    html.Td(minimum_payment_amount),
                    html.Td(next_bill_due_date),
                ])
            ])
        ])
        ######################### CreditDetails #############################

        ######################### Auth ############################# TODO: Account Names
        try:
            auth_response = client.Auth.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        accounts_ach = auth_response.get('numbers').get('ach')
        accounts_eft = auth_response.get('numbers').get('eft')

        account_numbers = [account['account'] for account in accounts_ach]
        routing_numbers = [account['routing'] for account in accounts_ach]
        wire_numbers = [account['wire_routing'] for account in accounts_ach]

        account_numbers.extend([account['routing'] for account in accounts_eft])
        routing_numbers.extend([account['routing'] for account in accounts_eft])
        wire_numbers.extend([account['routing'] for account in accounts_eft])

        # print(auth_response)

        ACCOUNT_MEAT = []
        for c in range(len(accounts_ach)+len(accounts_eft)):
            ACCOUNT_MEAT.append(html.Tr([html.Td(account_numbers[c]),
                                         html.Td(routing_numbers[c]),
                                         ]))

        ACCOUNTS = html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th('Account #'),
                            html.Th('Routing #'),
                        ])
                    ]),
                    html.Tbody([
                        *ACCOUNT_MEAT,
                    ])
                ])
            ])
        ######################### Auth #############################

        ######################### Balance #############################
        try:
            balance_response = client.Accounts.balance.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        # print(balance_response)
        ######################### Balance #############################

        ######################### Income #############################
        try:
            income_response = client.Income.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        income_streams = income_response.get('income').get('income_streams')

        income_names = [income['name'] for income in income_streams]
        income_permonth = [income['monthly_income'] for income in income_streams]
        income_days = [income['days'] for income in income_streams]
        income_confidence = [income['confidence'] for income in income_streams]
        income_lastyear = income_response.get('income').get('last_year_income')

        # print(income_response)

        INCOME_MEAT = []
        for b in range(len(income_streams)):
            INCOME_MEAT.append(html.Tr([html.Td(income_names[b]), html.Td(income_permonth[b]),
                                        html.Td(income_days[b]), html.Td(income_confidence[b])]))

        INCOME = html.Div([
                    html.Table([
                        html.Thead([
                            html.Tr([
                                html.Th('Name'),
                                html.Th('Monthly Income'),
                                html.Th('Days'),
                                html.Th('Confidence')
                            ])
                        ]),
                        html.Tbody([
                            *INCOME_MEAT,
                            html.Tr([html.Td(''), html.Td(''),
                                     html.Td('Est. Income Last Year'), html.Td(income_lastyear)])
                        ])
                    ])
                ])
        ######################### Income #############################

        ######################### AssetReport ############################# Finicky
        try:
            asset_report_create_response = client.AssetReport.create([access_token], 10)
        except plaid.errors.PlaidError as e:
            return jsonify(
                {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}})

        print(pretty_response(asset_report_create_response))

        asset_report_token = asset_report_create_response['asset_report_token']

        # Poll for the completion of the Asset Report.
        num_retries_remaining = 20
        asset_report_json = None
        while num_retries_remaining > 0:
            try:
                asset_report_get_response = client.AssetReport.get(asset_report_token)
                asset_report_json = asset_report_get_response['report']
                break
            except plaid.errors.PlaidError as e:
                if e.code == 'PRODUCT_NOT_READY':
                    num_retries_remaining -= 1
                    time.sleep(1)
                    continue
                return jsonify(
                    {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}})

        if asset_report_json is None:
            return jsonify({'error': {'display_message': 'Timed out when polling for Asset Report',
                                      'error_code': e.code, 'error_type': e.type}})

        asset_report_pdf = None
        try:
            asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
        except plaid.errors.PlaidError as e:
            return jsonify(
                {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}})

        # TODO: Get pdf
        # encoded_image = convert_from_bytes(open(asset_report_pdf, "rb").read())
        # asset_report_png = encoded_image.save("asset_report.png", "PNG")
        # report_file = 'asset_report.png'
        # file_base64 = base64.b64encode(open(report_file, 'rb').read()).decode('ascii')
        # PDF = html.Img(src='data:image/png;base64,{}'.format(file_base64)),
        ######################### AssetReport #############################

        return html.Div([
                         TRANSACTIONS, html.Br(),
                         INCOME, html.Br(),
                         ACCOUNTS, html.Br(),
                         CREDITS, html.Br(),
                         # PDF
                         ])


##################################################################


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
