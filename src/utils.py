"""
This file contains various helper (utility) functions
for datatracker.
"""

import urllib

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
