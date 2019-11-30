import pandas as pd
import MySQLdb as mdb

import retrieve_prices

if __name__ == '__main__':
    DB_HOST = 'localhost'
    DB_USER = 'sec_user'
    with open('sec_user_pass.txt', 'r') as file:
        DB_PASS = file.readline().rstrip()
    DB_NAME = 'securities_master'
    con = mdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)

    ticker_dict = retrieve_prices.get_dict_of_db_tickers()

    TEST_TICKER = 'GOOG'
    TEST_ID = ticker_dict[TEST_TICKER]

    av_data = retrieve_prices.get_daily_historic_data_alphavantage(TEST_TICKER)
    retrieve_prices.insert_daily_data_into_db('1', TEST_ID, av_data)

    sql = """SELECT dp.price_date, dp.adj_close_price
             FROM symbol AS sym
             INNER JOIN daily_price as dp
             ON dp.symbol_id = sym.id
             WHERE sym.ticker = '%s'
             ORDER BY dp.price_date ASC;
          """ % (TEST_TICKER)

    test = pd.read_sql_query(sql, con=con, index_col='price_date')

    print(test.tail())
