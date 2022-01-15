import hmac
import math
import time
import hashlib
from decimal import Decimal
import requests
import json
from urllib.parse import urlencode
import sys
import traceback
from configparser import ConfigParser
import datetime
import termcolor
from binance.client import Client

file = "config.ini"
config = ConfigParser()
config.read(file)

client = Client(str(config['appstate']['apikey']), str(config['appstate']['secretkey']))

today = datetime.date.today()

''' ======  begin of functions, you don't need to touch ====== '''
def hashing(query_string):
    SECRET = str(config['appstate']['secretkey'])

    return hmac.new(SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def get_timestamp():
    return int(time.time() * 1000)

def dispatch_request(http_method):
    KEY = str(config['appstate']['apikey'])

    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json;charset=utf-8',
        'X-MBX-APIKEY': KEY
    })
    return {
        'GET': session.get,
        'DELETE': session.delete,
        'PUT': session.put,
        'POST': session.post,
    }.get(http_method, 'GET')

# used for sending request requires the signature
def send_signed_request(http_method, url_path, payload={}):

    if int(config['appstate']['state']) == 0:
        BASE_URL = 'https://testnet.binance.vision'  # testnet base url
    else:
        BASE_URL = 'https://api.binance.com'  # real url

    query_string = urlencode(payload)
    # replace single quote to double quote
    query_string = query_string.replace('%27', '%22')
    if query_string:
        query_string = "{}&timestamp={}".format(query_string, get_timestamp())
    else:
        query_string = 'timestamp={}'.format(get_timestamp())

    url = BASE_URL + url_path + '?' + query_string + '&signature=' + hashing(query_string)

    params = {'url': url, 'params': {}}
    response = dispatch_request(http_method)(**params)
    return response.json()

# used for sending public data request
def send_public_request(url_path, payload={}):

    if int(config['appstate']['state']) == 0:
        BASE_URL = 'https://testnet.binance.vision'  # testnet base url
    else:
        BASE_URL = 'https://api.binance.com'  # real url

    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + '?' + query_string

    response = dispatch_request('GET')(url=url)
    return response.json()

def getprice():
    try:
        if str(config['appstate']['symbol']):

            params = {
                "symbol": str(config['appstate']['symbol'].replace("/", "")),
            }

            response = send_public_request("/api/v3/ticker/price", params)

            if "price" in response:
                return float(response["price"])
            elif "code" in response:
                            print(f"Error: Cannot get price...: {response['code']}, {response}. Exiting program")

                            sys.exit()
    except Exception as e:
        print("Cannot get instrument price. please fill the symbol label: {0}".format(e))
        traceback.print_exc()
        sys.exit()

def checkportfolio():
    try:
        response = send_signed_request('GET', '/api/v3/openOrders')

        if "code" in response:
            print(f"check portfolio error: {response}. Exiting program")
            # sys.exit()

        if type(response) == list and len(response) >= 1:
                for balance in response:
                    if str(config['appstate']['symbol'].replace("/", "")) == balance["symbol"]:
                        print(balance)
                        print("asset exsist in portfolio")
                        return True
        elif not response:
            return False
    except:
        print("cannot retrieve balance: exiting...")
        sys.exit()

