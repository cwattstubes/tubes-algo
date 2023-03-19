import pandas as pd
import requests
from datetime import datetime
from datetime import timedelta
import json

from database import *
from config import *

db = Database(dbname, dbuser, dbpassword, dbhost, dbport)

class TokenStorage:
    @staticmethod
    def readconfig(config_id):
        config = db.get_config(config_id)
        if config is None:
            return {}
        config_data = json.loads(config[2])
        return config_data

    
    @staticmethod
    def writeconfig(config_id, config_data):
        config_data_json = json.dumps(config_data)
        db.set_config(config_id, config_data_json)
        
    @staticmethod
    def is_stored(config_id):
        config = db.get_config(config_id)
        return config is not None
    
class Token:
    def __init__(self, config_id, refresh_token_duration=432000):
        self._config_id = config_id
        self._refresh_token_duration = refresh_token_duration
        self._registration = TokenStorage.readconfig(self._config_id)
        if self._registration is None:
            self._registration = {}
        if not self._is_registered() or self._is_refresh_expired():
            print("Token must be registered")
            self._register()
        elif self._is_expired():
            print("Token is expired")
            self._refresh()


    def _load(self):
        self._registration = TokenStorage.readconfig(self._config_id)
        if not self._is_registered() or self._is_refresh_expired():
            print("Token must be registered")
            self._register()
        elif self._is_expired():
            print("Token is expired")
            self._refresh()

    def _register(self):
        new_token = self._get_manual_token()
        new_registration = self._request_registration(new_token)
        self._set_registration(new_registration)

    def _refresh(self):
        new_token = self.get_refresh_token()
        new_registration = self._request_registration(new_token)
        self._set_registration(new_registration)

    def _request_registration(self, token):
        self._refresh_token_url = self.get_auth_server()
        endpoint = self._refresh_token_url + '/oauth2/token?grant_type=refresh_token&refresh_token=' + token
        response = requests.get(endpoint)
        print(response)
        return response.json()

    def _set_registration(self, new_registration):
        self._registration = new_registration
        self._registration.update({"timestamp": datetime.now().isoformat()})
        self._registration.update({"auth_server": "https://login.questrade.com"})
        TokenStorage.writeconfig(self._config_id, self._registration)

    def _is_refresh_expired(self):
        is_refresh_expired = datetime.now() >= self.get_refresh_expiration()
        return is_refresh_expired

    def _is_expired(self):
        is_expired = datetime.now() >= self.get_token_expiration()
        return is_expired

    def _is_registered(self):
        is_registered = self._registration is not None
        return is_registered

    def get_access_token(self):
        return self._registration['access_token']

    def get_token_type(self):
        return self._registration['token_type']

    def get_refresh_token(self):
        return self._registration['refresh_token']

    def get_api_server(self):
        return self._registration['api_server']

    def get_auth_server(self):
        return self._registration['auth_server']

    def get_timestamp(self):
        return self._registration['timestamp']

    def get_token_expiration(self):
        timestamp = datetime.fromisoformat(self.get_timestamp())
        duration = timedelta(0, seconds=self._registration['expires_in'])
        token_expiration = timestamp + duration
        return token_expiration

    def get_refresh_expiration(self):
        timestamp = datetime.fromisoformat(self.get_timestamp())
        duration = timedelta(0, seconds=self._refresh_token_duration)
        refresh_expiration = timestamp + duration
        return refresh_expiration

    @staticmethod
    def _get_manual_token():
        while True:
            manual_token = input("Enter the manually generated token: ").strip()
            if len(manual_token) < 24:  # general test.
                print("The token is not valid, please try again")
            else:
                return manual_token

class QtAPI:
    def __init__ (self, config_id):
        self._config_id = config_id
        self._token = Token(config_id)

        #requests_cache.install_cache('api_cache', backend='memory', expire_after=300)
    
    def api_get(self, endpoint):
        request_url = self._token.get_api_server() + endpoint
        response = requests.get(request_url, headers=self._get_headers())
        
        if response:
            print ("Request succeeded")
        else:
            print("Request failed: {0}".format(response.status_code))
            
        return response.json()
    
    def get_name(self):
        return self._name
    
    def _get_headers(self):
        token_type = self._token.get_token_type()
        token = self._token.get_access_token()
        auth = "{0} {1}".format(token_type, token)
        return {'Content-Type': 'application/json', "Authorization": auth}
    
class Questrade(QtAPI):
        
    API_VERSION = "v1"
    def __init__(self, config_id): #Constructor
        super().__init__(config_id)
        self.name = "Questrade"

    def get_time(self):
        endpoint = "{0}/time".format(Questrade.API_VERSION)
        return super().api_get(endpoint)
    
    def get_markets(self):
        endpoint = "{0}/markets".format(Questrade.API_VERSION)
        return super().api_get(endpoint)
    
    def get_quotes(self, id):
        endpoint = "{0}/markets/quotes/{1}".format(Questrade.API_VERSION, id)
        return super().api_get(endpoint)
    
    def get_symbol(self, symbol):
        endpoint = "{0}/symbols/search?prefix={1}".format(Questrade.API_VERSION, symbol)
        return super().api_get(endpoint)
    
    def get_accounts(self):
        endpoint = "{0}/accounts".format(Questrade.API_VERSION)
        return super().api_get(endpoint)
    
    def get_positions(self, account_id):
        endpoint = self._get_account_call('positions', account_id)
        return super().api_get(endpoint)

    def get_activities(self, account_id):
        endpoint = self._get_account_call('activities', account_id)
        return super().api_get(endpoint)
    
    def get_orders(self, account_id):
        endpoint = self._get_account_call('orders', account_id)
        return super().api_get(endpoint)
    
    def get_balances(self, account_id):
        endpoint = self._get_account_call('balances', account_id)
        return super().api_get(endpoint)
    
    def _get_account_call(self, function, account_id):
        return "{0}/accounts/{1}/{2}".format(Questrade.API_VERSION, account_id, function)

    def get_candles(self, id, start_time, end_time, interval):
        endpoint = "{0}/markets/candles/{1}/?startTime={2}&endTime={3}&interval={4}".format(Questrade.API_VERSION, id, start_time, end_time, interval)
        return super().api_get(endpoint)
    
    def get_socket(self):
        endpoint = "{0}/notifications?mode=WebSocket".format(Questrade.API_VERSION)
        return super().api_get(endpoint)
    
    def get_sockets(self,ids):
        endpoint = '{0}/markets/quotes?ids={1}&stream=true&mode=WebSocket'.format(Questrade.API_VERSION, ids)
        print (endpoint)
        return super().api_get(endpoint)
    
    def get_symbol_data(self,id):
        endpoint = '{0}/symbols/{1}'.format(Questrade.API_VERSION, id)
        return super().api_get(endpoint)

#Token(config_id='qt_auth')._refresh()
#s = TokenStorage.readconfig(config_id='qt_auth')
#s = Token(config_id='qt_auth').
#print (s)


#Set config
#QuestradeAPI = Questrade(config_id='qt_auth')
# Get the time
#time = QuestradeAPI.get_time()
#print (time)
#s = QuestradeAPI.get_symbol(symbol='SU')
#print (s)