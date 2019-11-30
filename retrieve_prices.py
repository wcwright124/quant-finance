import json
import MySQLdb as mdb
import requests
import time
import warnings

from datetime import datetime as dt

ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co'
ALPH_VANTAGE_TIME_SERIES_CALL = 'query?function=TIME_SERIES_DAILY_ADJUSTED'
with open('api_key.txt', 'r') as file:
    ALPHA_VANTAGE_API_KEY = file.readline().rstrip()

TICKER_COUNT = 10 # Set to 10 for testing purposes. Change to 505 to download all tickers in S&P 500.
WAIT_TIME_SECS = 15.0 # Wait time between API calls

# Open db connection to MySQL instance
DB_HOST = 'localhost'
DB_USER = 'sec_user'
with open ('sec_user_pass.txt', 'r') as file:
    DB_PASS = file.readline().rstrip()
DB_NAME = 'securities_master'
con = mdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)

def get_dict_of_db_tickers():
    """
    Returns a dictionary of the form {ticker_symbol: id}
    """
    cur = con.cursor()
    cur.execute("SELECT id, ticker FROM symbol")
    con.commit()
    data = cur.fetchall()
    return {d[1]: d[0] for d in data}

def get_list_of_db_tickers():
    """
    Returns list of ticker symbols from symbol table of securities_master database.
    """
    cur = con.cursor()
    cur.execute("SELECT id, ticker FROM symbol")
    con.commit()
    data = cur.fetchall()
    return [(d[0], d[1]) for d in data]

def get_alpha_vantage_symbol_call(ticker):
    """
    Constructs full API call to AlphaVantage based on the user
    provided API key and desired ticker symbol
    """
    return "%s/%s&symbol=%s&outputsize=full&apikey=%s" % (
        ALPHA_VANTAGE_BASE_URL,
        ALPH_VANTAGE_TIME_SERIES_CALL,
        ticker,
        ALPHA_VANTAGE_API_KEY
    )

def get_daily_historic_data_alphavantage(ticker):
    """
    Use the generated API call to query AlphaVantage with the appropriate
    API key and returns a list of price tuples for that particular ticker.
    """
    av_url = get_alpha_vantage_symbol_call(ticker)

    try:
        av_data_js = requests.get(av_url)
        data = json.loads(av_data_js.text)['Time Series (Daily)']
    except Exception as e:
        print(
            "Could not download AlphaVantage data for %s ticker "
            "(%s)...skipping." % (ticker, e)
        )
        return []
    else:
        prices = []
        for date_str in sorted(data.keys()):
            bar = data[date_str]
            prices.append(
                (
                    dt.strptime(date_str, '%Y-%m-%d'),
                    float(bar['1. open']),
                    float(bar['2. high']),
                    float(bar['3. low']),
                    float(bar['4. close']),
                    int(bar['6. volume']),
                    float(bar['5. adjusted close'])
                )
            )
        return prices

def insert_daily_data_into_db(data_vendor_id, symbol_id, daily_data):
    """
    Takes list of tuples of daily data and adds into the MySQL database.
    Appends the vendor ID and symbol ID to the data to match the schema
    for the daily_price table.
    """
    now = dt.utcnow()

    daily_data = [
        (data_vendor_id, symbol_id, d[0], now, now,
        d[1], d[2], d[3], d[4], d[5], d[6])
        for d in daily_data
    ]
    column_str = (
        "data_vendor_id, symbol_id, price_date, created_date, "
        "last_updated_date, open_price, high_price, low_price, "
        "close_price, volume, adj_close_price"
    )
    insert_str = ("%s, " * 11)[:-2]
    final_str = (
        "INSERT INTO daily_price (%s) VALUES (%s)" % (column_str, insert_str)
    )

    # Use MySQL connection to perform insertion
    cur = con.cursor()
    cur.executemany(final_str, daily_data)
    con.commit()

if __name__ == "__main__":
    # Ignore warnings regarding Data Truncation from AlphaVantage precision to Decimal(19, 4)
    warnings.filterwarnings('ignore')

    # Insert daily historical data into our DB
    tickers = get_list_of_db_tickers()[:TICKER_COUNT]

    for i, t in enumerate(tickers):
        print("Adding data for %s: %s out of %s" % (t[1], i+1, len(tickers)))
        av_data = get_daily_historic_data_alphavantage(t[1])
        insert_daily_data_into_db('1', t[0], av_data)
        time.sleep(WAIT_TIME_SECS)

    print("Successfully added AlphaVantage pricing data to DB.")