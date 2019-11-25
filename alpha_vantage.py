from datetime import datetime as dt
import json
import pandas as pd
import requests

ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co'
ALPH_VANTAGE_TIME_SERIES_CALL = 'query?function=TIME_SERIES_DAILY_ADJUSTED'
columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
key_file = open('api_key.txt', 'r')
API_KEY = key_file.readline().rstrip()
key_file.close()

class AlphaVantage(object):
    """
    Encapsulates calls to the AlphaVantage API with a
    provided API key.

    """
    def __init__(self, api_key = API_KEY):
        """
        Initialize the AlphaVantage instance.

        Args:
        api_key : 'str', optional
            The API key for the associated AlphaVantage Account
        """
        self.api_key = api_key

    def _construct_alpha_vantage_symbol_call(self, ticker):
        """
        Construct the full API call to AlphaVantage based on the user
        provided API key and the desired ticker symbol.

        Args:
        ticker : 'str'
            The ticker symbol, e.g. 'GOOG'

        Returns:
        'str'
            The full API call for a ticker time series
        """
        return '%s/%s&symbol=%s&outputsize=full&apikey=%s' % (
            ALPHA_VANTAGE_BASE_URL, 
            ALPH_VANTAGE_TIME_SERIES_CALL,
            ticker, 
            self.api_key)

    def get_daily_historic_data(self, ticker, start_date, end_date):
        """
        Use the generated API call to query AlphaVantage with the
        appropriate API key and return a list of price tuples
        for a particular ticker.
        
        Args:
        ticker : 'str'
            The ticker symbol, e.g. 'GOOG'
        start_date : 'datetime'
            The starting date from which to obtain pricing data
        end_date: 'datetime'
            The ending data from which to obtain pricing data

        Returns:
        'pd.DataFrame'
            The frame of OHLCV prices and volumes.
        """
        av_url = self._construct_alpha_vantage_symbol_call(ticker)

        try:
            av_data_js = requests.get(av_url)
            data = json.loads(av_data_js.text)['Time Series (Daily)']
        except Exception as e:
            print(
                "Could not download AlphaVantage data for %s ticker"
                "(%s)...stopping." % (ticker, e)
            )
            return pd.DataFrame(columns=COLUMNS).set_index('Date')
        else:
            prices = []
            for date_str in sorted(data.keys()):
                date = strptime(date_str, '%Y-%m-%d')
                if date < start_date or date > end_date:
                    continue

                bar = data[date_str]
                prices.append(
                    (
                        date,
                        float(bar['1. open']),
                        float(bar['2. high']),
                        float(bar['3. low']),
                        float(bar['4. close']),
                        int(bar['6. volume']),
                        float(bar['5. adjusted close'])
                    )
                )
            return pd.DataFrame(prices, columns=COLUMNS).set_index('Date')