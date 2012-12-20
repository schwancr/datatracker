
import argparse
import MySQLdb
from datatracker import utils

def main(forms=None, ciks=None, tickers=None, 
         date_range=None, user='tracker', host='localhost',
         db='datatracker', table='sec_index'):
    """
Update the indices stored on SEC's FTP 
server. These indices are easily translated into a MySQL 
table with these columns:

1. Company Name - string with the name of the company
2. CIK - ID that the SEC uses for each cmpany
3. Form - string with the form type
4. Date File - Date when the form was filed
5. File Name - URL to find the text file with that file

We will also add the column, whose default value is NULL,
which is the ticker symbol. In this manner, we can store
the ticker symbol as well, so the SECScraper does not
need to connect to the SEC's website everytime to look up
a ticker symbol. 

All options are OPTIONAL! If you don't pass any options,
then the default database/table will be updated on the
mysql on localhost. This will add ALL lines from all of 
the SEC indices.

Inputs:
-------
forms - list or None
    list of forms to grab from the SEC indices
ciks - list or None
    list of CIK ID's (ints or strings) to grab
tickers - list or None
    list of ticker symbols to grab
date_range - list of size 2 or None
    two dates, representing the range of dates to 
    update in this index. Each date should be a 
    str or int formatted like YYYYMMDD.
user [ tracker ] - str
    username to access mysql
host [ localhost ] - str
    hostname to access via mysql
db [ datatracker ] - str
    database to access in mysql. Will create if it does
    not exist
table [ sec_index ] - str
    table to create in datatracker if it does not exist
    """

    # first setup the connection to mysql

    db = MySQLdb.connect(host=host, user=user)

    cursor = db.cursor()

    cursor.execute('create database if not exists %s' % db)
    cursor.execute('use %s' % db)
    cursor.execute('create table if not exists %s' % table)

    # need a plan here...   



    db.commit()
    db.close()


if __name__ == '__main__':

    parser = ArgumentParser(description="""
This script will update the indices stored on SEC's FTP 
server. These indices are easily translated into a MySQL 
table with these columns:

1. Company Name - string with the name of the company
2. CIK - ID that the SEC uses for each cmpany
3. Form - string with the form type
4. Date File - Date when the form was filed
5. File Name - URL to find the text file with that file

We will also add the column, whose default value is NULL,
which is the ticker symbol. In this manner, we can store
the ticker symbol as well, so the SECScraper does not
need to connect to the SEC's website everytime to look up
a ticker symbol. 

All options are OPTIONAL! If you don't pass any options,
then the default database/table will be updated on the
mysql on localhost. This will add ALL lines from all of 
the SEC indices.""" )
    parser.add_argument('-f', '--form', nargs='+', help="""
        Only add rows corresponding to these form types""",
        default=None, dest='forms')
    parser.add_argument('-c', '--ciks', nargs='+', help="""
        Only add rows corresponding to these CIK ids.""",
        default=None, dest='ciks')
    parser.add_argument('-t', '--tickers', nargs='+', help="""
        Only add rows corresponding to these tickers.""",
        default=None, dest='tickers')
    parser.add_argument('-d', '--dates', nargs=2, help="""
        Pass two arguments that denote dates to search between.
        Each date must be formatted as YYYYMMDD without any
        delimiters.""", default=None, dest='dates')
    parser.add_argument('-h', '--host', default='localhost',
        help="""Mysql hostname [ localhost ]""", dest='host')
    parser.add_argument('-u', '--user', default='tracker',
        help="""mysql username [ tracker ]""", dest='user')
    parser.add_argument('-d', '--database', default='datatracker',
        help="""Database name to use. You probably should
            leave this as the default.""", dest='db')
    parser.add_argument('--table', default='sec_index', help="""
        table name to use in the mysql database, You probably
        should leave this as the default.""", dest='table')

    args = parser.parse_args()

    main(forms=args.forms, ciks=args.ciks, tickers=args.tickers, 
         date_range=args.dates, user=args.user, host=args.host,
         db=args.db, table=args.table)
