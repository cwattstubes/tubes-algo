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
        bot_configs = self.database.get_all_bots_active()
        
        # Create bot instances from configuration
        for bot_config in bot_configs:
            bot_config = {
                'bot_name': bot_config[0],
                'strategy_name': bot_config[1],
                'symbol_id': bot_config[2],
                'account_id': bot_config[3],
                'broker_name': bot_config[4]
            }
            bot = Bot(bot_config)
            bot.subscribe_to_data_feed(self.data_feed)
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
bot_config = db.get_bot_config_id('1')
print (bot_config)
bot_manager = BotManager(db)
bot_manager.start_all_bots()
