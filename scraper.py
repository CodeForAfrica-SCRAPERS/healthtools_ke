from config import SITES, CLOUDSEARCH_COS_ENDPOINT, CLOUDSEARCH_DOCTORS_ENDPOINT
import requests
from bs4 import BeautifulSoup
import re


class Scraper(object):
    def __init__(self):
        self.num_pages_to_scrape = None
        self.site_url = None
        self.fields = None

    def scrape_site():
        '''
        Scrape the whole site
        '''

    def scrape_page(self, page_url):
        '''
        Get data from page
        '''
        try:
            soup = self.make_soup(page_url)
            table = soup.find('table', {"class": "zebra"}).find("tbody")
            rows = table.find_all("tr")

            entries = []
            for row in rows:
                # only the columns we want
                columns = row.find_all("td")[:len(self.fields) - 1]  # -1 because fields has extra index; id
                columns = [text.text.strip() for text in columns]
                columns.append(self.generate_id(columns))
                entries.append(dict(zip(self.fields, columns)))

            return entries
        except Exception, err:
            print "ERROR: Failed to scrape data from page {}  -- {}".format(page, err)

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
            soup = self.make_soup(self.site_url.format(1))  # get first page
            text = soup.find("div", {"id": "tnt_pagination"}).getText()
            # what number of pages looks like
            pattern = re.compile("(\d+) pages?")
            self.num_pages_to_scrape = int(pattern.search(text).group(1))
        except Exception, err:
            print "ERROR: **get_total_page_numbers()** - url: {} - err: {}".\
                format(self.site_url, err)
            return

    def make_soup(self, url):
        '''
        Get page, make and return a BeautifulSoup object
        '''
        response = requests.get(url)  # get first page
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def generate_id(self, field):
        '''
        Generate id using field values in data
        '''
        pass


class DoctorsScraper(Scraper):
    def __init__(self):
        super(DoctorsScraper, self).__init__()
        self.site_url = SITES["DOCTORS"]
        self.fields = [
            "name", "regdate", "regno", "postaladdress", "qualifications",
             "speciality", "sub_speciality", "id",
        ]

    def generate_id(self, field):
        '''
        Generate id using registration number
        '''
        _id = field[2].strip().replace(" ", "")
        return _id
