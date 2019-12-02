# This module contains functions that will scrape wikipedia for
# information on the companies that currently constitute the S&P 500
# and add these stocks into the securities_master MySQL database.
# If the script is run, the main method will call both of these functions
# and modify the securities_master database.

import bs4
import datetime
import MySQLdb as mdb
import requests

from math import ceil


key_file = open('sec_user_pass.txt', 'r')
DB_PASSWORD = key_file.readline().rstrip()
key_file.close()

def obtain_parse_wiki_snp500():
    """
    Downloads and parses the Wikipedia list of S&P500 companies.
    
    Returns
        a list of tuples to add to securities_master database
    """
    now = datetime.datetime.utcnow()

    snp500_wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(snp500_wiki_url)
    soup = bs4.BeautifulSoup(response.text, features="html.parser")

    # Uses CSS Selector syntax to get first table
    # and second row (ignoring header row 0)
    symbols_list = soup.select('table')[0].select('tr')[1:]

    # Grabs symbol information by scraping each row, on the Wikipedia
    # page for the S&P 500 company list. Ordering matches the columns
    # in the securities master database.
    symbols = []
    for symbol in symbols_list:
        # grabs a row from the table of S&P 500 companies
        tds = symbol.select('td')
        symbols.append(
            (
                tds[0].select('a')[0].text, # ticker
                'stock', # instrument
                tds[1].select('a')[0].text, # name
                tds[3].text, # sector
                'USD', # currency
                now, # created_date
                now # last_updated_date
            )
        )
    return symbols

def insert_snp500_symbols(symbols):
    """
    Inserts the S&P 500 symbols into the securities_master database.
    """

    db_host = 'localhost'
    db_user = 'sec_user'
    db_pass = DB_PASSWORD
    db_name = 'securities_master'
    con = mdb.connect(
        host = db_host,
        user = db_user,
        passwd = db_pass,
        db = db_name
    )

    column_str = (
        "ticker, instrument, name, sector, currency, created_date, "
        "last_updated_date"
    )
    insert_str = ("%s, " * 7)[:-2]
    final_str = "INSERT INTO symbol (%s) VALUES (%s)" % (column_str, insert_str)
    
    cur = con.cursor()
    cur.executemany(final_str, symbols)
    con.commit()

if __name__ == "__main__":
    symbols = obtain_parse_wiki_snp500()
    insert_snp500_symbols(symbols)
    print("%s symbols were successfully added." % len(symbols))