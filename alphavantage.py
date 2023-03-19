import requests
import pandas as pd
import io
from typing import List
from database import Database
from config import *

from ratelimit import limits, sleep_and_retry
import time

def rate_limiter(max_requests, per_seconds):
    """
    A decorator function that can be used to rate limit HTTP requests.
    """
    requests_made = 0
    last_request_time = 0

    def decorate(func):
        def wrapper(*args, **kwargs):
            nonlocal requests_made
            nonlocal last_request_time

            current_time = time.time()
            time_since_last_request = current_time - last_request_time

            if time_since_last_request < (1 / per_seconds):
                time.sleep((1 / per_seconds) - time_since_last_request)

            result = func(*args, **kwargs)

            requests_made += 1
            last_request_time = time.time()

            if requests_made == max_requests:
                time_since_first_request = current_time - last_request_time
                if time_since_first_request < 1:
                    time.sleep(1 - time_since_first_request)
                requests_made = 0

            return result
        return wrapper
    return decorate

class avClient:
    def __init__(self):
        self.db = Database(dbname, dbuser, dbpassword, dbhost, dbport)
        self.cursor = self.db.get_cursor()
        api_key_row = self.db.get_config('alphavantage_api_key')
        self.api_key = api_key_row[2]
        self.base_url = 'https://www.alphavantage.co/query'
    
    @sleep_and_retry
    @limits(calls=4, period=60)
    def _get_data(self, params):
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))
    
    def search_symbol(self, keyword: str) -> List[str]:
        """
        Searches AlphaVantage for a given string and returns list of symbols

        Args:
            keyword (str): The string to search for

        Returns:
            List[str]: List of symbols that match the search string
        """
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keyword,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params).json()
        
        if 'bestMatches' in response:
            return [match['1. symbol'] for match in response['bestMatches']]

        else:
            return []
        
    def get_market_status(self, exchange):
        exchange_map = {
            'NASDAQ': 'NASDAQ',
            'NYSE': 'NYSE',
            'AMEX': 'AMEX',
            'BATS': 'BATS',
            'Toronto': 'TSX',
            'Toronto Ventures': 'TSX-V',
            'FOREX': 'Global',
            'CRYPTO': 'Global'
        }
        params = {
            'function': 'MARKET_STATUS',
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params).json()

        for market in response['markets']:
            if market['market_type'] == 'Equity':
                for primary_exchange in market['primary_exchanges'].split(', '):
                    if primary_exchange in exchange_map and exchange_map[primary_exchange] == exchange:
                        return market['current_status']
        # exchange not found in exchange_map
        return f"Error: '{exchange}' is not a recognized exchange."
    @sleep_and_retry
    @limits(calls=4, period=60)
    def get_company_overview(self, symbol):
        """
        Calls AlphaVantage OVERVIEW func to get Company meta data
        """

        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params).json()
        if 'Name' in response:
            return response;
        else:
            return f'symbol not found'
  
    def intraday_extended(self, symbol, interval, months):
        """
        Calls AlphaVantage returns historical intraday time series for the trailing N months
        """
        # the API requires you to slice up your requests (per month)
        # like "year1month1", "year1month2", ..., "year2month1" etc...
        time_range = range(1, months+1)  # (last N months)
        data = []
        for i in time_range:
            slice = "year1month" + str(i) if i <= 12 else "year2month" + str(i - 12)

            params = {
                'function': 'TIME_SERIES_INTRADAY_EXTENDED',
                'symbol': symbol,
                'interval': interval,
                'slice': slice,
                'apikey': self.api_key
            }
            try:
                df = self._get_data(params)
                data.append(df)
            except requests.exceptions.RequestException as e:
                print(f"Request failed with error {e}")
        return pd.concat(data)
    
    def intraday_extended_streaming(self, symbol, interval, months):
        """
        Calls AlphaVantage returns historical intraday time series for the trailing N months
        """
        # the API requires you to slice up your requests (per month)
        # like "year1month1", "year1month2", ..., "year2month1" etc...
        time_range = reversed(range(1, months+1))  # (last N months)
        for i in time_range:
            slice = "year1month" + str(i) if i <= 12 else "year2month" + str(i - 12)

            params = {
                'function': 'TIME_SERIES_INTRADAY_EXTENDED',
                'symbol': symbol,
                'interval': interval,
                'slice': slice,
                'apikey': self.api_key
            }
            try:
                df = self._get_data(params)
                df = df.rename(columns={
                        'time': 'timestamp',
                        'open': 'open',
                        'high': 'high',
                        'low': 'low',
                        'close': 'close',
                        'volume': 'volume'})
                yield df
            except requests.exceptions.RequestException as e:
                print(f"Request failed with error {e}")

    
    
    


#client = avClient()
#symols = client.intraday_extended(symbol='IBM', interval='1min', months=12)
#symols = client.search_symbol(keyword='GOOG')
#print(symols)
