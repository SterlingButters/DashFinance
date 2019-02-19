# https://plaid.com/docs/#exchange-token-flow
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import dash_html_components as html
import dash_core_components as dcc
import json
import plaid
import sd_material_ui
from pdf2image import convert_from_bytes

import os
import numpy as np
from flask import jsonify
import plaidash
import datetime
import time

from app import app

with open('/Users/sterlingbutters/.plaid/.credentials.json') as CREDENTIALS:
    KEYS = json.load(CREDENTIALS)
    # print(json.dumps(KEYS, indent=2))

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
    dcc.Store(id='public-tokens', storage_type='session', data={'tokens': [], 'institutions': []}),
    # TODO: Handle Expired Tokens (30 min)
    # TODO: Save credentials and LiveUpdate (credentials retrieved from client.Institutions.get_by_id(auth_response.get('item')...
    dcc.Dropdown(id='institution-dropdown'),
    # TODO: Use stepper to reveal corresponding children
    sd_material_ui.Stepper(
        id='use-guide',
        activeStep=0,
        finishedText='Institution Added! Restart?',
        stepCount=3,
        stepLabels=['Open Plaid Link', 'Store Token', 'Select From Dropdown']
    ),
    plaidash.LoginForm(
        id='plaid-link',
        clientName='Butters',
        env=PLAID_ENV,
        publicKey=PLAID_PUBLIC_KEY,
        product=PLAID_PRODUCTS,
        # institution=)
    ),
    html.Button('Store current token', id='store-button'),
    sd_material_ui.Snackbar(id='token-alert', open=False, message='Token Added to Dropdown', action='Select It'),
    html.H1('Accounts & Balances', style=dict()),
    html.Div(id='auth-container'),
    html.H1('Credit & Loans', style=dict()),
    html.Div(id='credit-container'),
    html.H1('Transactions & Spending', style=dict()),
    html.Div(id='transaction-container'),
    html.H1('Income & Cash Flow', style=dict()),
    html.Div(id='income-container'),
    html.H1('Assets & Property', style=dict()),
    html.Div(id='asset-container'),
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
    stored_institutions = data['institutions'] or []

    if public_token is not None and public_token not in stored_tokens:
        stored_tokens.append(public_token)

        access_token = client.Item.public_token.exchange(public_token)['access_token']
        try:
            auth_response = client.Auth.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        institution = client.Institutions.get_by_id(auth_response.get('item')['institution_id']).get('institution')['name']
        stored_institutions.append(institution)

    data = {'tokens': stored_tokens, 'institutions': stored_institutions}

    return data


# Alert User of new Token in Snackbar
@app.callback(
    Output('token-alert', 'open'),
    [Input('store-button', 'n_clicks')],
    [State('public-tokens', 'data')])
def open_snackbar(click: int, data):
    stored_tokens = data['tokens']
    if click is not None:
        if click > 0 and len(stored_tokens) >= 1:
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


