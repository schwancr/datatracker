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


class SECScraper(DocumentScraper):

    def __init__(self, ticker_symbol, form, 
                 storage_location=DEFAULT_STORAGE_LOCATION):
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

        # First create a table in the MySQL database if it
        # does not exist yet.    

        
                 

    
