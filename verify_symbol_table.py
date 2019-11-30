import MySQLdb as mdb

key_file = open('sec_user_pass.txt', 'r')
DB_PASSWORD = key_file.readline().rstrip()
key_file.close()

def display_securities_master():
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
    query = "SELECT * FROM symbol"
    cur = con.cursor()
    cur.execute(query)
    res = cur.fetchall()

    for r in res:
        print(r)

if __name__ == '__main__':
    display_securities_master()