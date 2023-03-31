import os
import sys
from logger import logger

from database import Database
from config import *
from bot import Bot
from data_feed import DataFeed
import threading
from time import sleep

# Create a Database object
db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

class BotManager:
    def __init__(self, database: Database, data_feed: DataFeed):
        self.database = database
        self.bots = []
        self.data_feed = data_feed
        self.bot_threads = []
        self.load_bots()

    def load_bots(self):
        # Read bot configuration from the database
        bot_configs = self.database.get_bots_autostart()

        # Create bot instances from the configuration
        for bot_config_tuple in bot_configs:
            bot_config_keys = ['bot_id', 'bot_name', 'strategy_name', 'symbol_id', 'account_id', 'broker_name']
            bot_config = {key: value for key, value in zip(bot_config_keys, bot_config_tuple)}
            bot = Bot(bot_config, self.database)
            bot.subscribe_to_data_feed(self.data_feed)
            self.bots.append(bot)
            logger.warning(f"Bot loaded: {bot.config['bot_id']}")

    def start_all_bots(self):
        logger.warning(f"Starting all {len(self.bots)} bots...")
        self.bot_threads = []
        for bot in self.bots:
            bot_thread = threading.Thread(target=bot.start)  # Create a new thread for the bot
            self.bot_threads.append(bot_thread)
            bot_thread.start()  # Start the thread
            logger.warning(f"Bot with ID: {bot.config['bot_id']} started in a new thread.")  # Print a message to confirm
                
    def stop_all_bots(self):
        for bot in self.bots:
            bot.stop()
        # Wait for all threads to terminate
        for bot_thread in self.bot_threads:
            bot_thread.join() 
        logger.warning(f"All {len(self.bots)} bots stopped.")
    def restart_all_bots(self):
        self.stop_all_bots()
        self.start_all_bots()

    def get_bot(self, bot_id):
        for bot in self.bots:
            if bot.config['bot_id'] == bot_id:
                return bot
        return None

    def get_running_bots(self):
        running_bots = self.database.get_running_bots()
        return [{'id': bot_id, 'name': bot_name, 'strategy': strategy_name} for bot_id, bot_name, strategy_name in running_bots]
    
    def stop_bot(self, bot_id):
        bot = self.get_bot(bot_id)
        if bot is not None:
            bot.stop()
            return True
        return False
    
    def start_bot(self, bot_id):
        bot_loaded = False
        for bot in self.bots:
            if bot.config['bot_id'] == bot_id:
                bot_loaded = True
                bot.start()
                break

        if not bot_loaded:
            bot_config_tuple = self.database.get_bot_config_id(bot_id)
            if bot_config_tuple:
                bot_config_keys = ['bot_id', 'bot_name', 'strategy_name', 'symbol_id', 'account_id', 'broker_name']
                bot_config = {key: value for key, value in zip(bot_config_keys, bot_config_tuple)}
                bot = Bot(bot_config, self.database)
                bot.subscribe_to_data_feed(self.data_feed)
                self.bots.append(bot)

                bot_thread = threading.Thread(target=bot.start)  # Create a new thread for the bot
                self.bot_threads.append(bot_thread)
                bot_thread.start()  # Start the thread

                logger.warning(f"Bot with ID: {bot_id} started in a new thread.")  # Print a message to confirm
                return True
        return False


'''
#db.set_bot_config('my_bot_4', 'FU', '3', '11111', 'paper')
bot_config = db.get_bot_config_id('1')

data_feed = DataFeed("Your Data Feed Name")
bot_manager = BotManager(db, data_feed)
bot_manager.start_all_bots()

for bot in bot_manager.bots:
    logger.warning(f"Bot ID: {bot.config['bot_id']}, Bot Name: {bot.config['bot_name']}, Strategy: {bot.config['strategy_name']}")

bleh = bot_manager.get_bot(4)
print (bleh)
#bot_manager.stop_bot(1)

#sleep (10)

#bot_manager.start_bot(3)
'''