def createorder(condition=None, ordertype=None, modquantity=None):
    try:
        if condition == "buy":

            print("buying instrument")

            if modquantity:
                quantity = modquantity

            if ordertype == "market":

                params = {
                    "symbol": str(config['appstate']['symbol'].replace("/", "")),
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": quantity,

                }
            elif ordertype == "limit":
                params = {
                    "symbol": str(config['appstate']['symbol'].replace("/", "")),
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": quantity,
                    "price": getprice() - int(config['appstate']['distance']),

                }

            response = send_signed_request('POST', '/api/v3/order', params)

            time.sleep(1)

            print(response)

            if "code" in response:
                print(f"buy order error: {response}. Exiting program")

                with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "a") as f:
                    f.write(
                        f" Order Error: {response['code']} \n")
                    f.close()
                    return False

            if "status" in response:
                if response["status"] == "FILLED":
                    print(f"Order bought for: {str(config['appstate']['symbol'])}, Price: {response['price']}, Quantity: {response['executedQty']}")

                    with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "a") as f:
                        f.write(f" Order filled/bought {response['symbol']}, {response['type']}, {response['price']}, {response['executedQty']} \n")
                        f.close()

        elif condition == "sell":

            print("selling instrument")

            if modquantity:
                quantity = modquantity

            if ordertype == "market":
                params = {
                    "symbol": str(config['appstate']['symbol'].replace("/", "")),
                    "side": "SELL",
                    "type": "MARKET",
                    "quantity": quantity,

                }
            elif ordertype == "limit":
                params = {
                    "symbol": str(config['appstate']['symbol'].replace("/", "")),
                    "side": "SELL",
                    "type": "MARKET",
                    "quantity": quantity,
                    "price": getprice() - int(config['appstate']['distance']),

                }

            response = send_signed_request('POST', '/api/v3/order', params)

            time.sleep(1)

            if "code" in response:
                print(f"sell order error: {response}. Exiting program")

                with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "a") as f:
                    f.write(
                        f" Order Error: {response['code']} \n")
                    f.close()
                    return False

            if "status" in response:
                if response["status"] == "FILLED":

                    print(f"Order sold for: {str(config['appstate']['symbol'])}, Price: {response['price']}, Quantity: {response['executedQty']}")

                    with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "a") as f:
                        f.write(f" Order filled/bought {response['symbol']}, {response['type']}, {response['price']}, {response['executedQty']} \n")
                        f.close()

                elif response["status"] == "EXPIRED":
                    print("Currency has no liquidity. you should check the open orders manually to sell")

                    with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "a") as f:
                        f.write(f" Order filled/bought {response['symbol']}, {response['type']}, {response['price']}, {response['executedQty']} \n")
                        f.close()
                    return False

    except Exception as e:
        print("Cannot place order")
        with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "a") as f:
            f.write(f" Cannot place order \n")
            f.close()
        traceback.print_exc()
        sys.exit()

def createreport():
    with open(f'report{today.strftime("%Y-%m-%d")}.txt', "w") as f:

        try:
            response = send_signed_request('GET', '/api/v3/account')

            if "code" in response:
                print(f"Convert error: {response}. Exiting program")
                sys.exit()

            if "balances" in response:
                f.write("Balance/assets \n")
                for balance in response['balances']:
                        f.write(f"{balance} \n")
                f.write(f"Total orders \n")
                f.write(f"{len(balance)} \n")

            response = send_signed_request('GET', '/api/v3/allOrders')

            if type(response) == list and response[0]:
                buylen = sum([1 for x in response if x['side'] == "BUY"])
                selllen = sum([1 for x in response if x['side'] == "SELL"])

                f.write(f"Total buy orders \n")
                f.write(f"{buylen} \n")
                f.write(f"Total sell orders \n")
                f.write(f"{selllen} \n")

        except:
            print("cannot retrieve balance: exiting...")
            sys.exit()

def getbalances():
    try:
        response = send_signed_request('GET', '/api/v3/account')

        if "code" in response:
            print(f"Convert error: {response}. Exiting program")
            sys.exit()

        if "balances" in response:
            for balance in response['balances']:
                if str(config['appstate']['symbol'].split("/")[0]) in balance['asset']:

                    newstr = balance['free'][0:-2] + "0" + "0"

                    return float(newstr)
    except:
        print("cannot get order")


def seebalance():
    try:
        response = send_signed_request('GET', '/api/v3/account')

        if "code" in response:
            print(f"Convert error: {response}. Exiting program")
            sys.exit()

        if "balances" in response:
            print("THIS IS YOUR BALANCE")
            for balance in response['balances']:
                print(balance)
    except:
        print("cannot get order")

def getlatestprice():
    prices = client.get_all_tickers()
    for symbols in prices:
        if symbols['symbol'] == "BTCUSDT":
            return int(float(symbols['price']))

def getval(currencyval):
    try:
        response = send_signed_request('GET', '/api/v3/account')

        if "code" in response:
            print(f"Convert error: {response}. Exiting program")
            sys.exit()

        if "balances" in response:
            for balance in response['balances']:
                if currencyval in balance['asset']:
                    mybalance = math.trunc(float(balance['free']))
                    mybalance = mybalance - 1
                    return mybalance
    except:
        print("cannot get order")

def getquantity():
    response = send_public_request("/api/v3/exchangeInfo")

    for symbol in response['symbols']:
        if symbol['symbol'] == config['appstate']['symbol'].replace("/", ""):
            precision = symbol['baseAssetPrecision']
            print(precision)

    order_amount = getval(config['appstate']['symbol'].split("/")[1]) / getlatestprice()  # size of order in BTC
    print(getval(config['appstate']['symbol'].split("/")[1]))
    print(getlatestprice())
    print(order_amount)

    precise_order_amount = "{:0.0{}f}".format(order_amount,precision)  # string of precise order amount that can be used when creating order
    newstr = precise_order_amount[0:-2] + "0" + "0"
    return float(newstr)


