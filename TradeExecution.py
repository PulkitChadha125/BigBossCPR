import traceback
import pyotp
import FivePaisaIntegration,Zerodha_Integration
import time as sleep_time
import pandas as pd
from datetime import datetime
import threading
lock = threading.Lock()
import time
FivePaisaIntegration.login()


def get_zerodha_credentials():
    credentials = {}
    try:
        df = pd.read_csv('MainSettings.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials

credentials_dict = get_zerodha_credentials()
user_id = credentials_dict.get('ZerodhaUserId')  # Login Id
password = credentials_dict.get('ZerodhaPassword')  # Login password
fakey = credentials_dict.get('Zerodha2fa')
twofa = pyotp.TOTP(fakey)
twofa = twofa.now()

Zerodha_Integration.login(user_id, password, twofa)


def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def calculate_percentage_values(value, percentage):
    final = (float(percentage) / 100) * float(value)
    return final


def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

symbol_dict={}
result_dict={}
def get_user_settings():
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}

        for index, row in df.iterrows():
            symbol_dict = {
                'Symbol': row['Symbol'],
                'ScripCode': int(row['ScripCode']),
                'BottomCentral':float(row['Bottom Central']),
                'TopCentral': float(row['Top Central']),
                'Difference':float(row['Difference']),
                'TradingEnabled': row['TradingEnabled'],
                'TimeFrame': row['TimeFrame'],
                "TradeType": row['TradeType'],
                "CandleRangePts": float(row['CandleRangePts']),
                "OpeningDistance": float(row['OpeningDistance']),
                "Quantity": int(row['Quantity']),
                "Volume": float(row['Volume']),
                "TargetMultiplier": int(row['TargetMultiplier']),
                "BreakEvenMultiplier": int(row['BreakEvenMultiplier']),
                "USE_CLOSING_CRITERIA": row['USE_CLOSING_CRITERIA'],
                "ClosePercentage": row['ClosePercentage'],
                "NoOfCounterTrade":int(row['NoOfCounterTrade']),
                "count":0,
                "RunOnceHistory":False,
                "open_value" : None,
                "high_value" :None,
                "low_value" : None,
                "close_value" :None,
                "volume_value": None,
                "TradeSide":None,
                "InitialTrade":None,
                "StoplossValue": None,
                "TargetValue": None,
                "BreakEvenValue": None,
                "EntryPrice":None,
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ",result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

get_user_settings()


# AliceBlueIntegration.option_contract(exch="NFO",symbol='BANKNIFTY',expiry_date="2024-03-27",strike=43300,call=True)
def main_strategy ():
    global result_dict,next_specific_part_time,total_pnl,runningpnl,niftypnl,bankniftypnl

    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                if params["RunOnceHistory"] ==False:
                    params["RunOnceHistory"]=True
                    data=FivePaisaIntegration.get_historical_data(int(params['ScripCode']),str(params['TimeFrame']))
                    print(data)
                    open_value = float(data['Open'])
                    high_value =float (data['High'])
                    low_value = float(data['Low'])
                    close_value = float(data['Close'])
                    volume_value = float(data['Volume'])
                    params["open_value"] = open_value
                    params["high_value"] = high_value
                    params["low_value"] = low_value
                    params["close_value"] =close_value
                    params["volume_value"]= volume_value
                    if high_value-low_value > params["CandleRangePts"]:
                        params["TradingEnabled"]=False
                    if volume_value < params["Volume"]:
                        params["TradingEnabled"] = False
                    if open_value> params["TopCentral"]:
                        params["TradeSide"]= "BUY"
                        if (abs(open_value-params["TopCentral"]))> params["OpeningDistance"]:
                            params["TradingEnabled"] = False
                    if open_value< params["BottomCentral"]:
                        params["TradeSide"] = "SHORT"
                        if (abs(open_value-params["BottomCentral"]))> params["OpeningDistance"]:
                            params["TradingEnabled"] = False

                if params["TradingEnabled"] == True:
                    ltp=float(FivePaisaIntegration.get_ltp(int(params['ScripCode'])))
                    print(f'Symbol: {symbol}, ltp {ltp}')

                    if params["TradeSide"]=="BUY" and params["InitialTrade"] == None and params["count"]<=params["NoOfCounterTrade"]:
                        if ltp>=params["high_value"]:
                            params["InitialTrade"]="BUY"
                            params["count"]=params["count"]+1
                            params["EntryPrice"]=ltp
                            stoploss= params["low_value"]
                            params["StoplossValue"]= stoploss
                            diff= params["high_value"]-stoploss
                            tgtdiff=diff*params["TargetMultiplier"]
                            breakdiff= diff*params["BreakEvenMultiplier"]
                            params["TargetValue"]= params["high_value"]+tgtdiff
                            params["BreakEvenValue"]= params["high_value"]+breakdiff

                            if params["TradeType"] == "BOTH" or params["TradeType"] == "BUY":
                                Zerodha_Integration.buy(sym=symbol,quantity=int(params["Quantity"]))
                                orderlog = f'{timestamp} Buy order executed @ {symbol} @ {ltp} , target= {params["TargetValue"]}, stoploss= {params["StoplossValue"]},tradecount={params["count"]}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

                    if params["TradeSide"]=="SHORT" and params["InitialTrade"] == None and params["count"]<=params["NoOfCounterTrade"]:
                        if ltp<=params["low_value"]:
                            params["InitialTrade"]="SHORT"
                            params["EntryPrice"] = ltp
                            params["count"] = params["count"] + 1
                            stoploss = params["high_value"]
                            params["StoplossValue"] = stoploss
                            diff = stoploss-params["low_value"]
                            tgtdiff = diff * params["TargetMultiplier"]
                            breakdiff = diff * params["BreakEvenMultiplier"]
                            params["TargetValue"] = params["low_value"]-tgtdiff
                            params["BreakEvenValue"] = params["low_value"]- breakdiff
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "SELL":
                                Zerodha_Integration.short(sym=symbol, quantity=int(params["Quantity"]))
                                orderlog = f'{timestamp} Sell order executed @ {symbol} @ {ltp}, target= {params["TargetValue"]}, stoploss= {params["StoplossValue"]},tradecount={params["count"]}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

    # target & stoposs calculation
                    if params["InitialTrade"]=="BUY":
                        if ltp>=params["TargetValue"]and params["TargetValue"]>0:
                            params["InitialTrade"]=None
                            params["TradingEnabled"]=False
                            params["TargetValue"]=0
                            params["StoplossValue"] = 0
                            params["BreakEvenValue"]=0
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "BUY":
                                Zerodha_Integration.sell(sym=symbol, quantity=int(params["Quantity"]))
                                orderlog = f'{timestamp} Target executed {symbol} @ {ltp}, no more trades will be taken in {symbol}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if ltp>=params["BreakEvenValue"] and params["BreakEvenValue"]>0:
                            params["StoplossValue"]=params["EntryPrice"]
                            params["BreakEvenValue"]=0
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "BUY":
                                orderlog = f'{timestamp} Breakeven executed {symbol} , newsl= {params["StoplossValue"]}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if ltp<=params["StoplossValue"]and params["StoplossValue"]>0:
                            params["InitialTrade"]=None
                            params["TargetValue"] = 0
                            params["StoplossValue"] = 0
                            params["BreakEvenValue"] = 0
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "BUY":
                                Zerodha_Integration.sell(sym=symbol, quantity=int(params["Quantity"]))
                                orderlog = f'{timestamp} Stoploss executed {symbol} @ {ltp}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

                    if params["InitialTrade"] == "SHORT":
                        if ltp <= params["TargetValue"] and params["TargetValue"] > 0:
                            params["InitialTrade"] = None
                            params["TradingEnabled"] = False
                            params["TargetValue"] = 0
                            params["StoplossValue"] = 0
                            params["BreakEvenValue"] = 0
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "SELL":
                                Zerodha_Integration.cover(sym=symbol, quantity=int(params["Quantity"]))
                                orderlog = f'{timestamp} Target executed {symbol} @ {ltp}, no more trades will be taken in {symbol}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if ltp <= params["BreakEvenValue"] and params["BreakEvenValue"] > 0:
                            params["InitialTrade"] = None
                            params["TargetValue"] = 0
                            params["StoplossValue"] = params["EntryPrice"]
                            params["BreakEvenValue"] = 0
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "SELL":
                                orderlog = f'{timestamp} Tsl executed {symbol} , newsl= {params["StoplossValue"]}'
                                print(orderlog)
                                write_to_order_logs(orderlog)

                        if ltp >= params["StoplossValue"] and params["StoplossValue"] > 0:
                            params["InitialTrade"] = None
                            params["TargetValue"] = 0
                            params["StoplossValue"] = 0
                            params["BreakEvenValue"] = 0
                            if params["TradeType"] == "BOTH" or params["TradeType"] == "SELL":
                                Zerodha_Integration.cover(sym=symbol, quantity=int(params["Quantity"]))
                                orderlog = f'{timestamp} Stoploss executed {symbol} @ {ltp}'
                                print(orderlog)
                                write_to_order_logs(orderlog)


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


# main_strategy()
# Zerodha_Integration.cover(sym="SBIN", quantity=1)
while True:
    StartTime = credentials_dict.get('StartTime')
    Stoptime = credentials_dict.get('Stoptime')
    start_time = datetime.strptime(StartTime, '%H:%M').time()
    stop_time = datetime.strptime(Stoptime, '%H:%M').time()

    now = datetime.now().time()
    if now >= start_time and now < stop_time:
        main_strategy()
        time.sleep(1)
