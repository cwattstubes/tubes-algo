import threading
import pandas as pd
import questrade as qt
import datetime
from time import sleep
import pytz

class DataFeed:
    def __init__(self, name):
        self.name = name
        self.subscribers = []
        self.lock = threading.Lock()
        self.qtsymbols = {}


    def subscribe(self, subscriber):
        with self.lock:
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        with self.lock:
            if subscriber in self.subscribers:
                self.subscribers.remove(subscriber)

    def notify(self, bot_id, data):
        with self.lock:
            for subscriber in self.subscribers:
                subscriber.process_data(bot_id, data)

    def start_qt_realtimebars(self, qt_id, interval, bot_id, callback):
        """
        Streams real-time bars for a given Questrade symbol ID and interval, invoking the callback function for each new bar.
        """
        if bot_id is None:
            print ("Must provide bot ID")

        if qt_id not in self.qtsymbols:
            self.qtsymbols[qt_id] = []
        bars = self.qtsymbols[qt_id]
        
        while True:
            now = datetime.datetime.now(pytz.timezone("America/New_York"))
            # If there are no bars yet, start at the current time minus one interval
            if not bars:
                end_time_str = (now + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
                start_time_str = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
                last_bar_time = (now - datetime.timedelta(minutes=1))
            else:
                lastbar = bars[-1]
                last_candle_str = str(lastbar['end'])
                start_time_str = datetime.datetime.fromisoformat(last_candle_str).strftime('%Y-%m-%dT%H:%M:%S')
                end_time_str = (datetime.datetime.fromisoformat(last_candle_str) + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
                last_bar_time = datetime.datetime.fromisoformat(str(lastbar['end']))

            next_bar_time = last_bar_time + datetime.timedelta(seconds=60)

            if now < next_bar_time:
                print (" now < next bar")
                pass
            else:

                start_time = start_time_str + '-04:00'  # Append timezone offset
                end_time = end_time_str + '-04:00'  # Append timezone offset
                
                # Call _load token to make sure we have a valid access token
                qt.Token(config_id='qt_auth')._load()
                QuestradeAPI = qt.Questrade(config_id='qt_auth')
                data = QuestradeAPI.get_candles(id=qt_id, start_time=start_time, end_time=end_time, interval=interval)
                if "candles" in data:
                    newbars = pd.DataFrame(data["candles"])

                    # Invoke the callback function for each new bar
                    for i, row in newbars.iterrows():
                        callback(row)

                    # Append the new bars to the existing list
                    bars.extend(newbars.to_dict('records'))

            # Sleep until the next interval
            print ("sleeping")
            sleep (10)

    def stop(self):
        # Implement code for stopping data feed subscription
        # For example, this could include disconnecting from a websocket or REST API.
        pass

class Subscriber:
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def process_data(self, bot_id, data):
        if self.bot_id == bot_id:
            print( f"Bot ID: {bot_id}, {data}")

df = DataFeed("Test Feed")

sub1 = Subscriber(bot_id='1')
sub2 = Subscriber(bot_id='2')

df.subscribe(sub1)
df.subscribe(sub2)


t1 = threading.Thread(target=df.start_qt_realtimebars, args=('37549', 'OneMinute', '1', lambda x: df.notify('1', x)))
t2 = threading.Thread(target=df.start_qt_realtimebars, args=('41726', 'OneMinute', '2', lambda x: df.notify('2', x)))

t1.start()
t2.start()
# Wait for threads to complete
t1.join()
t2.join()
# Stop the data feed subscription
df.stop()