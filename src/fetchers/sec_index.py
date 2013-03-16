"""
This class of scraper will download forms from the SEC (Securities
Exchange Commission). You can download any form, but parsing the
forms will be your job.
"""

from datatracker.scrapers import DocumentScraper
from datatracker import utils
from datatracker import DEFAULT_STORAGE_LOCATION,
                        DB_NAME

import MySQLdb
import zlib


class SECIndexScraper(DocumentScraper):

    def __init__(self, forms=None, tickers=None, ciks=None, 
                 date_range=None, db_name=DB_NAME, db_user='tracker',
                 db_host='localhost', db_table='sec_index'):
    """
    Update the indices stored on SEC's FTP 
    server. These indices are easily translated into a MySQL 
    table with these columns:

    1. Company Name - string with the name of the company
    2. CIK - ID that the SEC uses for each cmpany
    3. Form - string with the form type
    4. Date File - Date when the form was filed
    5. File Name - URL to find the text file with that file
    6. Ticker - Ticker symbol used by the stock exchange

    We will also add the column, whose default value is NULL,
    which is the ticker symbol. In this manner, we can store
    the ticker symbol as well, so the SECScraper does not
    need to connect to the SEC's website everytime to look up
    a ticker symbol. 

    All options are OPTIONAL! If you don't pass any options,
    then the default database/table will be updated on the
    mysql on localhost. This will add ALL lines from all of 
    the SEC indices.

    Usage:

        > fetcher = SECIndexFetcher(forms=['10-K'])
        > fetcher.fetch_all()  # This will fetch all 10-K's 
            # locations and save the urls to the MySQLdb. 
            # To actually download them you can use an
            # SECFileFetcher instance
        ...
        # Now every quarter, you can do:
        > scraper = SECScraper('AAPL', '10-Q')
        > scraper.fetch_data()  # This will only fetch forms
            # that are in the most recent index file
            # unless that file has already been read

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
    db [ datatracker ] - str
        database to access in mysql. Will create if it does
        not exist
    table [ sec_index ] - str
        table to create in datatracker if it does not exist

    """

        self.db_name = db_name
        self.db_user = db_user
        self.db_host = db_host
        self.db_table = db_table
        self.setup_database()

        self.forms = forms
        self.ciks = ciks
        self.tickers = tickers
        self.date_range = date_range
        # There are really two index files we could potentially use
        # one is ordered by form type, the other by cik number, so
        # if we only want a particular form but all companies, then
        # it's faster to use the form_re (I think) and vice versa
        form_re = re.compile(r'(?P<form>[\d\w\-/]+)\s+' 
                             r'(?P<name>[&\w\s/]+?)\s+'
                             r'(?P<cik>\d+)\s+'
                             r'(?P<date>[\d\-]+)\s+'
                             r'(?P<url>edgar/[\w/.\-\d]+)\s+')

        cik_re = re.compile(r'(?P<cik>\d+)|'
                            r'(?P<name>[&\w\s/]+)|'
                            r'(?P<form>[\d\w\-/]+)|'
                            r'(?P<date>[\d\-]+)|'
                            r'(?P<url>edgar/[\w.\=\d]+)')

        self.regex = form_re # default to using the forms file

        if forms is None:
            self.check_forms = False
        else:
            self.check_forms = True
            self.forms = forms

        if (ciks is None) and (tickers is None):
            self.check_ciks = False
        else:
            self.check_ciks = True
            self.ciks = []

        if not (self.check_ciks or self.check_forms):
            warnings.warn("Did not provide at least one ticker, cik, or form."
                          "This means we will save ALL data from the SEC index.")
    
        if not ciks is None:
            self.ciks.extend(list(np.unique(ciks)))

        if not tickers is None:
            # If tickers are also added, then we will add these to the
            # cik list. 

            # NOTE: Some weird user might want to use ciks logical_and 
            # tickers, in which case we would want the set intersection
            # of ciks and tickers, but this is weird. I think the better
            # functionality is to use all IDs
            self.tickers.extend(list(np.unique([utils.get_cik_from_ticker(t)
                for t in tickers])))

        if self.forms is None or len(self.forms) < len(self.ciks):
            # Use the cik form because we 
            #self.regex = cik_regex
            # Note that currently only the form index is implemented

        # This is a little hairy but it works...
        # We want to grab the year and then the fiscal quarter, so:
        # ( month - 1 ) / 3 + 1 gives the truncated 
        month_to_qtr = { 1 : 1, 
                         2 : 1,
                         3 : 1,
                         4 : 2,
                         5 : 2,
                         6 : 2,
                         7 : 3,
                         8 : 3,
                         9 : 3,
                        10 : 4,
                        11 : 4,
                        12 : 4 }
        if date_range is None:
            date_range = []
            date_range.append((1993,1))
            date_range.append((int(time.strftime('%Y')),
                               month_to_qtr[int(time.strftime('%m'))])
                               #(int(time.strftime('%m')) - 1) / 3 + 1))
        else:
            date_range = [(int(d[:4]), month_to_qtr[int(d[4:6])])
                          for d in date_range]
                         # (int(d[4:6]) - 1) / 3 + 1) 

        ((min_year, min_qtr), (max_year, max_qtr)) = date_range

        # You thought THAT was hacky?! Wait til you see this:
        dates_as_floats = np.arange((min_year + (min_qtr - 1) / 4.) * 4., 
                                    (max_year + max_qtr / 4.) * 4. ) / 4.
        # e.g. (1993, 1) -> 1993.0 
        # e.g. (1996, 3) -> 1993.75 

        years = dates_as_floats.astype(int)
        # get the years back
        qtrs = ((dates_as_floats - years) * 4 + 1).astype(int)
        # the quarters are just the truncation error
        # e.g. 1998.5 -> (1998, 3)

        self.year_qtr_tuples = zip(years, qtrs)

        # Now I have the setup 'cleaned up' so I can move to downloading.
        # Questions:
        # 1) How should this fetcher manage the date_range for the fetch_data
        #    and fetch_all methods? It seems like I might want to track which
        #    indices I have looked at... But that is tricky because many of
        #    these instances could be running at a time, even though that isn't
        #    optimal
        # 2) Should I save the index to disk after reading it?
        # 3) Is date range really necessary?
        # 4) Is there a less hacky way of doing these things? Especially the year
        #    thing...


    def setup_database(self):
        """
        Setup the mysql database for adding names.
        """

        try:
            db_conn = MySQLdb.connect(host=host, user=user)
        except:
            raise Exception('Cannot connect to MySQL on %s with user %s' %
                            (self.db_host, self.db_user))
        cursor = db_conn.cursor()

        print 'create database if not exists %s' % self.db_name
        cursor.execute('create database if not exists %s' % self.db_name)
        cursor.execute('use %s' % self.db_name)
        cursor.execute('create table if not exists %s' % self.db_table +
                       '( cik int, form varchar(10), name varchar(255), '
                       ' url text, date_filed date, format varchar(10), '
                       'ticker varchar(10) )')

        db_conn.commit()
        db_conn.close()


    def update_url(self):
        """
        The SECIndexFetcher is essentially the DocumentFetcher with a 
        changing URL, that changes chronolocally to the next form
        available.
        """
        

    def fetch_data(self):
        """
        Wrap the DocumentScraper.fetch_data, because we have to update 
        the URL before fetching data...
        """
        self.update_url()
        fetched_text = super(SECScraper, self).fetch_data(self, return_text)

        return fetched_text
        
    def save_data(self, filename):
        """
        Update the mysql database that stores each filename location.
        """

        db = MySQLdb.connect(host=self.db_host, user=self.db_user, 
                             db=self.db_name)

        cursor = db.cursor()

        cursor.execute('insert into %s set ' % self.db_table
                       'ticker = "%s" ' % self.ticker_symbol
                       'CIK = %d ' % self.cik
                       'form = "%s" ' % self.form
                       'file_date = %s ' % self.last_filed_date
                       'url = "%s" ' % self.url
                       'file = "%s" ' % filename
                       'time_fetched = now()')

        db.commit()
        db.close()
        
