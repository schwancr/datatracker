"""
data_tracker.scrapers contains classes that can scrape url's 
in certain ways. For instance, the GoogleFinance scraper can
fetch data for a given stock.
"""

import numpy as np
import urllib
import warnings
import os

class ScraperBaseClass(object):

    def __init__(self):
        
        return

    def fetch_data(self):
        """Each subclass must re-define how to fetch data."""
        return

class URLBaseClass(ScraperBaseClass):

    def __init__(self, url, username=None, password=None):
        """
        URLBaseClass uses urllib to access a server and fetch data.
        """
        self.url = url
        self.username = username
        self.password = password

        # Make sure we can connect to the given url
        self.test_connection()

    def test_connection(self):
        """
        Test the connection to the FTP server at the given url.
        """
        
        warnings.warn('Not Implemented.')
        
    def fetch_data(self):
        """
        Retrieve data from the specified url.
        """
        
        filename, headers = urllib.urlretrieve(self.url)

        print filename, os.path.exists(filename)
        return filename

        
        
