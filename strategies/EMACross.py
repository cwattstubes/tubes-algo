from strategies.strategybase import Strategy

import pandas as pd
import numpy as np

class EMACross(Strategy):
    def __init__(self, config, bot):
        super().__init__(config)
        self.short_window = config.get('short_window', 12)
        self.long_window = config.get('long_window', 26)
        self.prices = []
        self.buy_price = None
        self.historical_data = pd.DataFrame()
        self.bot = bot

    def process_historical_data(self, data):
        self.historical_data = data
        self.historical_data['short_ema'] = self.historical_data['close'].ewm(span=self.short_window).mean()
        self.historical_data['long_ema'] = self.historical_data['close'].ewm(span=self.long_window).mean()
        return self.historical_data

    def process_data(self, data, in_trade):
        self.newbar = pd.DataFrame(data)
        self.historical_data = pd.concat([self.historical_data, self.newbar], ignore_index=True)
        self.historical_data['short_ema'] = self.historical_data['close'].ewm(span=self.short_window).mean()
        self.historical_data['long_ema'] = self.historical_data['close'].ewm(span=self.long_window).mean()
        signal = self.calculate_signal(self.historical_data, self.newbar, in_trade)

        if signal == 'buy':
            self.buy_signal()
            self.buy_price = self.newbar.iloc[-1].close
        
        if signal == 'sell':
            self.sell_signal()

    def calculate_signal(self, historical_data, newbar, in_trade):
        last_short_ema = historical_data.iloc[-2].short_ema
        last_long_ema = historical_data.iloc[-2].long_ema
        current_short_ema = historical_data.iloc[-1].short_ema
        current_long_ema = historical_data.iloc[-1].long_ema

        if not in_trade and current_short_ema > current_long_ema and last_short_ema <= last_long_ema:
            return 'buy'
        
        elif in_trade and current_short_ema < current_long_ema and last_short_ema >= last_long_ema:
            return 'sell'

    def buy_signal(self):
        print(f"{self.config['bot_name']} Buy signal")
        self.bot.place_order('buy', True)

    def sell_signal(self):
        print(f"{self.config['bot_name']} Sell signal")
        self.bot.place_order('sell', False)
