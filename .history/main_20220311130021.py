import time
from bs4 import BeautifulSoup
from datetime import datetime
import numpy as np
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(ChromeDriverManager().install())


def get_table(table):
    """Get Info from Table

        Input : Table
        Output : Reshaped Array
    """

    elems = table.find_all('td')
    list_ = [elem.text for elem in elems]
    arr = np.array(list_)
    filtred_list = [item.replace("  ", "") for item in arr]
    digit_list = [x for x in filtred_list if any(c.isdigit() for c in x)]
    arr_ = np.array(digit_list)
    reshaped_arr = arr_.reshape((20, 14))
    return reshaped_arr


def get_options(ticker, time_):
    """
    Function get_otions fetches options data from barchart website

    User inputs:
        Ticker: ticker
            - Ticker for the underlying
        Time: time
            - How much time needs for update the output 
    Output :     
        - Return a pandas.DataFrame() object 
    """

    while(True):
        # Construct the URL
        url = 'https://www.barchart.com/stocks/quotes/' + ticker + '/options'
        try:
            # Open Barchart website
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # driver.close()
            table_calls = soup.find_all('table')[0]
            table_puts = soup.find_all('table')[1]
            calls_arr = get_table(table_calls)
            puts_arr = get_table(table_puts)
            # Creating Dataframe for Call and Puts
            calls = pd.DataFrame(calls_arr, columns=['Strike', 'Moneyness', 'Bid', 'Midpoint', 'Ask',
                                 'Last', 'Change', '%Chg', 'Volume', 'Open Int', 'Vol/OI', 'IV', 'LastTrade', 'Avg IV'])
            puts = pd.DataFrame(puts_arr, columns=['Strike', 'Moneyness', 'Bid', 'Midpoint', 'Ask',
                                'Last', 'Change', '%Chg', 'Volume', 'Open Int', 'Vol/OI', 'IV', 'LastTrade', 'Avg IV'])
            implied_volatility = soup.find_all(
                "div", {"class": "column small-12 medium-4 large-4"})[1].find('strong').get_text()
            name = soup.find('span', {'class': 'symbol'}).get_text()
            # Adding Implied Volatility and Name to calls and Puts Dataframes
            calls["Implied Volatility"] = puts["Implied Volatility"] = implied_volatility
            calls["Name"] = puts["Name"] = name
            # Adding local time
            calls["Time"] = puts["Time"] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')
            # Overwrite the csv files
            with open('output/calls.csv', 'w') as f:
                calls.to_csv(f)
            with open('output/puts.csv', 'w') as f:
                puts.to_csv(f)
            print("Change : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print("Sleep for : " + str(time_/60) + " min")
            time.sleep(time_)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # Time in secons
    # 60 => Delay 1 min
    # change 60 with 120 for example if you want 2 mins

    options = get_options('$SPX', 60)
