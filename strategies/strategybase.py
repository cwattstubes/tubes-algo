# strategies/strategybase.py

class Strategy:
    def __init__(self, config):
        self.config = config

    def on_data(self, data):
        raise NotImplementedError("on_data method must be implemented by the strategy")
