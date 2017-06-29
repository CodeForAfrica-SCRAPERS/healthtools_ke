from bs4 import BeautifulSoup
from cStringIO import StringIO
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from serializer import JSONSerializerPython2
from healthtools.config import AWS, ES, SLACK, SMALL_BATCH, DATA_DIR
import requests
import boto3
import re
import json
import hashlib
import sys
import os
import socket


class Scraper(object):
    def __init__(self):
        self.num_pages_to_scrape = None
        self.site_url = None
        self.fields = None
        self.s3_key = None
        self.document_id = 0  # id for each entry, to be incremented
        self.delete_file = None  # contains docs to be deleted after scrape
        self.s3_historical_record_key = None  # s3 historical_record key
        self.s3 = boto3.client("s3", **{
            "aws_access_key_id": AWS["aws_access_key_id"],
            "aws_secret_access_key": AWS["aws_secret_access_key"],
            "region_name": AWS["region_name"]
        })
        self.small_batch = True if "small_batch" in sys.argv else False
        try:
            # client host for aws elastic search service
            if "aws" in ES["host"]:
                # set up authentication credentials
                awsauth = AWS4Auth(AWS["aws_access_key_id"], AWS["aws_secret_access_key"], AWS["region_name"], "es")
                self.es_client = Elasticsearch(
                    hosts=ES["host"],
                    port=ES["port"],
                    http_auth=awsauth,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    serializer=JSONSerializerPython2()
                )
            else:
                self.es_client = Elasticsearch("{}:{}".format(ES["host"], ES["port"]))
        except Exception as err:
            self.print_error("[{}] - ERROR: Invalid Parameters For ES Client".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        # if to save locally create relevant directories
        if not AWS["s3_bucket"] and not os.path.exists(DATA_DIR):
            os.mkdir(DATA_DIR)
            os.mkdir(DATA_DIR + "archive")
            os.mkdir(DATA_DIR + "test")

    def scrape_site(self):
        '''
        Scrape the whole site
        '''
        print "[{0}] ".format(re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__))
        print "[{0}] Started Scraper.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        all_results = []
        delete_batch = []
        skipped_pages = 0

        self.get_total_number_of_pages()
        for page_num in range(1, self.num_pages_to_scrape + 1):
            url = self.site_url.format(page_num)
            try:
                self.retries = 0
                scraped_page = self.scrape_page(url)
                if type(scraped_page) != tuple:
                    print "There's something wrong with the site. Proceeding to the next scraper."
                    return

                entries, delete_docs = scraped_page

                all_results.extend(entries)
                delete_batch.extend(delete_docs)
            except Exception as err:
                skipped_pages += 1
                self.print_error("ERROR: scrape_site() - source: {} - page: {} - {}".format(url, page_num, err))
                continue
        print "[{0}] - Scraper completed. {1} documents retrieved.".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(all_results)/2)  # don't count indexing data

        if all_results:
            all_results_json = json.dumps(all_results)
            delete_batch = json.dumps(delete_batch)

            self.delete_elasticsearch_docs()
            self.upload_data(all_results)
            self.archive_data(all_results_json)

            # store delete operations for next scrape
            if AWS["s3_bucket"]:
                delete_file = StringIO(delete_batch)
                self.s3.upload_fileobj(
                    delete_file, AWS["s3_bucket"],
                    self.delete_file)
            else:
                with open(self.delete_file, "w") as delete:
                    json.dump(delete_batch, delete)
            print "[{0}] - Completed Scraper.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            return all_results

    def scrape_page(self, page_url):
        '''
        Get entries from page
        '''
        try:
            soup = self.make_soup(page_url)
            table = soup.find("table", {"class": "zebra"}).find("tbody")
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
                meta, entry = self.format_for_elasticsearch(entry)
                entries.append(meta)
                entries.append(entry)

                delete_batch.append({
                    "delete":
                        {
                            "_index": ES["index"],
                            "_type": meta["index"]["_type"],
                            "_id": entry["id"]
                            }})
                self.document_id += 1
            return entries, delete_batch
        except Exception as err:
            if self.retries >= 5:
                self.print_error("ERROR: Failed to scrape data from page {}  -- {}".format(page_url, str(err)))
                return err
            else:
                self.retries += 1
                self.scrape_page(page_url)

    def upload_data(self, payload):
        '''
        Upload data to Elastic Search
        '''
        try:
            # bulk index the data and use refresh to ensure that our data will be immediately available
            response = self.es_client.bulk(index=ES["index"], body=payload, refresh=True)
            return response
        except Exception as err:
            self.print_error("ERROR - upload_data() - {} - {}".format(type(self).__name__, str(err)))

    def archive_data(self, payload):
        '''
        Upload scraped data to AWS S3
        '''
        try:
            date = datetime.today().strftime("%Y%m%d")
            if AWS["s3_bucket"]:
                old_etag = self.s3.get_object(
                    Bucket=AWS["s3_bucket"], Key=self.s3_key)["ETag"]
                new_etag = hashlib.md5(payload.encode("utf-8")).hexdigest()
                if eval(old_etag) != new_etag:
                    file_obj = StringIO(payload.encode("utf-8"))
                    self.s3.upload_fileobj(file_obj,
                                           AWS["s3_bucket"], self.s3_key)

                    # archive historical data
                    self.s3.copy_object(Bucket=AWS["s3_bucket"],
                                        CopySource="{}/".format(AWS["s3_bucket"]) + self.s3_key,
                                        Key=self.s3_historical_record_key.format(
                                            date))
                    print "[{0}] - Archived data has been updated.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    return
                else:
                    print "[{0}] - Data Scraped does not differ from archived data.".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                # check if it's test and append the correct path
                if "test" in self.s3_key:
                    self.s3_key = DATA_DIR + self.s3_key
                # archive to local dir
                with open(self.s3_key, "w") as data:
                    json.dump(payload, data)
                # archive historical data to local dir
                with open(self.s3_historical_record_key.format(date), "w") as history:
                    json.dump(payload, history)
                print "[{0}] - Archived data has been updated.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        except Exception as err:
            self.print_error("ERROR - archive_data() - {} - {}".format(self.s3_key, str(err)))

    def delete_elasticsearch_docs(self):
        '''
        Delete documents that were uploaded to elasticsearch in the last scrape
        '''
        try:
            # get the type to use with the index depending on the calling method
            if "clinical" in re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__).lower():
                _type = "clinical-officers"
            elif "doctors" in re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__).lower():
                _type = "doctors"
            else:
                _type = "health-facilities"
            # get documents to be deleted
            if AWS["s3_bucket"]:
                delete_docs = self.s3.get_object(
                    Bucket=AWS["s3_bucket"],
                    Key=self.delete_file)["Body"].read()
            else:
                if os.path.exists(self.delete_file):
                    with open(self.delete_file) as delete:
                        delete_docs = json.load(delete)
                else:
                    self.print_error("ERROR - delete_elasticsearch_docs() - no delete file present")
                    return
            # delete
            try:
                response = self.es_client.bulk(index=ES["index"], body=delete_docs, refresh=True)
            except:
                # incase records are saved in cloudsearch's format, reformat for elasticsearch deletion
                delete_records = []
                for record in json.loads(delete_docs):
                    try:
                        delete_records.append({
                            "delete": {
                                "_index": ES["index"],
                                "_type": _type,
                                "_id": record["delete"]["_id"]
                                }
                            })
                    except:
                        delete_records.append({
                            "delete": {
                                "_index": ES["index"],
                                "_type": _type,
                                "_id": record["id"]
                                }
                            })
                response = self.es_client.bulk(index=ES["index"], body=delete_records)
            return response
        except Exception as err:
            if "NoSuchKey" in err:
                self.print_error("ERROR - delete_elasticsearch_docs() - no delete file present")
                return
            self.print_error("ERROR - delete_elasticsearch_docs() - {} - {}".format(type(self).__name__, str(err)))

    def get_total_number_of_pages(self):
        '''
        Get the total number of pages to be scraped
        '''
        try:
            # ensure the number of pages set is restrained to 1-10
            if self.small_batch:
                self.num_pages_to_scrape = SMALL_BATCH
            else:
                soup = self.make_soup(self.site_url.format(1))  # get first page
                text = soup.find("div", {"id": "tnt_pagination"}).getText()
                # what number of pages looks like
                pattern = re.compile("(\d+) pages?")
                self.num_pages_to_scrape = int(pattern.search(text).group(1))
        except Exception as err:
            self.print_error("ERROR: **get_total_page_numbers()** - url: {} - err: {}".format(self.site_url, str(err)))
            return

    def make_soup(self, url):
        '''
        Get page, make and return a BeautifulSoup object
        '''
        response = requests.get(url)  # get first page
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def format_for_elasticsearch(self, entry):
        """
        Format entry into elasticsearch ready document
        :param entry: the data to be formatted
        :return: dictionaries of the entry's metadata and the formatted entry
        """
        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": "index",
                "_type": "type",
                "_id": "id"
                }
            }
        return meta_dict, entry

    def print_error(self, message):
        """
        print error messages in the terminal
        if slack webhook is set up, post the errors to slack
        """
        print("[{0}] - ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + message)
        response = None
        if SLACK["url"]:
            errors = message.split("-")
            try:
                response = requests.post(
                    SLACK["url"],
                    data=json.dumps(
                        {"attachments": [{
                            "author_name": "{}".format(errors[2]),
                            "color": "danger",
                            "pretext": "[SCRAPER] New Alert for{}:{}".format(errors[2], errors[1]),
                            "fields": [{
                                "title": "Message",
                                "value": "{}".format(errors[3]),
                                "short": False}, {
                                "title": "Time",
                                "value": "{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                "short": True}, {
                                "title": "Severity",
                                "value": "{}".format(errors[3].split(":")[1]),
                                "short": True}
                                ]
                            }]}), headers={"Content-Type": "application/json"})
            except:
                # some errors are formatted differently and this block of code handles that
                errors = message.split(":")
                error_message = errors[0].split("-")
                response = requests.post(
                    SLACK["url"],
                    data=json.dumps(
                        {"attachments": [{
                            "author_name": "{}".format(error_message[2]),
                            "color": "danger",
                            "pretext": "[SCRAPER] New Alert for{}:{}".format(error_message[2], error_message[1]),
                            "fields": [{
                                "title": "Message",
                                "value": "{}".format(errors[1]),
                                "short": False}, {
                                "title": "Time",
                                "value": "{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                "short": True}, {
                                "title": "Severity",
                                "value": "{}".format(errors[1].split(".")[0]),
                                "short": True}
                                ]
                                }]}), headers={"Content-Type": "application/json"})
        return response
