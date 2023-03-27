import psycopg2
from psycopg2.extras import execute_values


class DatabaseAdmin:
    def __init__(self, dbname, dbuser, dbpassword, dbhost, dbport):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=dbuser,
            password=dbpassword,
            host=dbhost,
            port=dbport
        )

    def __del__(self):
        self.conn.close()

    def execute_query(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchall()
        return result

    def execute_update(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            self.conn.commit()

    def create_companies_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            company_name TEXT,
            exchange TEXT,
            symbol TEXT UNIQUE,
            questrade_id TEXT UNIQUE,
            alphavantage_id TEXT UNIQUE,
            ibx_id TEXT UNIQUE,
            broker TEXT,
            dataprovider TEXT,
            currency TEXT,
            industry TEXT,
            sector TEXT,
            website TEXT,
            description TEXT
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
        self.conn.commit()

    def create_stock_data_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER REFERENCES companies(id),
            timestamp TIMESTAMP NOT NULL,
            open DOUBLE PRECISION,
            close DOUBLE PRECISION,
            high DOUBLE PRECISION,
            low DOUBLE PRECISION,
            volume DOUBLE PRECISION,
            symbol TEXT NOT NULL,
            dataprovider TEXT,
            broker TEXT,
            PRIMARY KEY (id, timestamp)
        );
        
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            cur.execute("SELECT create_hypertable ('stock_data', 'timestamp')")
        self.conn.commit()

    def create_config_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS config (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            value TEXT
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
        self.conn.commit()

    def create_bot_config_table(self):
        query = """
        CREATE TABLE bot_config (
            bot_id SERIAL PRIMARY KEY,
            bot_name TEXT UNIQUE,
            strategy_name TEXT,
            symbol_id INT,
            account_id TEXT,
            broker_name TEXT,
            active BOOLEAN DEFAULT FALSE,
            autostart BOOLEAN DEFAULT FALSE
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __del__(self):
        self.close()


class Database:
    def __init__(self, dbname, dbuser, dbpassword, dbhost, dbport):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=dbuser,
            password=dbpassword,
            host=dbhost,
            port=dbport
        )

    def __del__(self):
        self.conn.close()
    
    def get_cursor(self):
        return self.conn.cursor()

    def execute_query(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchall()
        return result

#    def execute_update(self, query, params=None):
#        with self.conn.cursor() as cur:
#            cur.execute(query, params)
#            self.conn.commit()
    def execute_update(self, query, *params):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            self.conn.commit()


    def set_config(self, name, value):
        query = "INSERT INTO config (name, value) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET value = %s"
        params = (name, value, value)
        self.execute_update(query, *params)

    def get_config(self, name):
        query = "SELECT * FROM config WHERE name = %s"
        params = (name,)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        return row
    
#    def set_bot_config(self, bot_id, bot_name, strategy_name, account_id, broker_id):
#        query = "INSERT INTO bot_config (bot_id, bot_name, strategy_name, account_id, broker_name) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (bot_name) DO UPDATE SET strategy_name = %s, account_id = %s, broker_name = %s"
#        params = (bot_id, bot_name, strategy_name, account_id, broker_id, strategy_name, account_id, broker_id)
#        self.execute_update(query, *params)
    def set_bot_config(self, bot_name, strategy_name, symbol_id, account_id, broker_name, bot_id=None):
            
        if bot_id is None:
            query = """
            INSERT INTO bot_config (bot_name, strategy_name, symbol_id, account_id, broker_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (bot_id) DO UPDATE 
                SET strategy_name = excluded.strategy_name,
                    account_id = excluded.account_id,
                    broker_name = excluded.broker_name
            RETURNING bot_id;
            """
            params = (bot_name, strategy_name, symbol_id, account_id, broker_name)
        else:
            query = """
            INSERT INTO bot_config (bot_id, bot_name, symbol_id, strategy_name, account_id, broker_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (bot_id) DO UPDATE 
                SET bot_name = excluded.bot_name,
                    strategy_name = excluded.strategy_name,
                    account_id = excluded.account_id,
                    broker_name = excluded.broker_name
            RETURNING bot_id;
            """
            params = (bot_id, bot_name, symbol_id, strategy_name, account_id, broker_name)

        self.execute_update(query, *params)

    def get_bot_config_name(self, bot_name):
        query = "SELECT * FROM bot_config WHERE bot_name = %s"
        params = (bot_name,)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        return row
    
    def get_bot_config_id(self, bot_id):
        query = "SELECT * FROM bot_config WHERE bot_id = %s"
        params = (bot_id,)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        return row
    
    def get_bots_autostart(self):
        query = "SELECT * FROM bot_config WHERE autostart = true"
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        return rows
    
    def set_bot_status(self, bot_id, status):
        query = "UPDATE bot_config SET active = %s WHERE bot_id = %s"
        params = (status, bot_id)
        self.execute_update(query, *params)

    def get_bot_status(self, bot_id):
        query = "SELECT active FROM bot_config WHERE bot_id = %s"
        params = (bot_id,)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        return row

#    def get_config(self, name):
#        query = "SELECT * FROM config WHERE name = %s"
#        params = (name,)
#        with self.conn.cursor() as cur:
#            cur.execute(query, params)
#            row = cur.fetchone()
#        if row:
#            return {"id": row[0], "name": row[1], "value": row[2]}
#        else:
#            return None
            
    def create_company(self, symbol, broker, dataprovider):
        query = "insert into companies (symbol, broker, dataprovider) VALUES (%s, %s, %s)" 
        params = (symbol, broker, dataprovider)
        return self.execute_update(query, params)
    
    def update_company(self, id, params):
        query = """
        UPDATE companies SET 
            company_name = %s, 
            exchange = %s, 
            questrade_id = %s, 
            alphavantage_id = %s, 
            ibx_id = %s, 
            currency = %s, 
            industry = %s, 
            sector = %s, 
            website = %s, 
            description = %s 
        WHERE id = %s
        """
        param_values = [
            params.get('company_name'),
            params.get('exchange'),
            params.get('questrade_id'),
            params.get('alphavantage_id'),
            params.get('ibx_id'),
            params.get('currency'),
            params.get('industry'),
            params.get('sector'),
            params.get('website'),
            params.get('description'),
            id,
        ]
        return self.execute_update(query, param_values)

    def get_company_by_id(self, id):
        query = """
        SELECT * from companies where id = %s
        """
        params = (id,)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
        if row is None:
            return {}
        return {
            'id': row[0], 'company_name': row[1], 'exchange': row[2], 'symbol': row[3],
            'questrade_id': row[4], 'alphavantage_id': row[5], 'ibx_id': row[6], 'broker': row[7], 
            'dataprovider': row[8], 'currency': row[9], 'industry': row[10], 'sector': row[11], 'website': row[12], 'description': row[13]}
    

    def bulk_insert_bars(self, data):
        values = [tuple(x) for x in data.to_numpy()]
        query = """
            INSERT INTO stock_data (
                id, timestamp, open, close, high, low, volume, symbol, dataprovider, broker
                ) VALUES %s
            """

        with self.conn.cursor() as cur:
            execute_values(cur, query, values)
        self.conn.commit()




#from config import *
# Create a Database object
#db = DatabaseAdmin(dbname, dbuser, dbpassword, dbhost, dbport)
#db.create_companies_table()
#db.create_stock_data_table()
#db.create_bot_config_table()
