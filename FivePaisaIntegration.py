import time

AppName="5P50985207"
AppSource=22072
UserID="Xr375mgFMNK"
Password="3lk8hnSOROg"
UserKey="gmRtyJT5iSs21juJA6Q6eSG4lekeIyjo"
EncryptionKey="BTOYpwClDHz1qydFoyYy88Oc7XZwyDCB"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYDSOBVGIYDOXZVKBDUWRKZ"
from py5paisa import FivePaisaClient
import pyotp,datetime
from datetime import datetime,timedelta
import pandas as pd
client=None
def login():
    global client
    cred={
        "APP_NAME":AppName,
        "APP_SOURCE":AppSource,
        "USER_ID":UserID,
        "PASSWORD":Password,
        "USER_KEY":UserKey,
        "ENCRYPTION_KEY":EncryptionKey
        }

    twofa = pyotp.TOTP(totpstr)
    twofa = twofa.now()
    print(twofa)
    client = FivePaisaClient(cred=cred)
    client.get_totp_session(client_code=50985207,totp=twofa,pin=162916)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())

def get_historical_data(token,timeframe):
    global client
    from_time = datetime.now() - timedelta(days=4)
    to_time = datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    last_row_values = df.iloc[-1].to_dict()

    return last_row_values

def get_historical_data_tradeexecution(token, timeframe):
    global client
    current_time = datetime.now()
    if timeframe == "1m":
        delta_minutes = 1
    elif timeframe == "2m":
        delta_minutes = 2
    elif timeframe == "5m":
        delta_minutes = 5

    desired_time = current_time - timedelta(minutes=delta_minutes)
    desired_time = desired_time.replace(second=0)
    desired_time_str = desired_time.strftime('%Y-%m-%d %H:%M:%S')

    print("desired time:", desired_time_str)

    from_time = datetime.now() - timedelta(days=4)
    to_time = datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Filter last two rows
    last_two_rows = df.iloc[-2:]

    # Filter row matching the desired time
    desired_row = last_two_rows[last_two_rows['Datetime'] == desired_time_str]

    if not desired_row.empty:
        desired_row_values = desired_row.iloc[0].to_dict()
        return desired_row_values
    else:
        return None  # Or handle the case when no row matches the desired time



def get_live_market_feed():
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripData": "ITC"},
    {"Exch": "N", "ExchType": "C", "ScripCode": "2885"}]

    print(client.fetch_market_feed_scrip(req_list_))

def previousdayclose(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    pclose_value = float(responce['Data'][0]['PClose'])
    return pclose_value


def get_ltp(code):
    global client
    try:
        req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
        responce=client.fetch_market_feed_scrip(req_list_)
        last_rate = float(responce['Data'][0].get('LastRate', 0))
        print(last_rate)
    except Exception as e:
        time.sleep(1)
        req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
        responce = client.fetch_market_feed_scrip(req_list_)
        last_rate = float(responce['Data'][0].get('LastRate', 0))
        print(last_rate)

    return last_rate

def buy( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def sell( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)
def short( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def cover( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def get_position():
    global client
    responce = client.positions()

    return responce

def get_margin():
    global client
    responce= client.margin()
    if responce:
        net_available_margin =float (responce[0]['NetAvailableMargin'])
        return net_available_margin
    else:
        print("Error: Unable to get NetAvailableMargin")
        return None

def orderbook():


    global client
    client.get_tradebook()





















