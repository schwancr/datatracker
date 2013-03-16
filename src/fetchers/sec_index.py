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


class SECFileScraper(DocumentScraper):

    def __init__(self, ticker_symbol, form, 
                 storage_location=DEFAULT_STORAGE_LOCATION,
                 db_name=DB_NAME, db_user='tracker',
                 db_host='localhost', db_table='sec_docs'):
        """
        Initialize the SECScraper instance. This works slightly
        differently than the other scrapers because it must
        update the URL every time it tries to update the data.
        This means that SECScraper.fetch_data() fetches the 
        'next' piece of data. 

        Because of this, there is a convenience function that
        fetches all valid documents: SECScraper.fetch_all(). 
        Then the fetch_data() function will only fetch the 
        most recent form (if it hasn't already been fetched.

        This would be a typical usage:

        > scraper = SECScraper('AAPL', '10-Q')
        > scraper.fetch_all()  # This will fetch all forms and
            # download them to the default location, as well
            # as update the MySQL database.
        ...
        # Now every quarter, you can do:
        > scraper = SECScraper('AAPL', '10-Q')
        > scraper.fetch_data()  # This will only fetch the form
            # that is next in the stack. Note you could fall
            # behind if you don't update frequently enough.

        Inputs:
        -------
        ticker_symbol : str
            ticker symbol for the desired company. NOTE: If
            this is not found by the SEC, you will have to
            look up the CIK ID manually. But you can input 
            that as the ticker symbol here.
        form : str
            any form that the SEC will have. E.g. 10-Q, 10-K
        storage_location : str
            directory to place files
        oldest_date [ None ] : str
            oldest date to grab the forms. This should be input
            as the SEC formats the dates: YYYYMMDD, with no
            delimiters. If None, the scraper will grab all
            available forms

        Outputs:
        scraper : SECScraper instance
            returns the scraper instance that can be used to
            fetch the data
        """

        # If we can't find the cik number then we cannot proceed
        try:
            self.cik = utils.get_cik_from_ticker(ticker_symbol)
        except:
            raise Exception('Cannot find ticker symbol, please use a CIK instead.')
            
        self.ticker_symbol = ticker_symbol

        self.db_name = db_name
        self.db_user = db_user
        self.db_host = db_host
        self.db_table = db_table

        self.form = form
        self.oldest_date = oldest_date        

        self.setup_database()

    def setup_database(self):
        """
        Setup the mysql database for adding names.
        """

        try:
            db = MySQLdb.connect(host=self.db_host, user=self.db_user)
        except:
            raise Exception('Cannot connect to MySQL on %s with user %s' %
                            (self.db_host, self.db_user))

        cursor = db.cursor()

        cursor.execute('create database if not exists %s' % self.db_name)
        cursor.execute('use %s' % self.db_name)
        # Columns:
        # ticker symbol, CIK, form, date filed, date fetched, file, url
        cursor.execute('create table if not exists %s' % self.db_table +
                       '(ticker varchar(10), CIK int, form varchar(10), ' +
                       'file_date date, url text, file text, time_fetched datetime)')

        db.commit()
        db.close()

    def update_url(self):
        """
        The SECScraper is essentially the DocumentScraper with a 
        changing URL, that changes chronolocally to the next form
        available.
        """
        

    def fetch_data(self, return_text=False):
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
        
