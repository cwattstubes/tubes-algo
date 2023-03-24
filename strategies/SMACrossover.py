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

    def process_data(self, data):
        self.bars = data
        print (self.bars)



    def buy_signal(self):
        print("Buy signal")

    def sell_signal(self):
        print("Sell signal")