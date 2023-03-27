import questrade as qt
from database import *
from config import *
from alphavantage import *

# Create a Database object
db = Database(dbname, dbuser, dbpassword, dbhost, dbport)
av = avClient()
#qt.Token(config_id='qt_auth')._load()
QuestradeAPI = qt.Questrade(config_id='qt_auth')


def update_company_info_from_av(id):
    """
    Backfill company information using Alpha Vantage API
    """

    meta = db.get_company_by_id(id=id)
    if meta is None:
        print ("no matching record")
    else:
        if meta['dataprovider'] == "av":
            symbol = meta['symbol']
            data = av.get_company_overview(symbol=symbol)
            params = {
                'company_name': data['Name'],
                'exchange': data['Exchange'],
                'alphavantage_id': data['Symbol'],
                'currency': data['Currency'],
                'industry': data['Industry'],
                'sector': data['Sector'],
                'description': data['Description']
            }
            db.update_company(id, params)
        
        else:
            print (f"id {id} Symbol {meta['symbol']} is not AV datasource")

def bulk_historical_load_av(id, months, interval):
    """
    Bulk Load historical candles into our db
    """
    meta = db.get_company_by_id(id=id)
    symbol = meta['alphavantage_id']
    
    for df in av.intraday_extended_streaming(symbol=symbol, interval=interval, months=months):
        df['id'] = id
        df['symbol'] = symbol
        df['dataprovider'] = 'av'
        df['broker'] = None
        df = df[['id', 'timestamp', 'open', 'close', 'high', 'low', 'volume', 'symbol', 'dataprovider', 'broker']]

        print (df)
        db.bulk_insert_bars(df)

def search_qt_symbol(string):
    results = QuestradeAPI.get_symbol(string)
    return results


#s = search_qt_symbol(string='su')
#print (s)

#for i in range(1, 11):
#    update_company_info_from_av(id=i)

#bulk_historical_load_av(id=7, interval='1min', months=24)