import FivePaisaIntegration
import time as sleep_time
import pandas as pd
from datetime import datetime
import threading
lock = threading.Lock()

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

def get_user_settings():
    global result_dict
    try:
        df = pd.read_csv('MYINSTRUMENTS.csv')
        pf = pd.read_csv('ScripMaster.csv')
        cashdf = pf[(pf['Exch'] == "N") & (pf['ExchType'] == "C") & (pf['Series'] == "EQ")]
        cashdf['Name'] = cashdf['Name'].str.strip()
        cashdf = cashdf[['ScripCode', 'Name']]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for symbol in df['Symbol']:
            try:
                matching_row = cashdf[cashdf['Name'].str.strip() == symbol.strip()]
                if not matching_row.empty:
                    # Get the 'ScripCode' value
                    spcode = matching_row.iloc[0]['ScripCode']
                    cpr_percentage = df[df['Symbol'] == symbol]['CPR_Percentage'].values[0]

                    data = FivePaisaIntegration.get_historical_data(spcode)
                    open=float(data['Open'])
                    high=float(data['High'])
                    low=float(data['Low'])
                    close=float(data['Close'])

                    cpr_percentage_val = close * cpr_percentage*0.01

                    pivotpoint=high+low+close
                    pivotpoint=pivotpoint/3

                    bottomcentral=high+low
                    bottomcentral=bottomcentral/2

                    topcentral=pivotpoint-bottomcentral
                    topcentral=topcentral+pivotpoint

                    difference=topcentral-bottomcentral

                    if (topcentral-bottomcentral)<=cpr_percentage_val:
                        TradingEnabled= True
                    else:
                        TradingEnabled = False





                else:
                    print(f"No matching row found for symbol {symbol}")

                symbol_dict[symbol] = {
                    "ScripCode":spcode,
                    "CPR_Percentage":cpr_percentage,
                    "high":high,
                    "low":low,
                    "close":close,
                    "Pivot":pivotpoint,
                    "Bottom Central":bottomcentral,
                    "Top Central":topcentral,
                    "Difference": difference,
                    "TradingEnabled":TradingEnabled,
                }

            except Exception as e:
                print("Error happened in fetching symbol", str(e))

    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def savetocsv(symbol_dict):
    df = pd.DataFrame.from_dict(symbol_dict, orient='index')

    # Save the DataFrame to a CSV file
    df.to_csv('symbol_data.csv', index_label='Symbol')


get_user_settings()
savetocsv(symbol_dict)





