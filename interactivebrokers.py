from ib_insync import IB, Stock, Crypto, util, BarDataList
import datetime
from database import Database
from time import sleep


class InteractiveBrokers:
    def __init__(self, config, bot_id):
        self.ib = IB()
        config["client_id"] = bot_id
        self.ib.connect(config['host'], config['port'], config['client_id'])

    def fetch_historical_data(self, symbol, start_date, end_date):
        contract = Stock(symbol, 'SMART', 'USD')

        self.ib.qualifyContracts(contract)
        total_days = (end_date - start_date).days

        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='{} D'.format(total_days),
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True
        )
        return util.df(bars)
        #return bars

    def fetch_historical_crypto_data(self, symbol, start_date, end_date):
        contract = Crypto(symbol, 'PAXOS', 'USD')
        self.ib.qualifyContracts(contract)
        total_days = (end_date - start_date).days

        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='{} D'.format(total_days),
            barSizeSetting='1 min',
            whatToShow='AGGTRADES',
            useRTH=True
        )
        
        return util.df(bars)

    def fetch_realtime_bars(self, symbol, start_date, end_date):
        contract = Stock(symbol, 'SMART', 'USD')

        self.ib.qualifyContracts(contract)
        total_min = int((end_date - start_date).total_seconds())
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='{} S'.format(total_min),
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True,
            keepUpToDate=False
        )
        return util.df(bars)

    def process_realtime_crypto_bar(self, bar, contract):
        print(f'Real-time bar: {bar.date} {contract.localSymbol} {bar.close}')

    def fetch_realtime_crypto_bars(self, symbol, start_date, end_date):
        contract = Crypto(symbol, 'PAXOS', 'USD')
        
        self.ib.qualifyContracts(contract)
        total_min = int((end_date - start_date).total_seconds())
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='{} S'.format(total_min),
            barSizeSetting='1 min',
            whatToShow='AGGTRADES',
            useRTH=True,
            keepUpToDate=False
        )
        return util.df(bars)




    def disconnect(self):
        self.ib.disconnect()

'''
config = {
    'host': '127.0.0.1',    
    'port': 7497,
    'client_id': 1
}

#ib = InteractiveBrokers(config)
#data = ib.fetch_historical_data('MSFT', datetime.datetime(2023, 3, 25), datetime.datetime(2023, 3, 30))
# print(data)
#data = ib.fetch_realtime_crypto_bars('BTC', datetime.datetime(2023, 3, 25), datetime.datetime(2023, 3, 30))
#sleep(120)
#print (data)
#ib.disconnect()

# Testing real-time data
ib = InteractiveBrokers(config)
util.startLoop()

# Start real-time data streaming
bars = ib.fetch_realtime_crypto_bars('BTC')

print(bars)
# Keep the script running to receive real-time data
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nTerminating real-time data streaming...")

# Cancel the real-time bars subscription
ib.ib.cancelMktData(bars.contract)
# Disconnect from Interactive Brokers
ib.disconnect()
'''