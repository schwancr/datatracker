"""
data_tracker.scrapers contains classes that can scrape url's 
in certain ways. For instance, the GoogleFinance scraper can
fetch data for a given stock.
"""

from datatracker import utils
import numpy as np
import urllib
import warnings
import os
import MySQLdb

class ScraperBaseClass(object):

    def __init__(self):
        return

    def fetch_data(self):
        """Each subclass must re-define how to fetch data."""
        self.save_data()
        return

    def save_data(self):
        """Each scraper object must be able to save the data
        fetched into a mysql DB."""
        return

