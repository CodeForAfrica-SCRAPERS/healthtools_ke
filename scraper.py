from config import SITES, CLOUDSEARCH_COS_ENDPOINT, CLOUDSEARCH_DOCTORS_ENDPOINT
import requests
from bs4 import BeautifulSoup
import re


class Scraper(object):
    def __init__(self):
        self.num_pages_to_scrape = None
        self.site_url = None

    def scrape_site():
        '''
        Scrape the whole site
        '''
    def scrape_page():
        '''
        Get data from page
        '''
    def upload_data():
        '''
        Upload data to AWS Cloud Search
        '''

    def archive_data():
        '''
        Upload data to AWS S3 if changed
        '''

    def get_total_number_of_pages(self):
        '''
        Get the total number of pages to be scraped
        '''
        try:
            response = requests.get(self.site_url.format(1))  # get first page
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.find("div", {"id": "tnt_pagination"}).getText()
            pattern = re.compile("(\d+) pages?")  # what number of pages looks like
            self.num_pages_to_scrape = int(pattern.search(text).group(1))
        except Exception, err:
            print "ERROR: **get_total_page_numbers()** - url: {} - err: {}" .format(self.site_url, err)
            return


class DoctorsScraper(Scraper):
    def __init__(self):
        super(DoctorsScraper, self).__init__()
        self.site_url = SITES["DOCTORS"]
