import questrade as qt
from database import *
from config import *
from data_feed import *
from logger import logger
import threading
import importlib
import asyncio
import sys
import os


# Create a Database object
#db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

# Bot class invoked by bot_manager.py

class Bot:
    def __init__(self, config, database):
        self.config = config
        self.strategy_name = self.config['strategy_name']
        self.broker = self.config['broker_name']
        self.orders = []
        self.data_feed = None
        self.database = database
        self.stop_event = threading.Event()
        self.load_strategy()
        self.in_trade = False
            
    def load_strategy(self):
        """
        Load the strategy module from the strategies folder
        """
        try:
            strategy_module = importlib.import_module(f"strategies.{self.strategy_name}")
            strategy_class = getattr(strategy_module, self.strategy_name)
            self.strategy = strategy_class(self.config, self, logger)
        except Exception as e:
            logger.error(f"Error loading strategy {self.strategy_name}: {e}")
            self.strategy = None

    def set_strategy(self, strategy):
        self.strategy = strategy

    def set_broker(self, broker):
        self.broker = broker

    def place_order(self, order, in_trade):
        self.in_trade = in_trade
        self.orders.append(order)
        #return self.broker.place_order(order)

    def update_orders(self):
        for order in self.orders:
            self.broker.update_order(order)

    def get_orders(self):
        return self.orders

    def subscribe_to_data_feed(self, data_feed):
        self.data_feed = data_feed
        self.data_feed.subscribe(Subscriber(self.config['bot_id']))

    def process_data(self, data):
        if self.strategy:
            self.strategy.process_data(data, self.in_trade)
        else:
            logger.error("No strategy set for this bot")
        # Do something with the incoming data, using the strategy and broker as needed
        #print (f"{self.config['bot_id']} {data}")
        pass

    """
    start a bot
    """
    def start(self):
        logger.warning(f"Starting bot with ID: {self.config['bot_id']}")
        self.stop_event.clear()
        #self.load_strategy()
        # Get symbol_id, interval, and bot_id from the bot configuration
        symbol_id = self.config['symbol_id']
        interval = 'OneMinute'  # Replace with the desired interval
        bot_id = self.config['bot_id']
        broker = self.config['broker_name']

        asyncio.set_event_loop(asyncio.new_event_loop())

        
        # Get historical data for the symbol and interval

        if broker == 'qt':
            historicaldata = self.data_feed.get_qt_historical_data(symbol_id, interval)

        elif broker == 'ib':
            historicaldata = self.data_feed.get_ib_historical_data(symbol_id, interval, bot_id)
        
        elif broker == 'ib_crypto':
            historicaldata = self.data_feed.get_ib_historical_crypto_data(symbol_id, interval, bot_id)
        
        # Pre-process the historical data using the strategy
        self.strategy.process_historical_data(historicaldata)
    
        # Set the bot status to active in the database
        self.database.set_bot_status(self.config['bot_id'], 'true')
        logger.warning(f"Started bot with ID: {self.config['bot_id']}")

        # Start the data feed for this bot
        if broker == 'qt':
            self.data_feed.start_qt_realtimebars(symbol_id, interval, bot_id, self.process_data, self.stop_event)
        
        elif broker == 'ib':
            self.data_feed.start_ib_realtimebars(symbol_id, interval, bot_id, self.process_data, self.stop_event)

        elif broker == 'ib_crypto':
            self.data_feed.start_ib_crypto_realtimebars(symbol_id, interval, bot_id, self.process_data, self.stop_event)

    """
    stop a bot
    """
    def stop(self):
        logger.warning(f"Stopping bot with ID: {self.config['bot_id']}")
        """
        Stop the running bot
        """
        self.stop_event.set()

        # Set the bot status to inactive in the database
        self.database.set_bot_status(self.config['bot_id'], 'false')
        logger.warning(f"Stopped bot with ID: {self.config['bot_id']}")


