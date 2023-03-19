from database import *
from config import *
from bot import *

# Create a Database object
db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

class BotManager:
    def __init__(self, database):
        self.database = database
        self.bots = []
        self.load_bots()
        
    def load_bots(self):
        # Read bot configuration from database
        bot_configs = self.database.select_all('bot_config')
        
        # Create bot instances from configuration
        for bot_config in bot_configs:
            bot = Bot(bot_config['bot_name'], bot_config['strategy_name'], bot_config['symbol_id'], bot_config['account_id'], bot_config['broker_name'])
            self.bots.append(bot)
            
    def start_all_bots(self):
        for bot in self.bots:
            bot.start()
            
    def stop_all_bots(self):
        for bot in self.bots:
            bot.stop()
            
    def restart_all_bots(self):
        self.stop_all_bots()
        self.start_all_bots()


#db.set_bot_config('my_bot_4', 'FU', '3', '11111', 'paper')
bot_config = db.get_bot_config_id('13')
print (bot_config)