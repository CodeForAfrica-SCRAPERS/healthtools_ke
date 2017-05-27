from bs4 import BeautifulSoup
from cStringIO import StringIO
from datetime import datetime
from elasticsearch import Elasticsearch
from healthtools.config import AWS, ELASTICSEARCH
import requests
import boto3
import re
import json
import hashlib

print "the host na er {} {}".format(ELASTICSEARCH["host"], ELASTICSEARCH["port"])
es = Elasticsearch([
  {'host': ELASTICSEARCH["host"],
  'port': ELASTICSEARCH["port"]}])

class Scraper(object):
    def __init__(self):
        self.num_pages_to_scrape = None
        self.site_url = None
        self.fields = None
        self.cloudsearch = None
        self.s3_key = None
        self.document_id = 0  # id for each entry, to be incremented
        self.delete_file = None  # contains docs to be deleted after scrape
        self.s3_historical_record_key = None  # s3 historical_record key
        self.s3 = boto3.client("s3", **{
            "aws_access_key_id": AWS["aws_access_key_id"],
            "aws_secret_access_key": AWS["aws_secret_access_key"],
            "region_name": AWS["region_name"],
        })

    def scrape_site(self):
        '''
        Scrape the whole site
        '''
        self.get_total_number_of_pages()
        all_results = []
        delete_batch = []
        skipped_pages = 0

        print "[{0}] ".format(re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__))
        print "{{{0}}} - Started Scraper.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for page_num in range(1, self.num_pages_to_scrape + 1):
            url = self.site_url.format(page_num)
            try:
                self.retries = 0
                scraped_page = self.scrape_page(url)
                import pdb; pdb.set_trace()
                if type(scraped_page) != tuple:
                    print "There's something wrong with the site" \
                     "Proceeding to the next scraper."
                    return

                entries = scraped_page[0]
                delete_docs = scraped_page[1]

                all_results.extend(entries)
                delete_batch.extend(delete_docs)

            except Exception as err:
                skipped_pages += 1
                print "ERROR: scrape_site() - source: {} - page: {} - {}".format(url, page_num, err)
                continue
        print "{{{0}}} - Scraper completed. {1} documents retrieved.\
        ".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(all_results))

        if all_results:
            all_results_json = json.dumps(all_results)
            self.index_data(all_results)
            self.archive_data(all_results_json)
            print "{{{0}}} - Completed Scraper.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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
            delete_batch = []
            for row in rows:
                # only the columns we want
                # -1 because fields/columns has extra index; id
                columns = row.find_all("td")[:len(self.fields) - 1]
                columns = [text.text.strip() for text in columns]
                columns.append(self.document_id)

                entry = dict(zip(self.fields, columns))
                entry = self.format_doc(entry)
                entries.append(entry)

                delete_batch.append({"type": "delete", "id": entry["id"]})
                self.document_id += 1
            return entries, delete_batch
        except Exception as err:
            if self.retries >= 5:
                print "ERROR: Failed to scrape data from page {}  -- {}".format(page_url, str(err))
                return err
            else:
                self.retries += 1
                self.scrape_page(page_url)

    def archive_data(self, payload):
        '''
        Upload scraped data to AWS S3
        '''
        try:
            old_etag = self.s3.get_object(
                Bucket="cfa-healthtools-ke", Key=self.s3_key)["ETag"]
            new_etag = hashlib.md5(payload.encode('utf-8')).hexdigest()

            if eval(old_etag) != new_etag:
                file_obj = StringIO(payload.encode('utf-8'))
                self.s3.upload_fileobj(file_obj,
                                       "cfa-healthtools-ke", self.s3_key)

                # archive historical data
                date = datetime.today().strftime('%Y%m%d')
                self.s3.copy_object(Bucket="cfa-healthtools-ke",
                                    CopySource="cfa-healthtools-ke/" + self.s3_key,
                                    Key=self.s3_historical_record_key.format(
                                        date))
                print "{{{0}}} - Archived data has been " \
                "updated.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                return
            else:
                print "{{{0}}} - Data Scraped does not differ from archived" \
                 "data.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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

    def format_doc(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        return entry

    def index_data(self, result):
        es.indices.delete(index=type(self).__name__, ignore=[400, 404])
        for i, record in enumerate(result):
            es.index(index=type(self).__name__, doc_type=type(self).__name__, id=i, body=record)



