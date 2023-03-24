from strategies.strategybase import Strategy
import pandas as pd
import numpy as np
import ta

class SMACrossover(Strategy):
    def __init__(self, config):
        super().__init__(config)
        self.short_window = config.get('short_window', 10)
        self.long_window = config.get('long_window', 30)
        self.prices = []
        self.historical_data = pd.DataFrame()

    def process_historical_data(self, data):
        self.historical_data = pd.DataFrame(data['candles'])
        #closes = self.historical_data['close']
        return self.historical_data

    def process_data(self, data):
        self.newbar = pd.DataFrame(data)
        self.historical_data = pd.concat([self.historical_data, self.newbar], ignore_index=True)
        print(self.newbar)
        print(self.historical_data)
        pass
      
    def buy_signal(self):
        print("Buy signal")

    def sell_signal(self):
        print("Sell signal")
