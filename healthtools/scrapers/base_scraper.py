from bs4 import BeautifulSoup
from cStringIO import StringIO
import requests
import re
import json


class Scraper(object):
    def __init__(self):
        self.num_pages_to_scrape = None
        self.site_url = None
        self.fields = None
        self.cloudsearch = None
        self.s3 = None
        self.s3_key = None
        self.document_id = 0  # id for each entry, to be incremented

    def scrape_site(self):
        '''
        Scrape the whole site
        '''
        self.get_total_number_of_pages()
        all_results = []
        skipped_pages = 0

        print "Running {} ".format(type(self).__name__)
        for page_num in range(1, self.num_pages_to_scrape + 1):
            url = self.site_url.format(page_num)
            try:
                print "Scraping page %s" % str(page_num)
                entries = self.scrape_page(url)
                all_results.extend(entries)
                print "Scraped {} entries from page {}".format(len(entries), page_num)
            except Exception as err:
                skipped_pages += 1
                print "ERROR: scrape_site() - source: {} - page: {} - {}".format(url, page_num, err)
                continue
        print "|{} completed. | {} entries retrieved. | {} pages skipped.".format(type(self).__name__,len(all_results), skipped_pages)

        all_results_json = json.dumps(all_results)
        self.upload_data(all_results_json)
        self.archive_data(all_results_json)

        return all_results

    def scrape_page(self, page_url):
        '''
        Get entries from page
        '''
        try:
            soup = self.make_soup(page_url)
            table = soup.find('table', {"class": "zebra"}).find("tbody")
            rows = table.find_all("tr")

            entries = []
            for row in rows:
                # only the columns we want
                # -1 because fields/columns has extra index; id
                columns = row.find_all("td")[:len(self.fields) - 1]
                columns = [text.text.strip() for text in columns]
                columns.append(self.document_id)
                entry = dict(zip(self.fields, columns))
                entry = self.format_for_cloudsearch(entry)
                entries.append(entry)
                self.document_id += 1
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
            print "DEBUG - upload_data() - {} - {}".format(type(self).__name__, response.get("status"))
            return response
        except Exception as err:
            print "ERROR - upload_data() - {} - {}".format(type(self).__name__, str(err))

    def archive_data(self, payload):
        '''
        Upload scraped data to AWS S3
        '''
        try:
            file_obj = StringIO(payload)
            response = self.s3.upload_fileobj(file_obj, "cfa-healthtools-ke", self.s3_key)
            print "DEBUG - archive_data() - {}".format(self.s3_key)
        except Exception as err:
            print "ERROR - archive_data() - {} - {}".format(self.s3_key, str(err))

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
        return {"id": entry["id"], "type": "add", "fields": entry}
