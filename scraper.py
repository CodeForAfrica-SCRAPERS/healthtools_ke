from healthtools_ke.config import SITES, CLOUDSEARCH_COS_ENDPOINT, CLOUDSEARCH_DOCTORS_ENDPOINT
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re
import json
import sys
import boto3
import random


class Scraper(object):
    def __init__(self):
        self.num_pages_to_scrape = None
        self.site_url = None
        self.fields = None
        self.cloudsearch = None

    def scrape_site(self):
        '''
        Scrape the whole site
        '''
        self.get_total_number_of_pages()
        for page_num in range(1, self.num_pages_to_scrape + 1):
            print "Scraping page %s" % str(page_num)
            entries = self.scrape_page(self.site_url.format(page_num))
            self.upload_data(json.dumps(entries))
            # print "Scraped {} entries from page {}".format(len(entries),
            # page_num)

    def scrape_page(self, page_url):
        '''
        Get entries from page
        '''
        try:
            soup = self.make_soup(page_url)
            table = soup.find('table', {"class": "zebra"}).find("tbody")
            rows = table.find_all("tr")

            entries = []
            _id = 0
            for row in rows:
                # only the columns we want
                # -1 because fields/columns has extra index; id
                columns = row.find_all("td")[:len(self.fields) - 1]
                columns = [text.text.strip() for text in columns]
                columns.append(_id)
                entry = dict(zip(self.fields, columns))
                entry = self.format_for_cloudsearch(entry)
                entries.append(entry)
                _id += 1

            return entries
        except Exception as err:
            print "ERROR: Failed to scrape data from page {}  -- {}".format(page_url, str(err))

    def upload_data(self, payload):
        '''
        Upload data to AWS Cloud Search
        '''
        try:
            response = self.cloudsearch.upload_documents(
                documents=payload, contentType="application/json"
            )
            print "DEBUG - upload_data() - {} - {}".format(len(payload), response.get("status"))
            return response
        except Exception as err:
            print "ERROR - upload_data() - %s - %s" % (len(payload), str(err))

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
        except Exception as err:
            print "ERROR: **get_total_page_numbers()** - url: {} - err: {}".\
                format(self.site_url, str(err))
            return

    def make_soup(self, url):
        '''
        Get page, make and return a BeautifulSoup object
        '''
        response = requests.get(url)  # get first page
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        pass


class DoctorsScraper(Scraper):
    def __init__(self):
        super(DoctorsScraper, self).__init__()
        self.site_url = SITES["DOCTORS"]
        self.fields = [
            "name", "reg_date", "reg_no", "postal_address", "qualifications",
            "speciality", "sub_speciality", "id",
        ]
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **CLOUDSEARCH_DOCTORS_ENDPOINT)

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        date_obj = datetime.strptime(entry['reg_date'], "%Y-%m-%d")
        entry['reg_date'] = datetime.strftime(date_obj, "%Y-%m-%dT%H:%M:%S.000Z")
        entry["facility"] = entry["practice_type"] = "-"
        return {"id": entry["id"], "type": "add", "fields": entry}


class ForeignDoctorsScraper(Scraper):
    def __init__(self):
        super(ForeignDoctorsScraper, self).__init__()
        self.site_url = SITES["FOREIGN_DOCTORS"]
        self.fields = [
            "name", "postal_address", "qualifications", 
            "facility", "practice_type", "id",
        ]
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **CLOUDSEARCH_DOCTORS_ENDPOINT)

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        entry["reg_date"] = "0000-01-01T00:00:00.000Z"
        entry["reg_no"] = entry["speciality"] = entry["sub_speciality"] = "-" 
        return {"id": entry["id"], "type": "add", "fields": entry}
