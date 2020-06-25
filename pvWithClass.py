import alpaca_trade_api as tradeapi
import websocket
import json
import time
import stock_class
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# account keys
key = 'PKKISGBT814WSEQWZ2AM'
sec = '/4r0nC5Y7D9r7I1VcNI5c/zua0FoSZS3D/A6VRyJ'

# API endpoint URL
base_url = 'https://paper-api.alpaca.markets'

# ensure api version is correct
api = tradeapi.REST(key, sec, base_url, api_version='v2')

# init an account variable
account = api.get_account()

# create stocks to subscribe to
ekso = stock_class.Stock('EKSO')
stocks = [ekso]

# get opening prices for all stocks
for stock in stocks:
    url = "https://finance.yahoo.com/quote/" + stock.ticker + "?p=" + stock.ticker
    # Path to Chrome Driver
    DRIVER_PATH = r'H:\PyCharm\ChromeWebDriver\chromedriver.exe'
    # Open browser/server connection
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    # Go to yahoo finance
    driver.get(url)
    # Get the opening price
    h1 = driver.find_element_by_xpath("""//*[@id="quote-summary"]/div[1]/table/tbody/tr[2]/td[2]/span""")
    stock.opening_price = float(h1.text)
    stock.peak = stock.opening_price
    stock.valley = stock.opening_price
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
    print(message)
    stock = get_stock(message)
    if '\"x\"' in message:
        # Get indexes and values of all needed variables for stream T
        price_index = message.index('\"p\"')
        s_index = message.index('\"s\"')
        stock.two_prices_ago = stock.previous_price
        stock.previous_price = stock.current_price
        stock.current_price = float(message[(price_index + 4):(s_index - 1)])

        # if the current price is 1% from valley, can set peak and not valley
        if (stock.valley + stock.change) < stock.current_price < stock.previous_price >= stock.two_prices_ago:
            stock.peak = stock.previous_price
            print('PEAK SET: ' + str(stock.peak) + '\nCurrent valley: ' + str(stock.valley))
            # sell if there is a significant turn
            if stock.shares_bought != 0 and stock.peak / stock.current_price >= 1.005:
                print('\nSell ' + str(stock.shares_owned) + ' stocks for ' + str(stock.current_price) + '\n')
                '''
                api.submit_order(
                    symbol=[stock.ticker],
                    qty=stock.shares_bought,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                '''

        # if the current price is 1% from peak, can set valley and not peak
        if (stock.peak - stock.change) > stock.current_price > stock.previous_price <= stock.two_prices_ago:
            stock.valley = stock.previous_price
            print('VALLEY SET: ' + str(stock.valley) + '\nCurrent peak: ' + str(stock.peak))
            # buy if there is a significant turn
            if stock.current_price / stock.valley >= 1.005:
                stock.shares_bought = stock.shares_bought + int(((float(account.equity)) * 0.01) / stock.current_price)
                stock.shares_owned = stock.shares_owned + stock.shares_bought
                print('\nBuy ' + str(stock.shares_bought) + ' stocks for ' + str(stock.current_price) + '\n')
                '''
                api.submit_order(
                    symbol=[stock.ticker],
                    qty=stock.shares_bought,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                '''
                stock.bought_price = stock.current_price


def on_close(ws):
    print("closed connection")
socket = "wss://data.alpaca.markets/stream"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

ws.run_forever()
