from flask import Flask, render_template, Response, jsonify
from flask_sse import sse
from bot_manager import BotManager, Database, DataFeed
from logger import logger
import atexit
from config import *
import os

def create_app():
    app = Flask(__name__)
    #app.config["REDIS_URL"] = "redis://localhost"

    # Create a Database object
    db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

    # Create a DataFeed object
    data_feed = DataFeed("Your Data Feed Name")

    # Create a BotManager object
    bot_manager = BotManager(db, data_feed)
    
    def exit_handler():
        bot_manager.stop_all_bots()
    
    # Register the stop_all_bots function to be called when the program exits
    atexit.register(exit_handler)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/start_all_bots', methods=['POST'])
    def start_all_bots():
        bot_manager.start_all_bots()
        return "Starting all bots..."

    @app.route('/stop_all_bots', methods=['POST'])
    def stop_all_bots():
        bot_manager.stop_all_bots()
        return "Stopping all bots..."
    
    @app.route('/start_bot/<int:bot_id>', methods=['POST'])
    def start_bot(bot_id):
        success = bot_manager.start_bot(bot_id)
        if success:
            return f"Starting bot {bot_id}..."
        else:
            return f"Failed to start bot {bot_id}.", 400

    @app.route('/stop_bot/<int:bot_id>', methods=['POST'])
    def stop_bot(bot_id):
        success = bot_manager.stop_bot(bot_id)
        if success:
            return f"Stopping bot {bot_id}..."
        else:
            return f"Failed to stop bot {bot_id}.", 400
        
    @app.route('/restart_bot/<int:bot_id>', methods=['POST'])
    def restart_bot(bot_id):
        success = bot_manager.restart_bot(bot_id)
        if success:
            return f"Restarting bot {bot_id}..."
        else:
            return f"Failed to restart bot {bot_id}.", 400

    @app.route('/reload_bots', methods=['POST'])
    def reload_bots():
        bot_manager.reload_bots()
        return "Reloading bots..."
    
    @app.route('/running_bots')
    def running_bots():
        bots = bot_manager.get_running_bots()
        return jsonify(bots)

    @app.route('/get_log_file')
    def get_log_file():
        log_file_path = 'logs/console.log'
        mtime = os.path.getmtime(log_file_path)

        with open(log_file_path, 'r') as file:
            lines = file.readlines()

        last_10_lines = ''.join(lines[-20:])
        return jsonify({'content': last_10_lines, 'mtime': mtime})


    return app
'''
def generate_console_output():
    while True:
        record = log_queue.get()
        message = logger.handlers[0].format(record)  # Use the first handler (file handler) to format the message
        yield f"data: {message}\n\n"
'''
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)