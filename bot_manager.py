import os
import sys
import threading
from time import sleep

from logger import logger
from database import Database
from config import *
from bot import Bot
from data_feed import DataFeed


class BotManager:
    def __init__(self, database: Database, data_feed: DataFeed):
        self.database = database
        self.bots = []
        self.data_feed = data_feed
        self.bot_threads = []
        self.load_bots()

    def _create_bot(self, bot_config_tuple):
        """Create a Bot instance from the given configuration tuple."""
        bot_config_keys = ['bot_id', 'bot_name', 'strategy_name', 'symbol_id', 'account_id', 'broker_name']
        bot_config = {key: value for key, value in zip(bot_config_keys, bot_config_tuple)}
        bot = Bot(bot_config, self.database)
        bot.subscribe_to_data_feed(self.data_feed)
        return bot

    def load_bots(self):
        """Load bots from the database and store them in the bots list."""
        bot_configs = self.database.get_bots_autostart()
        self.bots = [self._create_bot(bot_config_tuple) for bot_config_tuple in bot_configs]
        for bot in self.bots:
            logger.warning(f"Bot loaded: {bot.config['bot_id']}")

    def _start_bot_in_thread(self, bot):
        """Start the given bot in a new thread."""
        bot_thread = threading.Thread(target=bot.start)
        self.bot_threads.append(bot_thread)
        bot_thread.start()
        logger.warning(f"Bot with ID: {bot.config['bot_id']} started in a new thread.")

    def start_all_bots(self):
        """Start all bots stored in the bots list."""
        logger.warning(f"Starting all {len(self.bots)} bots...")
        self.bot_threads = []
        for bot in self.bots:
            self._start_bot_in_thread(bot)

    def stop_all_bots(self):
        """Stop all bots stored in the bots list."""
        for bot in self.bots:
            bot.stop()
        for bot_thread in self.bot_threads:
            bot_thread.join()
        logger.warning(f"All {len(self.bots)} bots stopped.")

    def restart_all_bots(self):
        self.stop_all_bots()
        self.start_all_bots()

    def reload_bots(self):
        logger.warning("Reloading bots...")
        self.stop_all_bots()
        self.bots = []
        self.bot_threads = []
        self.load_bots()
        self.start_all_bots()
        logger.warning("Bots reloaded.")

    def get_bot(self, bot_id):
        return next((bot for bot in self.bots if bot.config['bot_id'] == bot_id), None)

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
        bot = self.get_bot(bot_id)
        if bot is not None:
            self._start_bot_in_thread(bot)
            return True

        bot_config_tuple = self.database.get_bot_config_id(bot_id)
        if bot_config_tuple:
            bot = self._create_bot(bot_config_tuple)
            self.bots.append(bot)
            self._start_bot_in_thread(bot)
            return True

        return False

    def restart_bot(self, bot_id):
        bot = self.get_bot(bot_id)
        if bot is not None:
            bot.stop()
            self._start_bot_in_thread(bot)
            return True
        return False

'''
if __name__ == "__main__":
    # Create a Database object
    db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

    # Create BotManager instance
    bot_manager = BotManager(db, DataFeed())

    # Example usage of BotManager
    bot_manager.start_all_bots()
    sleep(10)
    bot_manager.stop_all_bots()
'''