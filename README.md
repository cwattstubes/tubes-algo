<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Algo Trader</title>
</head>
<body>
    <h1>Algo Trader</h1>
    <p>Algo Trader is a Python-based project that combines the APIs of Interactive Brokers and Questrade to fetch
        historical and real-time stock and crypto data. This project aims to provide a unified interface to interact
        with multiple brokerage APIs, allowing users to easily fetch and analyze data.</p>
    <h2>Overview</h2>
    <p>This project consists of several Python files:</p>
    <ol>
        <li><code>main.py</code>: The main entry point of the application, responsible for initializing and running the
            desired functions based on the user's input.</li>
        <li><code>config.py</code>: Contains the configuration settings for the application, such as database
            credentials and brokerage API details.</li>
        <li><code>database.py</code>: Provides an interface to interact with a PostgreSQL database, allowing for the
            storage and retrieval of configuration and data.</li>
        <li><code>interactivebrokers.py</code>: Contains the <code>InteractiveBrokers</code> class, which provides
            methods to fetch historical and real-time data for stocks and cryptocurrencies using the Interactive
            Brokers API.</li>
        <li><code>questrade.py</code>: Contains the <code>Questrade</code> class, which provides methods to fetch
            historical and real-time data for stocks and cryptocurrencies using the Questrade API.</li>
        <li><code>bot.py</code>: Contains the <code>Bot</code> class, which is responsible for handling trading
            strategies and managing orders using the specified brokerage API.</li>
        <li><code>bot_manager.py</code>: Contains the <code>BotManager</code> class, which manages multiple instances
            of the <code>Bot</code> class and provides an interface to monitor and control their actions.</li>
    </ol>
    <h2>Getting Started</h2>
    <p>To get started with the Algo Trader project, follow these steps:</p>
    <ol>
        <li>Install the required Python packages:
            <pre><code>pip install pandas ib_insync psycopg2 requests</code></pre>
        </li>
        <li>Set up a PostgreSQL database and configure the connection settings in <code>config.py</code>.</li>
        <li>Obtain the necessary API credentials for Interactive Brokers and Questrade, and configure the settings in
            <code>config.py</code>.</li>
        <li>Run the <code>main.py</code> script to start the application:
            <pre><code>python main.py</code></pre>
        </li>
    </ol>
    <h2>Usage</h2>
    <p>Once the application is running, you can use the provided methods in the <code>InteractiveBrokers</code>,
        <code>Questrade</code>, <code>Bot</code>, and <code>BotManager</code> classes to fetch historical and real-time
        data for stocks and cryptocurrencies, manage trading strategies, and monitor bot performance.</p>
    <p>Example usage:</p>
    <pre><code>Bot
from bot_manager import BotManager

# Interactive Brokers example
ib_config = {
    'host': 'YOUR_HOST',
    'port': 'YOUR_PORT',
    'client_id': 'YOUR_CLIENT_ID'
}

ib = InteractiveBrokers(ib_config, 1)
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()
symbol = 'AAPL'
historical_data = ib.fetch_historical_data(symbol, start_date, end_date)
print(historical_data)
ib.disconnect()

# Questrade example
qt_config_id = 'YOUR_CONFIG_ID'
qt = Questrade(qt_config_id)
symbol_info = qt.get_symbol('AAPL')
symbol_id = symbol_info['symbols'][0]['symbolId']
candles = qt.get_candles(symbol_id, start_date.isoformat(), end_date.isoformat(), 'OneHour')
print(candles)

# Bot example
bot1 = Bot('Bot 1', ib)
bot1.start_trading()

# Bot Manager example
manager = BotManager()
manager.add_bot(bot1)
manager.start_all_bots()
manager.stop_all_bots()
</code></pre>
<p>By using the examples above, you can fetch historical data from both Interactive Brokers and Questrade, create a trading bot using the Interactive Brokers API, and manage the bot using the BotManager class.</p>
</body>
</html>
