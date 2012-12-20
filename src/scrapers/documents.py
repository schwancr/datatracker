"""
DocumentScraper can scrape entire documents (.txt, .pdf, etc.) 
using FTP. In order for this to work, you must be able to access
the FTP server that stores the data.
"""

from datatracker.scrapers import ScraperBaseClass, URLBaseClass
from datatracker import DEFAULT_STORAGE_LOCATION
import os

class DocumentScraper(URLBaseClass):

    def __init__(self, url, username=None, password=None, 
                 storage_location=DEFAULT_STORAGE_LOCATION):
        """
        DocumentScraper can fetch entire documents (.txt, .pdf, etc.) 
        using FTP. In order for this to work, you must be able to access
        the FTP server that stores the data.
    
        Inputs:
        -------
        username : str
            username for the FTP service
        password : str
            password for the FTP service
        url : str
            FTP url location
        storage_location [ %s ] : str
            location (on the web server) to store the documents.
            If None, then the document will NOT be saved. This is
            useful if you are going to parse the document and save
            pieces of data. 

        Outputs:
        scraper : data_tracker.scrapers.DocumentScraper instance
        """

        super(DocumentScraper, self).__init__(url, username, password)
        
        self.storage_location = storage_location
        if self.storage_location is None:
            self.store_file = False

        else:
            if not os.path.exists(self.storage_location):
                print "Creating directory %s" % self.storage_location
                os.makedirs(self.storage_location)

            self.store_file = True

        
    def fetch_data(self, return_text=True):
        
        filename = super(DocumentScraper, self).fetch_data()
        print filename, os.path.exists(filename)

        if self.store_file:
            new_filename = os.path.join(self.storage_location, 
                                        os.path.basename(filename))
            os.rename(filename, new_filename)
            filename = new_filename

        if return_text:
            with open(filename, 'r') as file_obj:
                fetched_text = file_obj.read()

            return fetched_text


