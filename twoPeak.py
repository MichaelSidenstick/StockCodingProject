import alpaca_trade_api as tradeapi
import websocket
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import yfinance as yf
import numpy as np

class Stock:
    def __init__(self, ticker, shares_owned=0):
        self.ticker = ticker
        self.opening_price = 0.0
        self.current_price = 0.0
        self.time = time
        self.can_set_peak = True
        self.can_set_valley = True
        self.shares_owned = shares_owned
        self.bought_price = 0.0
        self.old_peak = 0.0
        self.recent_peak = 0.0
        self.old_peak_time = 0.0
        self.recent_peak_time = 0.0
        self.old_valley = 0.0
        self.recent_valley = 0.0
        self.old_valley_time = 0.0
        self.recent_valley_time = 0.0
        self.resistanceSlope = 0.0
        self.supportSlope = 0.0
        self.change_pv = 0.0
        self.change_sl = 0.0
        self.ATR = 0.0
        self.stop_loss = 0.0



# account keys
key = 'PKKISGBT814WSEQWZ2AM'
sec = '/4r0nC5Y7D9r7I1VcNI5c/zua0FoSZS3D/A6VRyJ'

# API endpoint URL
base_url = 'https://paper-api.alpaca.markets'

# ensure api version is correct
api = tradeapi.REST(key, sec, base_url, api_version='v2')

# init an account variable
account = api.get_account()


# Get the most volatile stock
url = 'https://finviz.com/'
DRIVER_PATH = r'H:\PyCharm\ChromeWebDriver\chromedriver.exe'
# Open browser/server connection
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
# Go to yahoo finance
driver.get(url)
# Get two most volatile stocks from finviz
h1 = driver.find_element_by_xpath("""//*[@id="homepage"]/table/tbody/tr[4]/td/table/tbody/tr/td[3]/table/tbody/tr[14]/td[1]/a""")
most_volatile_1 = h1.text

# create stocks to subscribe to
_stock1_ = Stock(most_volatile_1)
stocks = [_stock1_]

# get opening prices and for all stocks
for stock in stocks:
    url = "https://finance.yahoo.com/quote/" + stock.ticker
    driver.get(url)
    # Get the opening price
    h5 = driver.find_element_by_xpath("""//*[@id="quote-summary"]/div[1]/table/tbody/tr[2]/td[2]/span""")
    stock.opening_price = float(h5.text)
    print(stock.ticker + ' OPENING PRICE: ' + str(stock.opening_price))
    driver.quit()
    # Get the ATR
    # Get historical price data
    price_data = yf.download(stock.ticker,
                             start='2019-01-01',
                             end='2019-12-31',
                             progress=False)
    # Initialize counter and True Range Array for while loop
    counter = 0
    TR_Array = []
    while (counter < 14):
        # Get current high, current low, and previous close
        day_high = price_data.iloc[counter, 1]
        day_low = price_data.iloc[counter, 2]
        prev_close = price_data.iloc[(counter + 1), 3]
        # Calculate the True Range possibilities
        ATR_A = day_high - day_low
        ATR_B = abs(day_high - prev_close)
        ATR_C = abs(day_low - prev_close)
        counter = 1 + counter
        TR = max(ATR_A, ATR_B, ATR_C)
        TR_Array.append(TR)
    # Calculate average true range
    TR_Array = np.array(TR_Array)
    stock.ATR = np.mean(TR_Array)
    stock.change_pv = float((stock.ATR / 8.0))
    stock.change_sl = float((stock.ATR / 10.0))


# get streams to tune into
streams = []
for stock in stocks:
    streams.append('T.' + stock.ticker)


# get stock object in message from ticker
def get_stock(message, stocks=stocks):
    if '\"x\"' in message:
        data_index = message.index('\"data\"') - 2
        stream_index = message.index('.') + 1
        tick = message[stream_index:data_index]
        for thing in stocks:
            if thing.ticker == tick:
                return thing


def on_open(ws):
    print("opened")
    auth_data = {
        "action": "authenticate",
        "data": {
            "key_id": key,
            "secret_key": sec
        }
    }
    ws.send(json.dumps(auth_data))
    listen_message = {"action": "listen",
                      "data": {
                          "streams": streams
                      }
                      }
    ws.send(json.dumps(listen_message))


