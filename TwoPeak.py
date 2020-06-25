import alpaca_trade_api as tradeapi
import websocket
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Stock:
    def __init__(self, ticker, opening_price=0.0, current_price=0.0, previous_price=0.0, time=0.0, can_set_peak=True,
                 can_set_valley=True, shares_bought=0.0, bought_price=0.0):
        self.ticker = ticker
        self.opening_price = opening_price
        self.current_price = current_price
        self.previous_price = previous_price
        self.time = time
        self.can_set_peak = can_set_peak
        self.can_set_valley = can_set_valley
        self.shares_bought = shares_bought
        self.bought_price = bought_price
        self.peak1 = 0.0
        self.peak2 = 0.0
        self.peakTime1 = 0.0
        self.peakTime2 = 0.0
        self.valley1 = 0.0
        self.valley2 = 0.0
        self.valleyTime1 = 0.0
        self.valleyTime2 = 0.0
        self.resistanceSlope = 0.0
        self.supportSlope = 0.0
        self.change = 0.01 * opening_price

# account keys
key = 'PK2490RRZ4FGDLO4SO4M'
sec = 'Lnjn97piqx44HZPl4WarYntA6SXALa627iUkJK7t'

# API endpoint URL
base_url = 'https://paper-api.alpaca.markets'

# ensure api version is correct
api = tradeapi.REST(key, sec, base_url, api_version='v2')

# init an account variable
account = api.get_account()

# create stocks to subscribe to
htz = Stock('EKSO')
stocks = [htz]

# get opening prices for all stocks
for stock in stocks:
    url = "https://finance.yahoo.com/quote/" + stock.ticker
    driver = webdriver.Chrome()
    # Go to yahoo finance
    driver.get(url)
    # Get the opening price
    h1 = driver.find_element_by_xpath("""//*[@id="quote-summary"]/div[1]/table/tbody/tr[2]/td[2]/span""")
    stock.opening_price = float(h1.text)
    stock.change = float((stock.opening_price / 100.0).__format__('.4f'))
    print(stock.ticker + ' OPENING PRICE: ' + str(stock.opening_price))
    driver.quit()

# get streams to tune into
streams = []
for a_stock in stocks:
    streams.append('T.' + a_stock.ticker)


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
    print("received a message!")
    print(message)

    # Get indexes and values of all needed variables for stream T
    price_index = message.index('\"p\"')
    s_index = message.index('\"s\"')
    timestamp_index = message.index('\"t\"')
    c_index = message.index('\"c\"')
    stock.time = (int(message[(timestamp_index + 4):(c_index - 1)]))/1000000000
    stock.previous_price = stock.current_price
    stock.current_price = float(message[(price_index + 4):(s_index - 1)])
    print("Previous Price: " + str(stock.previous_price))
    print("Current Price: " + str(stock.current_price))

    print(stock.change)
    print(stock.valley1)
    print(stock.valley2)
    print(stock.peak1)
    print(stock.peak2)

    # if the current price is 1% from valley, can set peak and not valley
    if stock.current_price > (stock.valley2 + stock.change):
        stock.can_set_peak = True
        stock.can_set_valley = False

    # if the current price is 1% from peak, can set valley and not peak
    if stock.current_price < (stock.peak2 - stock.change):
        stock.can_set_valley = True
        stock.can_set_peak = False

    # set valley
    # valley 2 is the more recent valley, valley 1 is the previous valley
    if stock.previous_price < stock.current_price and stock.can_set_valley:
        print('VALLEY SET: ' + str(stock.previous_price) + '')
        stock.valleyTime1 = stock.valleyTime2
        stock.valleyTime2 = stock.time
        stock.valley1 = stock.valley2
        stock.valley2 = stock.previous_price

    # set peak
    # peak 2 is the more recent peak, peak 1 is the previous peak
    if stock.previous_price > stock.current_price and stock.can_set_peak:
        print('PEAK SET: ' + str(stock.previous_price) + '')
        stock.peakTime1 = stock.peakTime2
        stock.peakTime2 = stock.time
        stock.peak1 = stock.peak2
        stock.peak2 = stock.previous_price
        
    slopeMaker()
    slopeBuyer()

def slopeMaker():
    
    if stock.peak1 != 0 and stock.peak2 != 0:
        rise1 = stock.peak2-stock.peak1
        run1 = stock.peakTime2 - stock.peakTime1
        stock.resistanceSlope = rise1/run1
        print(rise1)
        print(run1)
        print(stock.resistanceSlope)
        print("resistance slope formed")
    
    if stock.valley1 != 0 and stock.valley2 != 0:
        rise2 = stock.valley2-stock.valley1
        run2 = stock.valleyTime2 - stock.valleyTime1
        stock.supportSlope = rise2/run2
        print(rise2)
        print(run2)
        print(stock.supportSlope)
        print("support slope formed")

def slopeBuyer():
    if stock.valley1 != 0 and stock.valley2 != 0 and stock.peak1 != 0 and stock.peak2 != 0:
        
        max = stock.valley2 + stock.supportSlope * (stock.time-stock.valleyTime2)
        if stock.current_price < max:
            print("buy stonks")

def on_close(ws):
    print("closed connection")
socket = "wss://data.alpaca.markets/stream"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

ws.run_forever()