# Populate Dropdown from Memory
@app.callback(Output('institution-dropdown', 'options'),
              [Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data')])
def create_dropdown(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    data = data or {}
    STORED_TOKENS = data.get('tokens')
    STORED_INSTITUTIONS = data.get('institutions')

    options = []
    if STORED_TOKENS is not None:
        for t in range(len(STORED_TOKENS)):
            options.append({'label': '{}'.format(STORED_INSTITUTIONS[t]), 'value': '{}'.format(STORED_TOKENS[t])})

    return options


######################### Auth/Balance #############################
# Display Transactions from Token Memory
@app.callback(Output('auth-container', 'children'),
              [Input('institution-dropdown', 'value')],
)
def display_auth(public_token):
    if public_token is None:
        return "Navigate Plaid Link to Obtain Token"
    else:
        access_token = client.Item.public_token.exchange(public_token)['access_token']
        print("Public Token '{}' was exchanged for Access Token '{}'".format(public_token, access_token))

        try:
            auth_response = client.Auth.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        # print(pretty_response(auth_response))

        accounts = auth_response.get('accounts')
        balances = [account['balances'] for account in accounts]

        ids = [account['account_id'] for account in accounts]
        availables = [balance['available'] for balance in balances] if type(balances)==list else balances['available']
        currents = [balance['current'] for balance in balances] if type(balances)==list else balances['current']
        currencies = [balance['iso_currency_code'] for balance in balances] if type(balances)==list else balances['iso_currency_code']
        limits = [balance['limit'] for balance in balances] if type(balances)==list else balances['limit']

        masks = [account['mask'] for account in accounts]
        account_names = [account['name'] for account in accounts]
        official_names = [account['official_name'] for account in accounts]
        subtypes = [account['subtype'] for account in accounts]
        types = [account['type'] for account in accounts]

        accounts_ach = auth_response.get('numbers').get('ach')
        accounts_eft = auth_response.get('numbers').get('eft')

        # ACH Accounts
        account_numbers = [account['account'] for account in accounts_ach]
        routing_numbers = [account['routing'] for account in accounts_ach]
        wire_numbers = [account['wire_routing'] for account in accounts_ach]

        # EFT Accounts
        account_numbers.extend([account['routing'] for account in accounts_eft])
        routing_numbers.extend([account['routing'] for account in accounts_eft])
        wire_numbers.extend([account['routing'] for account in accounts_eft])

        # print(pretty_response(auth_response))

        ACCOUNT_MEAT = []
        for c in range(len(accounts_ach) + len(accounts_eft)):
            ACCOUNT_MEAT.append(html.Tr([html.Td('{}/{}'.format(account_numbers[c], routing_numbers[c])),
                                         html.Td('{}/{}'.format(account_names[c], official_names[c])),
                                         html.Td('{}/{}'.format(types[c], subtypes[c])),
                                         html.Td('{}'.format(currents[c])),
                                         html.Td('{}/{}'.format(availables[c], limits[c])),
                                         html.Td('{}/{}'.format(masks[c], currencies[c]))
                                         ]))

        ACCOUNTS = html.Div([
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Account/Routing #'),  # Account/Routing
                        html.Th('Account'),            # Nickname/Official
                        html.Th('Type'),               # Subtype/Type
                        html.Th('Current Amount'),     # Current
                        html.Th('Available/Limit'),    # Available/Limit
                        html.Th('Mask/Currency'),      # Mask/Currency
                    ])
                ]),
                html.Tbody([
                    *ACCOUNT_MEAT,
                ])
            ])
        ])

        return ACCOUNTS
######################### Auth/Balance #############################


######################### Transactions #############################
# TODO: Add DatePicker for transaction history
@app.callback(Output('transaction-container', 'children'),
              [Input('institution-dropdown', 'value')],
)
def display_transactions(public_token):
    if public_token is None:
        return "Navigate Plaid Link to Obtain Token"
    else:
        access_token = client.Item.public_token.exchange(public_token)['access_token']

        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

        try:
            transaction_response = client.Transactions.get(
                access_token=access_token, start_date=start_date, end_date=end_date)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        # print(pretty_response(transaction_response))

        transactions = transaction_response.get('transactions')

        id = [transaction['transaction_id'] for transaction in transactions]
        transaction_names = [transaction['name'] for transaction in transactions]
        categories = [transaction['category'] for transaction in transactions]
        locations = [transaction['location'] for transaction in transactions]
        statuses = [transaction['pending'] for transaction in transactions]
        amounts = [transaction['amount'] for transaction in transactions]
        dates = [transaction['date'] for transaction in transactions]
        # Payment Method: payment_meta

        TRANSACTION_MEAT = []
        for b in range(len(transactions)):
            TRANSACTION_MEAT.append(html.Tr([html.Td(transaction_names[b]), html.Td(amounts[b]),
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
                            html.Th('Pending')
                            # html.Th('Location'),
                        ])
                    ]),
                    html.Tbody([
                        *TRANSACTION_MEAT,
                    ])
                ])
            ])

        transactions = go.Pie(labels=categories, values=amounts,
                              hole=.3,
                              )
        layout = dict(title='Categorical Spending')
        transaction_pie = go.Figure(data=[transactions], layout=layout)
        CATEGORY_SPENDING = dcc.Graph(figure=transaction_pie)

        spending = go.Scatter(x=dates[::-1],
                              y=np.cumsum(amounts[::-1]),
                              fill='tozeroy')
        layout2 = dict()
        spending_plot = go.Figure(data=[spending], layout=layout2)
        TIME_SPENDING = dcc.Graph(figure=spending_plot)

        spent_bar = go.Bar(
            x=[category[0] for category in categories],
            y=amounts,
            name='Spent'
        )
        budget_bar = go.Bar(
            x=[category[0] for category in categories], # Since categories are like this: ['Recreation', 'Gyms and Fitness Centers']
            y=2*np.array(amounts),
            name='Budgeted'
        )

        data = [spent_bar, budget_bar]
        layout = go.Layout(
            barmode='stack'
        )

        budget_plot = go.Figure(data=data, layout=layout)
        BUDGETS = dcc.Graph(figure=budget_plot)

        return html.Div([TRANSACTIONS, CATEGORY_SPENDING, TIME_SPENDING,
                         html.H1('Budget & Bills', style=dict()),
                         BUDGETS])
