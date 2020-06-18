import alpaca_trade_api as tradeapi
import websocket
import json
import time
# account keys
key = 'PKKISGBT814WSEQWZ2AM'
sec = '/4r0nC5Y7D9r7I1VcNI5c/zua0FoSZS3D/A6VRyJ'
# API endpoint URL
base_url = 'https://paper-api.alpaca.markets'
# ensure api version is correct
api = tradeapi.REST(key, sec, base_url, api_version='v2')
# init an account variable
account = api.get_account()
#Get streams
tickers = ["AM.AAPL", "T.AAPL"]
#Initialize a few variables
price_array = []
peak = 100000
valley = 0
a_value = 0
peak_valley_array = [peak,valley]

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
    print("received a message")
    print(message)
    if '\"x\"' in message:
        # Get indexes of all needed variables for stream T
        price_index = message.index('\"p\"')
        s_index = message.index('\"s\"')
        price_current = message[(price_index+4):(s_index-1)]
        price_array.append(price_current)
    if '\"v\"' in message:
        # Get indexes of all needed variables for stream AM
        opening_price_index = message.index('\"op\"')
        ticker_index = message.index('\"T\"')
        volume_index = message.index('\"v\"')
        av_index = message.index('\"av\"')
        vw_index = message.index('\"vw\"')
        ticker = message[(ticker_index + 4):(volume_index - 1)]
        volume = message[(volume_index + 5):(av_index - 2)]
        opening_price = message[(opening_price_index+5):(vw_index-1)]

    if price_current >= (peak_valley_array[1]+(0.01*opening_price)):
        peak_valley_array[0] = price_current
    if price_current <= (peak_valley_array[0]-(0.01*opening_price)):
        peak_valley_array[1] = price_current
    if price_current >= peak_valley_array[0]:
        peak_valley_array[0] = price_current
    if price_current <= peak_valley_array[1]:
        peak_valley_array[1] = price_current

    #if price_current >= (1.01*peak_valley_array[0]) or price_current <= (0.99*peak_valley_array[0]) and peak_valley_array[4] == 1:
     #   peak_valley_array[0]=price_current


def on_close(ws):
    print("closed connection")
socket = "wss://data.alpaca.markets/stream"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)

ws.run_forever()
