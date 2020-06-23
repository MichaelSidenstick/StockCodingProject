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
        self.peak = 0.0
        self.valley = 100000.0
        self.change = 0.01 * opening_price