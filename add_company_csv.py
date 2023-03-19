import csv
import sys
from database import *
from config import *

# Create a DatabaseAdmin object
db_admin = Database(dbname, dbuser, dbpassword, dbhost, dbport)

def read_csv(file_path):
    """Reads CSV file and returns a list of dictionaries"""
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]
    return rows

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide path to CSV file")
        sys.exit(1)

    file_path = sys.argv[1]
    rows = read_csv(file_path)

    db_admin = Database(
        dbname, dbuser, dbpassword, dbhost, dbport)

    for row in rows:
        symbol = row['symbol']
        broker = row['broker']
        dataprovider = row['dataprovider']

        db_admin.create_company(symbol, broker, dataprovider)

    print("Companies added successfully.")