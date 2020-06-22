import alpaca_trade_api as tradeapi
import websocket
import json
import time
# account keys
key = [YOUR KEY HERE]
sec = [YOUR SECRET KEY HERE]
# API endpoint URL
base_url = 'https://paper-api.alpaca.markets'
# ensure api version is correct
api = tradeapi.REST(key, sec, base_url, api_version='v2')
# init an account variable
account = api.get_account()
# Get streams
tickers = ["T.IDEX", "AM.IDEX"]

opening_price = 0.0
current_price = 0.0
time = 0.0
tf_AM = 0.0
tf_T = 0.0
tf_peak = 0.0
tf_valley = 0.0
shares_bought = 0.0
buy_sell = 0
bought_price = 0
data = [opening_price,current_price, time, tf_AM, tf_T, tf_peak, tf_valley, buy_sell, shares_bought, 0, bought_price]
peak = 0.0
valley = 0.0
peak_valley = [peak,valley]

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
                          "streams": tickers
                      }
                      }
    ws.send(json.dumps(listen_message))

def on_message(ws, message):
    print("received a message!")
    print(message)

    if '\"v\"' in message:
        # Get indexes and values of all needed variables for stream AM
        opening_price_index = message.index('\"op\"')
        ticker_index = message.index('\"T\"')
        volume_index = message.index('\"v\"')
        # tick_price_index = message.index('\"c|\"')
        # h_index = message.index('\"h\"')
        av_index = message.index('\"av\"')
        vw_index = message.index('\"vw\"')
        ticker = message[(ticker_index + 5):(volume_index - 2)]
        # volume = message[(volume_index + 5):(av_index - 2)]
        data[0] = float(message[(opening_price_index + 5):(vw_index - 1)])
        # data[1] = message[(tick_price_index + 4):(h_index - 1)]
        data[3] = 1
    elif '\"x\"' in message:
        # Get indexes and values of all needed variables for stream T
        price_index = message.index('\"p\"')
        s_index = message.index('\"s\"')
        timestamp_index = message.index('\"t\"')
        data[1] = float(message[(price_index + 4):(s_index - 1)])
        c_index = message.index('\"c\"')
        data[2] = (int(message[(timestamp_index + 4):(c_index - 1)]))/1000000
        data[4] = 1

    if data[3] == 1 and data[4] == 1:
        print(data)
        if peak_valley[0] == 0:
            peak_valley[0] = data[1]
            peak_valley[1] = data[1]
            print(peak_valley)

        if data[5] and data[6] == 1:
            # If the stock hits the resistance line, sell the stock
            if data[1] >= peak_valley[0] and data[7] == 1:
                api.submit_order(
                    symbol=[TICKER NAME HERE],
                    qty=data[8],
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                data[7] = 0
                data[8] = 0
                print("Sold Shares")
            # If the stock hits the support line, buy the stock
            if data[1] <= peak_valley[1] and data[7] == 0:
                data[8] = int(((float(account.equity))*0.01)/data[1])
                api.submit_order(
                    symbol=[TICKER NAME HERE],
                    qty=data[8],
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                data[7] = 1
                data[10] = data[1]
                print("Bought Shares")
            # If the price drops 1 percent below where you bought it, sell it
            if data[1] <= (data[10]*0.99) and data[7] == 1:
                api.submit_order(
                    symbol=[TICKER NAME HERE],
                    qty=data[8],
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                data[7] = 0
                data[8] = 0
                print("Sold Shares by Stop Safe")

        # If the current price is under the current valley
        if data[1] < peak_valley[1] and data[6] == 1:
            peak_valley[1] = data[1]
            print(peak_valley)

        # If the current price is above the current peak
        if data[1] > peak_valley[0] and data[5] == 1:
            peak_valley[0] = data[1]
            print(peak_valley)

        # If the current price is 1% of the opening price above the current valley FOR FIRST PEAK
        if data[1] > (data[0]*0.02+peak_valley[1]) and data[9] == 0:
            peak_valley[0] = data[1]
            data[5] = 1
            print(peak_valley)
            data[9] = 1

        # If the current price is 1% of the opening price under the current peak FOR FIRST VALLEY
        if data[1] < (peak_valley[0]-data[0]*0.02) and data[9] == 0:
            peak_valley[1] = data[1]
            data[6] = 1
            print(peak_valley)
            data[9] = 2

        # If the current price is 1% of the opening price above the current valley
        if data[1] > (data[0] * 0.005 + peak_valley[1]) and data[9] == 2:
            peak_valley[0] = data[1]
            data[5] = 1
            print(peak_valley)
            data[9] = 1

        # If the current price is 1% of the opening price under the current peak
        if data[1] < (peak_valley[0] - data[0] * 0.005) and data[9] == 1:
            peak_valley[1] = data[1]
            data[6] = 1
            print(peak_valley)
            data[9] = 2

def on_close(ws):
    print("closed connection")
socket = "wss://data.alpaca.markets/stream"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

ws.run_forever()
