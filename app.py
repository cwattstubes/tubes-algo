from flask import Flask, render_template, Response
from flask_sse import sse
from bot_manager import BotManager, Database, DataFeed
from logger import log_queue, setup_logger
from config import *

def create_app():
    app = Flask(__name__)
    app.config["REDIS_URL"] = "redis://localhost"

    # Create a Database object
    db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

    # Create a DataFeed object
    data_feed = DataFeed("Your Data Feed Name")

    # Create a BotManager object
    bot_manager = BotManager(db, data_feed)

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

    @app.route('/console_output')
    def stream_console_output():
        def generate():
            while True:
                message = log_queue.get()
                yield f"event: console_output\ndata: {message}\n\n"
        return Response(generate(), content_type='text/event-stream')

    @app.route('/logs')
    def view_console_output():
        return render_template('logs.html')


    # Initialize logger within the Flask application context
    with app.app_context():
        logger = setup_logger(log_queue, log_file='logs/console.log')
        bot_manager.logger = logger

    return app

def generate_console_output():
    while True:
        record = log_queue.get()
        message = logger.handlers[0].format(record)  # Use the first handler (file handler) to format the message
        yield f"data: {message}\n\n"

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