######################### Transactions #############################


######################### Income #############################
@app.callback(Output('income-container', 'children'),
              [Input('institution-dropdown', 'value')],
              )
def display_income(public_token):
    if public_token is None:
        return "Navigate Plaid Link to Obtain Token"
    else:
        access_token = client.Item.public_token.exchange(public_token)['access_token']
        try:
            income_response = client.Income.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        income_streams = income_response.get('income').get('income_streams')

        income_names = [income['name'] for income in income_streams]
        income_permonth = [income['monthly_income'] for income in income_streams]
        income_days = [income['days'] for income in income_streams]
        income_confidences = [income['confidence'] for income in income_streams]
        income_lastyear = income_response.get('income').get('last_year_income')

        # print(pretty_response(income_response))

        INCOME_MEAT = []
        for b in range(len(income_streams)):
            INCOME_MEAT.append(html.Tr([html.Td(income_names[b]), html.Td(income_permonth[b]),
                                        html.Td(income_days[b]), html.Td(income_confidences[b])]))

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

        incomes = go.Pie(labels=income_names, values=income_permonth,
                         hole=.3,
                         text=['Confidence: {}'.format(confidence) for confidence in income_confidences])
        layout = dict(title='Categorical Income')
        transaction_pie = go.Figure(data=[incomes], layout=layout)
        CATEGORY_INCOME = dcc.Graph(figure=transaction_pie)

        return html.Div([INCOME, CATEGORY_INCOME])
######################### Income #############################


######################### CreditDetails #############################
@app.callback(Output('credit-container', 'children'),
              [Input('institution-dropdown', 'value')],
              )
def display_credit(public_token):
    if public_token is None:
        return "Navigate Plaid Link to Obtain Token"
    else:
        access_token = client.Item.public_token.exchange(public_token)['access_token']

        try:
            credit_response = client.CreditDetails.get(access_token=access_token)

        except plaid.errors.PlaidError as e:
            return html.P('There was an error: {}'.format(format_error(e)))

        # print(pretty_response(credit_response))

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

        return CREDITS
######################### CreditDetails #############################


######################### AssetReport #############################
@app.callback(Output('asset-container', 'children'),
              [Input('institution-dropdown', 'value')],
)
def display_transactions(public_token):
    if public_token is None:
        return "Navigate Plaid Link to Obtain Token"
    else:
        access_token = client.Item.public_token.exchange(public_token)['access_token']
        try:
            asset_report_create_response = client.AssetReport.create([access_token], 10)
        except plaid.errors.PlaidError as e:
            return jsonify(
                {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}})

        # print(pretty_response(asset_report_create_response))

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

        try:
            asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
        except plaid.errors.PlaidError as e:
            return jsonify(
                {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}})

        # TODO: Display pdf
        PIL = convert_from_bytes(asset_report_pdf)
        filename = '/Users/sterlingbutters/odrive/AmazonDrive/PycharmProjects/DashFinance/static/asset_report.png'
        PIL[0].save(filename, "PNG")
        PDF = html.Img(src='data:image/png;base64,{}'.format(filename))

        # No Interim
        # asset_report_png = PIL[0]
        # PDF = html.Img(src=asset_report_png)

        return PDF
######################### AssetReport #############################
