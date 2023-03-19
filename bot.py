import questrade as qt
from database import *
from config import *
from alphavantage import *

# Create a Database object
db = Database(dbname, dbuser, dbpassword, dbhost, dbport)


class Bot:
    def __init__(self, config):
        self.config = config
        self.strategy = None
        self.broker = None
        self.orders = []

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_broker(self, broker):
        self.broker = broker

    def place_order(self, order):
        self.orders.append(order)
        return self.broker.place_order(order)

    def update_orders(self):
        for order in self.orders:
            self.broker.update_order(order)

    def get_orders(self):
        return self.orders
