import os.path


class Stock:
    def __init__(self, ticker, shares_bought=0.0, bought_price=0.0):
        self.ticker = ticker
        self.current_price = 0.0
        self.time = 0.0
        self.can_set_peak = True
        self.can_set_valley = True
        self.shares_bought = shares_bought
        self.bought_price = bought_price
        self.old_peak = 0.0
        self.recent_peak = 0.0
        self.shadow_peak = 0.0
        self.old_peak_time = 0.0
        self.recent_peak_time = 0.0
        self.shadow_peak_time = 0.0
        self.old_valley = 0.0
        self.recent_valley = 0.0
        self.shadow_valley = 0.0
        self.old_valley_time = 0.0
        self.recent_valley_time = 0.0
        self.shadow_valley_time = 0.0
        self.resistanceSlope = 0.0
        self.supportSlope = 0.0
        self.change_sl = 0.0
        self.ATR = 0.0
        self.stop_loss = 0.0
        self.state = 0


# format of the text document:
# stock ticker
# change_sl
# price_time

# an example of what to input would be:
# H:\Stocks\Data\NIO_prices
account_equity = 100000.00
file_name = input('File name to read (exclude .txt extension): ')
file_path = 'H:\\Stocks\\Data'
complete_file_name = os.path.join(file_path, file_name + '.txt')
file = open(complete_file_name, "r")
ticker = file.readline()
stock = Stock(ticker)
stock.change_sl = float(file.readline())
print('stock.change_sl: ' + str(stock.change_sl))
possible_low = 0.0
lowest_price = 0.0
highest_price = 0.0
net_profit = 0.0

while True:
    line = file.readline()
    if line == '':
        break

    # Get price and time
    separator = line.index('_')
    stock.current_price = float(line[0:separator])
    stock.time = int(line[(separator + 1):])

    # set high and low
    if stock.current_price < possible_low:
        possible_low = stock.current_price
    if stock.current_price > highest_price:
        lowest_price = possible_low
        highest_price = stock.current_price

    # initializes peaks and valleys to first price given
    if stock.state == 0:
        stock.shadow_peak = stock.current_price
        stock.shadow_valley = stock.current_price
        stock.old_valley = stock.current_price
        stock.recent_valley = stock.current_price
        stock.old_peak = stock.current_price
        stock.recent_peak = stock.current_price
        highest_price = stock.current_price
        lowest_price = stock.current_price
        possible_low = stock.current_price
        stock.state = 1

    # set peaks if a valley was just set and the price has risen enough
    if stock.can_set_peak and stock.current_price > stock.shadow_valley + stock.change_sl:
        stock.old_peak_time = stock.recent_peak_time
        stock.recent_peak_time = stock.shadow_peak_time
        stock.shadow_peak_time = stock.time
        stock.old_peak = stock.recent_peak
        stock.recent_peak = stock.shadow_peak
        stock.shadow_peak = stock.current_price
        stock.can_set_peak = False
        stock.can_set_valley = True
        if stock.state < 7:
            stock.state = stock.state + 1

    # continue to set the earliest peak if the price is rising
    if stock.can_set_valley and stock.current_price > stock.shadow_peak:
        stock.shadow_peak = stock.current_price
        # print('Shadow Peak: ' + str(stock.shadow_peak))
        stock.can_set_peak = False
        stock.can_set_valley = True

    # set valleys if a peak was just set and the price has fallen enough
    if stock.can_set_valley and stock.current_price < stock.shadow_peak - stock.change_sl:
        stock.old_valley_time = stock.recent_valley_time
        stock.recent_valley_time = stock.shadow_valley_time
        stock.shadow_valley_time = stock.time
        stock.old_valley = stock.recent_valley
        stock.recent_valley = stock.shadow_valley
        stock.shadow_valley = stock.current_price
        stock.can_set_valley = False
        stock.can_set_peak = True
        if stock.state < 7:
            stock.state = stock.state + 1

    # continue to set the earliest valley if the price is falling
    if stock.can_set_peak and stock.current_price < stock.shadow_valley:
        stock.shadow_valley = stock.current_price
        # print('Shadow valley: ' + str(stock.shadow_valley))
        stock.can_set_valley = False
        stock.can_set_peak = True

    # runs when three peaks and three valleys have been recorded
    if stock.state == 7:
        # calculate resistance and support lines
        rise1 = stock.recent_peak - stock.old_peak
        run1 = stock.recent_peak_time - stock.old_peak_time
        stock.resistanceSlope = rise1 / run1
        rise2 = stock.recent_valley - stock.old_valley
        run2 = stock.recent_valley_time - stock.old_valley_time
        stock.supportSlope = rise2 / run2
        support = stock.recent_valley + stock.supportSlope * (stock.time - stock.recent_valley_time)
        resistance = stock.recent_peak + stock.resistanceSlope * (stock.time - stock.recent_peak_time)

        # buy if the current price is under or on the support line
        if stock.shares_bought == 0 and stock.current_price <= support and resistance - support > 0.03:
            stock.shares_bought = int(float(account_equity)*0.01/stock.current_price)
            stock.bought_price = stock.current_price
            stock.stop_loss = stock.current_price - stock.change_sl

        # sell if over or on resistance line
        if stock.current_price >= resistance and stock.shares_bought > 0:
            # print trade
            net_of_trade = stock.shares_bought * (stock.current_price - stock.bought_price)
            print(str(stock.bought_price) + ' -> ' + str(stock.current_price) + ' at ' + str(stock.time) + ' for net ' +
                  net_of_trade.__format__('.2f'))
            net_profit = net_profit + net_of_trade
            # reset shares bought
            stock.shares_bought = 0

        # sell if price hits stop loss value calculated
        if stock.current_price <= stock.stop_loss and stock.shares_bought > 0:
            # print trade
            net_of_trade = stock.shares_bought * (stock.current_price - stock.bought_price)
            print(str(stock.bought_price) + ' -> ' + str(stock.current_price) + ' at ' + str(stock.time) + ' for net ' +
                  net_of_trade.__format__('.2f') + ' BY STOP LOSS')
            net_profit = net_profit + net_of_trade
            # reset shares bought
            stock.shares_bought = 0

# print results
print('\nNet profit: ' + net_profit.__format__('.2f'))
percent_profit = (100.0 * (account_equity + net_profit) / account_equity).__format__('.4f')
print(percent_profit + '%')
print('\nLowest price we could\'ve bought at: ' + str(lowest_price))
print('Highest price we could\'ve sold at: ' + str(highest_price))
