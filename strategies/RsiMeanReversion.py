from .strategybase import Strategy
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

class RsiMeanReversion(Strategy):
    def __init__(self, config, bot, logger):
        super().__init__(config, logger)
        self.rsi_period = config.get('rsi_period', 14)
        self.oversold_threshold = config.get('oversold_threshold', 40)
        self.overbought_threshold = config.get('overbought_threshold', 60)
        self.historical_data = pd.DataFrame()
        self.bot = bot

    def process_historical_data(self, data):
        self.historical_data = data
        rsi_indicator = RSIIndicator(self.historical_data['close'], self.rsi_period)
        self.historical_data['rsi'] = rsi_indicator.rsi()
        return self.historical_data

    def process_data(self, data, in_trade):
        self.newbar = pd.DataFrame(data)
        self.historical_data = pd.concat([self.historical_data, self.newbar], ignore_index=True)
        rsi_indicator = RSIIndicator(self.historical_data['close'], self.rsi_period)
        self.historical_data['rsi'] = rsi_indicator.rsi()
        signal = self.calculate_signal(self.historical_data, self.newbar, in_trade)

        if signal == 'buy':
            self.buy_signal()
        
        if signal == 'sell':
            self.sell_signal()

    def calculate_signal(self, historical_data, newbar, in_trade):
        current_rsi = historical_data.iloc[-1].rsi

        if not in_trade and current_rsi <= self.oversold_threshold:
            return 'buy'
        
        elif in_trade and current_rsi >= self.overbought_threshold:
            return 'sell'

    def buy_signal(self):
        print(f"{self.config['bot_name']} Buy signal")
        self.logger.warning(f"{self.config['bot_name']} Buy signal")
        self.bot.place_order('buy', True)

    def sell_signal(self):
        print(f"{self.config['bot_name']} Sell signal")
        self.logger.warning(f"{self.config['bot_name']} Sell signal")
        self.bot.place_order('sell', False)