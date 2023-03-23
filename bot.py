import questrade as qt
from database import *
from config import *
from alphavantage import *
from data_feed import *

# Create a Database object
db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

# Bot class invoked by bot_manager.py

class Bot:
    def __init__(self, config):
        self.config = config
        self.strategy = None
        self.broker = None
        self.orders = []
        self.data_feed = None

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

    def subscribe_to_data_feed(self, data_feed):
        self.data_feed = data_feed
        self.data_feed.subscribe(Subscriber(self.config['bot_id']))

    def process_data(self, data):
        # Do something with the incoming data, using the strategy and broker as needed
        print (data)
        pass

    """
    start a bot
    """
    def start(self):
        # Get bot configuration from database

        # Create a Bot object
        bot = Bot(self.config)

        # Subscribe to data feed
        bot.subscribe_to_data_feed(self.data_feed)

        # Start data feed
        bot.start_data_feed()

        # Start the bot
        #bot.start()

    """
    stop a bot
    """
    def stop(self):
        # Stop the bot
        #bot.stop()
        pass

#Bot.start(bot_id='1')
