from strategies.strategybase import Strategy
import pandas as pd
import numpy as np
import ta

class SMACrossover(Strategy):
    def __init__(self, config, bot):
        super().__init__(config)
        self.short_window = config.get('short_window', 10)
        self.long_window = config.get('long_window', 30)
        self.prices = []
        self.buy_price = None
        self.historical_data = pd.DataFrame()
        self.bot = bot

    def process_historical_data(self, data):
        self.historical_data = pd.DataFrame(data['candles'])
        self.closes = self.historical_data['close']
        return self.historical_data

    def process_data(self, data, in_trade):
        self.newbar = pd.DataFrame(data)
        #print (self.newbar)
        signal = self.calculate_signal(self.historical_data, self.newbar, in_trade)

        if signal == 'buy':
            self.buy_signal()
            self.buy_price = self.newbar.iloc[-1].close
        
        if signal == 'sell':
            self.sell_signal()
         

        self.historical_data = pd.concat([self.historical_data, self.newbar], ignore_index=True)
    
    def calculate_signal(self, historical_data, newbar, in_trade):
        # Calculate signal based on strategy
        lastLow = self.historical_data.iloc[-1].low
        lastClose = self.historical_data.iloc[-1].close
        
        if not in_trade and self.newbar.iloc[-1].close > lastClose:
            return 'buy'
        
        elif in_trade:
            if self.newbar.iloc[-1].close > lastClose:
                return 'sell'

        

    def buy_signal(self):
        print(f"{self.config['bot_name']} Buy signal")
        self.bot.place_order('buy', True)

    def sell_signal(self):
        print(f"{self.config['bot_name']} Sell signal")
        self.bot.place_order('sell', False)
