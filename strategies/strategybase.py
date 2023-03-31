# strategies/strategybase.py
from logger import logger

class Strategy:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def on_data(self, data):
        raise NotImplementedError("on_data method must be implemented by the strategy")
