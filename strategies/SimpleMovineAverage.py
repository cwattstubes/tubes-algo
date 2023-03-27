# strategies/SimpleMovingAverage.py
from strategies.strategybase import Strategy

class SimpleMovingAverage(Strategy):
    def __init__(self, config):
        super().__init__(config)

    def on_data(self, data):
        # Implement your strategy logic here
        print (data)
        pass

