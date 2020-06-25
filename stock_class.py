class Stock:
    def __init__(self, ticker, shares_owned=0):
        self.ticker = ticker
        self.opening_price = 0.0
        self.current_price = 0.0
        self.previous_price = 0.0
        self.two_prices_ago = 0.0
        self.time = 0.0
        self.shares_bought = 0.0
        self.shares_owned = shares_owned
        self.bought_price = 0.0
        self.peak = 0.0
        self.valley = 0.0
        self.change = 0.0
