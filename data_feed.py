import threading
import pandas as pd
import questrade as qt
import datetime
from interactivebrokers import InteractiveBrokers
from time import sleep
import pytz
import asyncio

class DataFeed:
    def __init__(self, name):
        self.name = name
        self.subscribers = []
        self.lock = threading.Lock()
        self.symbols = {}


    def subscribe(self, subscriber):
        with self.lock:
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        with self.lock:
            if subscriber in self.subscribers:
                self.subscribers.remove(subscriber)

    def notify(self, bot_id, data):
        print(f"Notify called for bot ID: {bot_id}")
        with self.lock:
            for subscriber in self.subscribers:
                subscriber.process_data(bot_id, data)

    def get_qt_historical_data(self, qt_id, interval):
        """
        Grabs historical data for a given Questrade symbol ID and interval.
        """
        now = datetime.datetime.now(pytz.timezone("America/New_York"))
        end_time_str = (now - datetime.timedelta(minutes=2)).strftime('%Y-%m-%dT%H:%M:%S')
        start_time_str = (now - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
        start_time = start_time_str + '-04:00'  # Append timezone offset
        end_time = end_time_str + '-04:00'  # Append timezone offset

        # Call _load token to make sure we have a valid access token
        qt.Token(config_id='qt_auth')._load()
        QuestradeAPI = qt.Questrade(config_id='qt_auth')
        data = QuestradeAPI.get_candles(id=qt_id, start_time=start_time, end_time=end_time, interval=interval)

        return data    
    
    def start_qt_realtimebars(self, qt_id, interval, bot_id, callback, stop_event):
        """
        Streams real-time bars for a given Questrade symbol ID and interval, invoking the callback function for each new bar.
        """
        if bot_id is None:
            print ("Must provide bot ID")

        if qt_id not in self.symbols:
            self.symbols[qt_id] = []
        bars = self.symbols[qt_id]
        
        print("Starting data streaming...")
        while True and not stop_event.is_set():
            now = datetime.datetime.now(pytz.timezone("America/New_York"))
            # If there are no bars yet, start at the current time minus one interval
            if not bars:
                end_time_str = (now + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
                start_time_str = (now - datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%S')
                last_bar_time = (now - datetime.timedelta(minutes=1))
            else:
                lastbar = bars[-1]
                last_candle_str = str(lastbar['end'])
                start_time_str = datetime.datetime.fromisoformat(last_candle_str).strftime('%Y-%m-%dT%H:%M:%S')
                end_time_str = (datetime.datetime.fromisoformat(last_candle_str) + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
                last_bar_time = datetime.datetime.fromisoformat(str(lastbar['end']))

            next_bar_time = last_bar_time + datetime.timedelta(seconds=60)

            if now < next_bar_time:
                #print (" now < next bar")
                pass
            else:

                start_time = start_time_str + '-04:00'  # Append timezone offset
                end_time = end_time_str + '-04:00'  # Append timezone offset
                
                # Call _load token to make sure we have a valid access token
                qt.Token(config_id='qt_auth')._load()
                QuestradeAPI = qt.Questrade(config_id='qt_auth')
                data = QuestradeAPI.get_candles(id=qt_id, start_time=start_time, end_time=end_time, interval=interval)
                if "candles" in data and data["candles"]:
                    newbars = pd.DataFrame(data["candles"])

                    # Invoke the callback function for each new bar
                    #for i, row in newbars.iterrows():
                    #    callback(row)
                    callback(newbars)
                    # Append the new bars to the existing list
                    bars.extend(newbars.to_dict('records'))
                else:
                    print("No data returned")   
                    sleep (60)
            # Sleep until the next interval
            print (f" {bot_id} sleeping")
            sleep (5)

    # Add new methods for Interactive Brokers
    def get_ib_historical_data(self, symbol, interval):
        """
        Grabs historical data for a given Interactive Brokers symbol and interval.
        """
        now = datetime.datetime.now(pytz.timezone("America/New_York"))
        end_time = now - datetime.timedelta(minutes=2)
        start_time = now - datetime.timedelta(days=7)
        
        # Convert interval format to Interactive Brokers format
        if interval == "OneMinute":
            ib_interval = "1 min"
        elif interval == "FiveMinutes":
            ib_interval = "5 mins"
        elif interval == "OneHour":
            ib_interval = "1 hour"
        elif interval == "OneDay":
            ib_interval = "1 day"
        else:
            raise ValueError("Unsupported interval")

        ib = InteractiveBrokers(config)
        data = ib.fetch_historical_data(symbol, start_time, end_time, ib_interval)
        
        return data

    def start_ib_realtimebars(self, symbol, interval, bot_id, callback, stop_event):
        """
        Streams real-time bars for a given Interactive Brokers symbol and interval, invoking the callback function for each new bar.
        """

        asyncio.set_event_loop(asyncio.new_event_loop())

        if bot_id is None:
            print("Must provide bot ID")

        if symbol not in self.symbols:
            self.symbols[symbol] = []
        bars = self.symbols[symbol]

        print("Starting data streaming...")
        while True and not stop_event.is_set():
            now = datetime.datetime.now(pytz.timezone("America/New_York"))

            # Convert interval format to Interactive Brokers format
            if interval == "OneMinute":
                ib_interval = "1 min"
            elif interval == "FiveMinutes":
                ib_interval = "5 mins"
            elif interval == "OneHour":
                ib_interval = "1 hour"
            elif interval == "OneDay":
                ib_interval = "1 day"
            else:
                raise ValueError("Unsupported interval")

            start_time = now - datetime.timedelta(minutes=1)
            end_time = now
            #start_time = start_time.strftime("%Y-%m-%d %H:%M:%S%z")
            #end_time = end_time.strftime("%Y-%m-%d %H:%M:%S%z")

            print (f" {bot_id} start time: {start_time} end time: {end_time}")
            config = {
                'host': '127.0.0.1',    
                'port': 7497,
                'client_id': 1
            }
            ib = InteractiveBrokers(config)
            data = ib.fetch_historical_data(symbol, start_time, end_time)
            
            if not data.empty:
                newbars = data

                # Invoke the callback function for each new bar
                #for i, row in newbars.iterrows():
                #    callback(row)
                callback(newbars)

                # Append the new bars to the existing list
                bars.extend(newbars.to_dict('records'))
            else:
                print("No data returned")
                sleep(60)

            # Sleep until the next interval
            print(f" {bot_id} sleeping")
            sleep(5)

    def stop(self):
        # Implement code for stopping data feed subscription
        # For example, this could include disconnecting from a websocket or REST API.
        pass

class Subscriber:
    def __init__(self, bot_id):
        self.bot = bot_id

    def process_data(self, bot_id, data):
        if self.bot.config['bot_id'] == bot_id:
            #print( f"Bot ID: {bot_id}, {data}")
            self.bot.process_data(data)
"""
df = DataFeed("Test Feed")

sub1 = Subscriber(bot_id='1')
#sub2 = Subscriber(bot_id='2')

df.subscribe(sub1)
#df.subscribe(sub2)

# Interactive Brokers Example
#t1 = threading.Thread(target=df.start_ib_realtimebars, args=('AAPL', 'OneMinute', '1', lambda x: df.notify('1', x)))
# Interactive Brokers Example

#stop_event = threading.Event()
#t1 = threading.Thread(target=df.start_ib_realtimebars, args=('AAPL', 'OneMinute', '1', lambda x: df.notify('1', x), stop_event))


# Questrade Example
#t2 = threading.Thread(target=df.start_qt_realtimebars, args=('41726', 'OneMinute', '2', lambda x: df.notify('2', x)))

#t1.start()
#t2.start()
# Wait for threads to complete
#t1.join()
#t2.join()
# Stop the data feed subscription
#df.stop()
"""