def on_message(ws, message):
    print(message)

    # Get indexes and values of all needed variables for stream T
    price_index = message.index('\"p\"')
    s_index = message.index('\"s\"')
    timestamp_index = message.index('\"t\"')
    c_index = message.index('\"c\"')
    stock.time = int(message[(timestamp_index + 4):(c_index - 10)])
    stock.current_price = float(message[(price_index + 4):(s_index - 1)])

    if stock.can_set_peak and stock.current_price > (stock.recent_valley + stock.change_pv):
        stock.old_peak_time = stock.recent_peak_time
        stock.recent_peak_time = stock.time
        stock.old_peak = stock.recent_peak
        stock.recent_peak = stock.current_price
        stock.can_set_peak = False
        stock.can_set_valley = True
        print('Old Peak: ' + str(stock.old_peak))
        print('Rec Peak: ' + str(stock.recent_peak))

    if stock.can_set_valley and stock.current_price > stock.recent_peak:
        stock.recent_peak = stock.current_price
        print('New recent valley: ' + str(stock.recent_peak))

    if stock.can_set_valley and stock.current_price < (stock.recent_peak - stock.change_pv):
        stock.old_valley_time = stock.recent_valley_time
        stock.recent_valley_time = stock.time
        stock.old_valley = stock.recent_valley
        stock.recent_valley = stock.current_price
        stock.can_set_valley = False
        stock.can_set_peak = True
        print('Old Valley: ' + str(stock.old_valley))
        print('Rec Valley: ' + str(stock.recent_valley))

    if stock.can_set_peak and stock.current_price < stock.recent_valley:
        stock.recent_valley = stock.current_price
        print('New recent valley: ' + str(stock.recent_valley))

    slopeMaker()

    if stock.old_valley != 0 and stock.recent_valley != 0 and stock.old_peak != 0 and stock.recent_peak != 0:
        max = stock.recent_valley + stock.supportSlope * (stock.time - stock.recent_valley_time)
        min = stock.recent_peak + stock.resistanceSlope * (stock.time - stock.recent_peak_time)

        if stock.can_set_valley and stock.current_price >= 1.0025 * min and stock.shares_owned == 0:
            stock.shares_owned = int(float(account.equity) * 0.01 / stock.current_price)
            api.submit_order(
                symbol=stock.ticker,
                qty=stock.shares_owned,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            stock.stop_loss = stock.current_price - stock.change_sl

        if stock.can_set_peak and stock.current_price <= max * 0.9975 and stock.shares_owned>0:
            api.submit_order(
                symbol=stock.ticker,
                qty=stock.shares_owned,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            stock.shares_owned = 0

        if stock.current_price <= stock.stop_loss and stock.shares_owned > 0:
            api.submit_order(
                symbol=stock.ticker,
                qty=stock.shares_owned,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            stock.shares_owned = 0

    if stock.can_set_valley and stock.current_price > 1.0025 * stock.recent_valley:
        stock.shares_owned = int(float(account.equity) * 0.01 / stock.current_price)
        api.submit_order(
            symbol=stock.ticker,
            qty=stock.shares_owned,
            side='buy',
            type='market',
            time_in_force='gtc'
        )

    if stock.can_set_peak and stock.current_price < 0.9975 * stock.recent_peak:
        api.submit_order(
            symbol=stock.ticker,
            qty=stock.shares_owned,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        stock.shares_owned = 0

def slopeMaker():
    if stock.old_peak != 0 and stock.recent_peak != 0:
        rise1 = stock.recent_peak - stock.old_peak
        run1 = stock.recent_peak_time - stock.old_peak_time
        stock.resistanceSlope = rise1 / run1

    if stock.old_valley != 0 and stock.recent_valley != 0:
        rise2 = stock.recent_valley - stock.old_valley
        run2 = stock.recent_valley_time - stock.old_valley_time
        stock.supportSlope = rise2 / run2


def on_close(ws):
    print("closed connection")


socket = "wss://data.alpaca.markets/stream"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

ws.run_forever()