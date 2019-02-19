import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)

# # Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
# PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
# PLAID_SECRET = os.getenv('PLAID_SECRET')
# PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
# # Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# # password: pass_good)
# # Use `development` to test with live users and credentials and `production`
# # to go live
# PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# # PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# # Link. Note that this list must contain 'assets' in order for the app to be
# # able to create and retrieve asset reports.
# PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')

PLAID_CLIENT_ID = '5c4a2ad8d8717a0010e5176c'
PLAID_SECRET = '740664395d8cb7b64490c19a452a26'
PLAID_PUBLIC_KEY = '7a3daf1db208b7d1fe65850572eeb1'
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')

client = plaid.Client(client_id=PLAID_CLIENT_ID,
                      secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY,
                      environment=PLAID_ENV,
                      api_version='2018-05-22')


@app.route('/')
def index():
    return render_template(
        'index.ejs',
        plaid_public_key=PLAID_PUBLIC_KEY,
        plaid_environment=PLAID_ENV,
        plaid_products=PLAID_PRODUCTS,
    )


access_token = None


# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@app.route('/get_access_token', methods=['POST'])
def get_access_token():
    global access_token
    public_token = request.form['public_token']
    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))

    pretty_print_response(exchange_response)
    access_token = exchange_response['access_token']
    return jsonify(exchange_response)


@app.route('/set_access_token', methods=['POST'])
def set_access_token():
    global access_token
    access_token = request.form['access_token']
    item = client.Item.get(access_token)
    return jsonify({'error': None, 'item_id': item['item']['item_id']})


# Retrieve high-level information about an Item
# https://plaid.com/docs/#retrieve-item
@app.route('/item', methods=['GET'])
def item():
    global access_token
    item_response = client.Item.get(access_token)
    institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
    pretty_print_response(item_response)
    pretty_print_response(institution_response)
    return jsonify({'error': None, 'item': item_response['item'], 'institution': institution_response['institution']})


# Retrieve ACH or ETF account numbers for an Item
# https://plaid.com/docs/#auth
@app.route('/auth', methods=['GET'])
def get_auth():
    try:
        auth_response = client.Auth.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(auth_response)
    return jsonify({'error': None, 'auth': auth_response})


# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    # Pull transactions for the last 30 days
    start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
    end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
    try:
        transactions_response = client.Transactions.get(access_token, start_date, end_date)
    except plaid.errors.PlaidError as e:
        return jsonify(format_error(e))
    pretty_print_response(transactions_response)
    return jsonify({'error': None, 'transactions': transactions_response})


# Retrieve Identity data for an Item
# https://plaid.com/docs/#identity
@app.route('/identity', methods=['GET'])
def get_identity():
    try:
        identity_response = client.Identity.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(identity_response)
    return jsonify({'error': None, 'identity': identity_response})


# Retrieve real-time balance data for each of an Item's accounts
# https://plaid.com/docs/#balance
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        balance_response = client.Accounts.balance.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(balance_response)
    return jsonify({'error': None, 'balance': balance_response})


# Retrieve an Item's accounts
# https://plaid.com/docs/#accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
    try:
        accounts_response = client.Accounts.get(access_token)
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(accounts_response)
    return jsonify({'error': None, 'accounts': accounts_response})


# Create and then retrieve an Asset Report for one or more Items. Note that an
# Asset Report can contain up to 100 items, but for simplicity we're only
# including one Item here.
# https://plaid.com/docs/#assets
@app.route('/assets', methods=['GET'])
def get_assets():
    try:
        asset_report_create_response = client.AssetReport.create([access_token], 10)
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
    pretty_print_response(asset_report_create_response)

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
            return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

    if asset_report_json is None:
        return jsonify({'error': {'display_message': 'Timed out when polling for Asset Report', 'error_code': e.code, 'error_type': e.type } })

    asset_report_pdf = None
    try:
        asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
    except plaid.errors.PlaidError as e:
        return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

    return jsonify({
        'error': None,
        'json': asset_report_json,
        'pdf': base64.b64encode(asset_report_pdf),
    })


def pretty_print_response(response):
    print(json.dumps(response, indent=2, sort_keys=True))


def format_error(e):
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 8000))

