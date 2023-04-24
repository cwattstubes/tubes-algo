import cmd
from bot_manager import BotManager, Database, DataFeed
from logger import logger
from config import *
import atexit

class BotCLI(cmd.Cmd):
    intro = 'Welcome to the Bot Manager CLI. Type help or ? to list commands.\n'
    prompt = '(bot-manager) '

    def __init__(self):
        super().__init__()
        self.db = Database(dbname, dbuser, dbpassword, dbhost, dbport)
        self.data_feed = DataFeed("Your Data Feed Name")
        self.bot_manager = BotManager(self.db, self.data_feed)

    def do_start(self, arg):
        'Start a bot by ID: start <bot_id>'
        bot_id = int(arg)
        self.bot_manager.start_bot(bot_id)

    def do_stop(self, arg):
        'Stop a bot by ID: stop <bot_id>'
        bot_id = int(arg)
        self.bot_manager.stop_bot(bot_id)

    def do_restart(self, arg):
        'Restart a bot by ID: restart <bot_id>'
        bot_id = int(arg)
        self.bot_manager.restart_bot(bot_id)

    def do_start_all(self, arg):
        'Start all bots: start_all'
        self.bot_manager.start_all_bots()

    def do_stop_all(self, arg):
        'Stop all bots: stop_all'
        self.bot_manager.stop_all_bots()

    def do_reload(self, arg):
        'Reload bots: reload'
        self.bot_manager.reload_bots()

    def do_running(self, arg):
        'List running bots: running'
        running_bots = self.bot_manager.get_running_bots()
        for bot in running_bots:
            print(f"Bot {bot['id']} is running")

    def do_exit(self, arg):
        'Exit the CLI: exit'
        return True

    def do_EOF(self, arg):
        'Exit the CLI with Ctrl-D'
        return True

    def emptyline(self):
        pass

def main():
    def exit_handler():
        cli.bot_manager.stop_all_bots()

    atexit.register(exit_handler)
    cli = BotCLI()
    cli.cmdloop()

if __name__ == '__main__':
    main()
