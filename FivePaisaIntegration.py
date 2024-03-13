AppName="5P50985207"
AppSource=22072
UserID="Xr375mgFMNK"
Password="3lk8hnSOROg"
UserKey="gmRtyJT5iSs21juJA6Q6eSG4lekeIyjo"
EncryptionKey="BTOYpwClDHz1qydFoyYy88Oc7XZwyDCB"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYDCMBRHA3TOXZVKBDUWRKZ"
from py5paisa import FivePaisaClient
import pyotp,datetime
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
    client = FivePaisaClient(cred=cred)
    client.get_totp_session(client_code=50101877,totp=twofa,pin=654321)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())

def get_historical_data(token,timeframe):
    global client
    from_time = datetime.datetime.now() - datetime.timedelta(days=4)
    to_time = datetime.datetime.now()
    df = client.historical_data('N', 'C', token, timeframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    last_row_values = df.iloc[-1].to_dict()

    return last_row_values




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
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
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





















