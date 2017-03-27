from bs4 import BeautifulSoup
from cStringIO import StringIO
from datetime import datetime
from healthtools.config import AWS
import requests
import boto3
import re
import json
import hashlib


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

        print "Running {} ".format(type(self).__name__)
        for page_num in range(1, self.num_pages_to_scrape + 1):
            url = self.site_url.format(page_num)
            try:
                print "Scraping page %s" % str(page_num)
                scraped_page = self.scrape_page(url)
                entries = scraped_page[0]
                delete_docs = scraped_page[1]

                all_results.extend(entries)
                delete_batch.extend(delete_docs)
                print "Scraped {} entries from page {} | {}".format(len(entries), page_num, type(self).__name__)
            except Exception as err:
                skipped_pages += 1
                print "ERROR: scrape_site() - source: {} - page: {} - {}".format(url, page_num, err)
                continue
        print "| {} completed. | {} entries retrieved. | {} pages skipped.".format(type(self).__name__, len(all_results), skipped_pages)

        if all_results:
            all_results_json = json.dumps(all_results)
            delete_batch = json.dumps(delete_batch)

            self.delete_cloudsearch_docs()
            self.upload_data(all_results_json)
            self.archive_data(all_results_json)

            # store delete operations for next scrape
            delete_file = StringIO(delete_batch)
            self.s3.upload_fileobj(
                delete_file, "cfa-healthtools-ke",
                self.delete_file)

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
                columns.append(self.generate_id())

                entry = dict(zip(self.fields, columns))
                entry = self.format_for_cloudsearch(entry)
                entries.append(entry)

                delete_batch.append({"type": "delete", "id": entry["id"]})
                self.document_id += 1
            return entries, delete_batch
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
            old_etag = self.s3.get_object(
                Bucket="cfa-healthtools-ke", Key=self.s3_key)["ETag"]
            new_etag = hashlib.md5(payload).hexdigest()

            if eval(old_etag) != new_etag:
                file_obj = StringIO(payload)
                self.s3.upload_fileobj(file_obj,
                                       "cfa-healthtools-ke", self.s3_key)

                # archive historical data
                date = datetime.today().strftime('%Y%m%d')
                self.s3.copy_object(Bucket="cfa-healthtools-ke",
                                    CopySource="cfa-healthtools-ke/" + self.s3_key,
                                    Key=self.s3_historical_record_key.format(
                                        date)
                                    )
                print "DEBUG - archive_data() - {}".format(self.s3_key)
                return
            else:
                print "DEBUG - archive_data() - no change in archive"
        except Exception as err:
            print "ERROR - archive_data() - {} - {}".format(self.s3_key, str(err))

    def delete_cloudsearch_docs(self):
        '''
        Delete documents that were uploaded to cloudsearch in the last scrape
        '''
        try:
            # get documents to be deleted
            delete_docs = self.s3.get_object(
                Bucket="cfa-healthtools-ke",
                Key=self.delete_file)['Body'].read()

            # delete
            response = self.cloudsearch.upload_documents(
                documents=delete_docs, contentType="application/json"
            )
            print "DEBUG - delete_cloudsearch_docs() - {} - {}".format(type(self).__name__, response.get("status"))
            return response
        except Exception as err:
            if "NoSuchKey" in err:
                print "ERROR - delete_cloudsearch_docs() - no delete file present"
                return
            print "ERROR - delete_cloudsearch_docs() - {} - {}".format(type(self).__name__, str(err))

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

    def generate_id(self):
        '''
        Generate an id for an entry
        '''
        pass
