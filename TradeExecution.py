import traceback
import FivePaisaIntegration
import time as sleep_time
import pandas as pd
from datetime import datetime
import threading
lock = threading.Lock()
import time
FivePaisaIntegration.login()
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
                'ScripCode': row['ScripCode'],
                'BottomCentral':row['Bottom Central'],
                'TopCentral': row['Top Central'],
                'Difference':row['Difference'],
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
                "RunOnceHistory":False,
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

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()




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


while True:
    StartTime = credentials_dict.get('StartTime')
    Stoptime = credentials_dict.get('Stoptime')
    start_time = datetime.strptime(StartTime, '%H:%M').time()
    stop_time = datetime.strptime(Stoptime, '%H:%M').time()

    now = datetime.now().time()
    if now >= start_time and now < stop_time:
        main_strategy()
        time.sleep(1)
