"""
This file contains various helper (utility) functions
for datatracker.
"""

import urllib
import zlib
import re
import IPython
import ftplib

TEMP_STRING = ''
def store_string(x):
    global TEMP_STRING
    TEMP_STRING += x

def get_cik_from_ticker(ticker_symbol):
    """
    Search www.sec.gov by the given ticker symbol and
    get the CIK number so that we can find forms easier.
    
    Inputs:
    -------
    ticker_symbol : str
        ticker symbol (case insensitive)

    Outputs:
    cik_id : int
        the cik number, if the ticker was found, 
        otherwise, None.
    """

    result = urllib.urlopen('http://www.sec.gov/cgi-bin/browse-edgar?company=&' +
                            'match=&CIK=%s&filenum=&State=&Country=&' % ticker_symbol +
                            'SIC=&owner=exclude&Find=Find+Companies&action=getcompany')
    
    for line in result.fp:
        match_obj = re.search('cik=(\d+)', line, re.IGNORECASE)
        if match_obj:  
            cik_id = int(match_obj.group(1))
            break

    return cik_id
    
def format_sql_string(raw_string):
    
    special_characters = [':', ';' ]

    for spec_char in special_characters:
        raw_string = raw_string.replace(spec_char, r'\%s' % spec_char)

    return raw_string

def get_sec_index_file(year, quarter, index_type='form',
                       compression=None):
    """
    Get the index file for a given year and quarter. If
    it does not exist then return an empty string.

    Inputs:
    -------
    year : int
        Year to find data for
    quarter : one of: [1, 2, 3, 4]
        Quarter to grab.
    index_type : str
        one of ['form', 'company', 'cik']. The difference
        is just how the file is sorted, so if you are 
        looking for a particular form, then use form, if
        you are looking for a particular CIK id, then use
        cik, etc.
    compression : str
        one of ['z', 'gz', 'zip', 'sit'] where the strings
        correspond to the extension you want to download.
        If compression is None, then the flat text is used. 

    Outputs:
    --------
    open_url_obj : urllib.addinfourl instance
        Use open_url_obj.fp to read the page from the index
        > url_text = open_url_obj.fp.read()
    """
    global TEMP_STRING
    TEMP_STRING = ''

    translate_index_type = { 'form' : 'form',
                             'company' : 'company',
                             'cik' : 'master' }

    index_type = index_type.lower()

    if not index_type in translate_index_type.keys():
        raise Exception('Unknown index_type %s' % index_type)   

    filename = translate_index_type[index_type]
    
    ext = compression

    if ext is None:
        ext = 'idx'

    if ext == 'z':
        ext = 'Z'

    if not ext in ['Z', 'gz', 'zip', 'sit', 'idx']:
        raise Exception('Unknown compression type %s' % compression)

    url = ('ftp://sec.gov/edgar/full-index/%d/QTR%d/%s.%s' %
           (year, quarter, filename, ext))
    ftp_url = ('edgar/full-index/%d/QTR%d/%s.%s' %
           (year, quarter, filename, ext))
    
    print url
    ftp = ftplib.FTP(host='sec.gov', user='anonymous', passwd='schwancr@gmail.com')
    out = ftp.retrbinary('RETR ' + ftp_url, store_string)

    ftp.close()
    #open_url_obj = urllib.urlopen(url)
    text = zlib.decompress(TEMP_STRING, 15 + 32)

#    open_url_obj.close()
 #   del open_url_obj

    return text
