"""
DocumentScraper can scrape entire documents (.txt, .pdf, etc.) 
using FTP. In order for this to work, you must be able to access
the FTP server that stores the data.
"""

import urllib
import warnings
import os
import MySQLdb
from datatracker.scrapers import ScraperBaseClass
from datatracker import utils
from datatracker import DEFAULT_STORAGE_LOCATION,
                        DB_NAME

class DocumentScraper(ScraperBaseClass):

    def __init__(self, url, username=None, password=None, 
                 storage_location=DEFAULT_STORAGE_LOCATION,
                 db_name=DB_NAME, db_user='tracker',
                 db_host='localhost', db_table='docs'):
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

        self.url = url
        self.username = username
        self.password = password

        self.db_name = db_name
        self.db_user = db_user
        self.db_host = db_host
        self.db_table = db_table

        # Make sure we can connect to the given url
        self.test_connection()
        # Setup the MySQL database and table
        self.setup_database()

        self.storage_location = storage_location
        if self.storage_location is None:
            self.store_file = False

        else:
            if not os.path.exists(self.storage_location):
                print "Creating directory %s" % self.storage_location
                os.makedirs(self.storage_location)

            self.store_file = True

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
        cursor.execute('create table if not exists %s' % self.db_table +
                       '(url text, file text, url_type varchar(255), ' +
                        ' hostname varchar(255), time_fetched datetime)')
        # Since this is a very basic class, we will hard-code the
        # columns, but for future classes, this should be defined 
        # via several kwargs.

        db.commit()
        db.close()

    def test_connection(self):
        """
        Test the connection to the server at the given url.
        """
        # Ideally this function would check that we can connect
        # via the internet as well as check for HTTP errors, like
        # 404 Not Found type messages that are clearly not good.
        warnings.warn('Not Implemented.')

    def fetch_data(self, return_text=True):
        """
        Fetch data according to this scraper's rules (i.e.
        from the url passed in the initialization).

        Inputs:
        -------
        return_text [ True ] : bool
            The data of this scraper is a file, which is saved
            locally, if return_text is True, then the file will
            be read as a string and returned. 

        Outputs:
        --------
        file_text : str
            If return_text is True, then the file will be read into
            memory and returned as a string. Otherwise None will
            be returned.
        """

        filename, headers = urllib.urlretrieve(self.url)

        if self.store_file:
            new_filename = os.path.join(self.storage_location, 
                                        os.path.basename(filename))
            os.rename(filename, new_filename)
            filename = new_filename

            self.save_data(filename)

        else: # We are not saving the file, so we should not log
              # it to the mysql DB. Note that this scraper then 
              # does not do anything other than return test, but
              # this could be all it's needed for.
            warnings.warn('Not saving file. It will be left in %s' % filename)
            pass
            
        if return_text:
            with open(filename, 'r') as file_obj:
                fetched_text = file_obj.read()

            return fetched_text

        return None

    def save_data(self, filename):
        """
        Save the data fetched into the mysql database.
            
        Inputs:
        -------
        filename : str
            filename pointing to location of the retrieved
            url. This string will be entered in the database
        """

        db = MySQLdb.connect(db=self.db_name, host=self.db_host,
                             user=self.db_user)

        url_type, no_type = urllib.splittype(self.url)

        hostname = urllib.splithost(no_type)[0]

        cursor = db.cursor()
        cmd = 'insert into %s (url, file, url_type, hostname, time_fetched) ' % \
              self.db_table + 'values ("%s", "%s", "%s", "%s", now())' % \
              (self.url, filename, url_type, hostname)
        cursor.execute(cmd)
        # This currently does not check for errors in the sql
        # command. this could be improved later, but for now
        # we will just assume it's working correctly.

        db.commit()
        db.close()

