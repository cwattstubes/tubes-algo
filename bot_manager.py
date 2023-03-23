from database import Database
from config import *
from bot import Bot
from data_feed import DataFeed
import threading


# Create a Database object
db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

class BotManager:
    def __init__(self, database: Database, data_feed: DataFeed):
        self.database = database
        self.bots = []
        self.data_feed = data_feed
        self.load_bots()

    def load_bots(self):
        # Read bot configuration from the database
        bot_configs = self.database.get_all_bots_active()

        # Create bot instances from the configuration
        for bot_config_tuple in bot_configs:
            bot_config_keys = ['bot_id', 'bot_name', 'strategy_name', 'symbol_id', 'account_id', 'broker_name']
            bot_config = {key: value for key, value in zip(bot_config_keys, bot_config_tuple)}
            bot = Bot(bot_config, self.database)
            bot.subscribe_to_data_feed(self.data_feed)
            self.bots.append(bot)
            print(f"Bot loaded: {bot.config['bot_id']}")

    def start_all_bots(self):
        print(f"Starting all {len(self.bots)} bots...")
        for bot in self.bots:
            bot_thread = threading.Thread(target=bot.start)  # Create a new thread for the bot
            bot_thread.start()  # Start the thread
            print(f"Bot with ID: {bot.config['bot_id']} started in a new thread.")  # Print a message to confirm
                
    def stop_all_bots(self):
        for bot in self.bots:
            bot.stop()
            
    def restart_all_bots(self):
        self.stop_all_bots()
        self.start_all_bots()


#db.set_bot_config('my_bot_4', 'FU', '3', '11111', 'paper')
bot_config = db.get_bot_config_id('1')

data_feed = DataFeed("Your Data Feed Name")
bot_manager = BotManager(db, data_feed)
bot_manager.start_all_bots()

for bot in bot_manager.bots:
    print(f"Bot ID: {bot.config['bot_id']}, Bot Name: {bot.config['bot_name']}, Strategy: {bot.config['strategy_name']}")
