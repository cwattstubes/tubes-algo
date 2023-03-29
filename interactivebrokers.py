from ib_insync import IB, Stock, Crypto, util, BarDataList
import datetime
from database import Database
from time import sleep


class InteractiveBrokers:
    def __init__(self, config):
        self.ib = IB()
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
        
        total_seconds = int((end_date - start_date).total_seconds())
        
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='{} D'.format(total_seconds),
            barSizeSetting='1 min',
            whatToShow='AGGTRADES',
            useRTH=True
        )
        
        return util.df(bars)

    def fetch_realtime_bars(self, symbol, start_date, end_date):
        contract = Stock(symbol, 'SMART', 'USD')

        self.ib.qualifyContracts(contract)
        total_min = int((end_date - start_date).total_seconds())
        print (total_min)
        print (end_date)
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

    
    def fetch_realtime_crypto_bars(self, symbol, start_date, end_date):
        contract = Crypto(symbol, 'PAXOS', 'USD')
        self.ib.qualifyContracts(contract)
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime=end_date,
            durationStr='{} D'.format((end_date - start_date).days),
            barSizeSetting='1 min',
            whatToShow='AGGTRADES',
            useRTH=True
        )
        return util.df(bars)

    def disconnect(self):
        self.ib.disconnect()


#config = {
#    'host': '127.0.0.1',    
#    'port': 7497,
#    'client_id': 1
#}

#ib = InteractiveBrokers(config)
#data = ib.fetch_historical_data('MSFT', datetime.datetime(2023, 3, 25), datetime.datetime(2023, 3, 30))
# print(data)
#data = ib.fetch_realtime_data('MSFT')
#util.startLoop()
#sleep(120)
#print (data)
#ib.disconnect()
