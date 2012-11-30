"""
data_tracker.Controller is a class for manipulating scraper objects.
The idea is to have a single controller running that can use many 
scraper objects at different time intervals to keep track of various
data.
"""

def Controller:

    class ControlledScraper(scrapers.BaseScraperClass):
        """ ControlledScraper is a class that subclasses the scraper
        class. There are additional attributes that are used by the 
        Controller. These are defined in __init__."""

        def __init__(self, scraper, update_frequency=1, update_start=0, 
                     track_for=0):

            for key in dir(scraper):
                self.__setattribute__(scraper.key)

            self.update_frequency = update_frequency
            self.update_start = update_start
            self.track_for = track_for 

            self.init_time = time.time()
            self.last_update = None

            if self.update_start == 0:
                self.fetch_data()
                self.last_update = time.time()
            
    def __init__(self):

        self.current_scrapers = []
        
    def add_scraper(self, scraper, update_frequency=1, update_start=0, 
                    track_for=0):
        """
        Controller.add_scraper adds one of many scraper objects
        found in data_tracker.scrapers to the controller object.

        The Controller object will then update the data that 
        each scraper in it's queue at the frequency that the scraper
        would like to update.

        Input:
    
        scraper - scraper instance
        update_frequency [ 1 ] - Frequency of update in units of inverse days.
        track_for [ 0 ] - How long to use this scraper in units of days
            Zero means do not stop.
        update_start [ 0 ] - When to start the update in units of days
            from now.
        
        Output:
        
        No output.
        """
        controlled_scraper = Controller.ControlledScraper(
                                scraper, update_frequency=update_frequency,
                                update_start=update_start, track_for=track_for)

        self.current_scrapers.append( controlled_scraper )

    
