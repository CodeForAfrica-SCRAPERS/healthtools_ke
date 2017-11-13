import argparse
import boto3
import getpass
import hashlib
import json
import logging
import re
import requests
import time

from time import gmtime, strftime
from bs4 import BeautifulSoup
from io import StringIO
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from termcolor import colored

from healthtools.config import (AWS, ES, SLACK, DATA_DIR,
                                SMALL_BATCH, NHIF_SERVICES)
from healthtools.lib.json_serializer import JSONSerializerPython2

from healthtools.handle_s3_objects import S3ObjectHandler

log = logging.getLogger(__name__)

class Scraper(object):
    '''
    Base Scraper:
    -------------
    This is the default scraper inherited by the rest.
    '''

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-sb', '--small-batch', action="store_true",
                            help="Specify option to scrape limited pages from site in development mode")
        parser.add_argument('-scr', '--scraper', nargs='+',
                            choices=["doctors", "clinical_officers",
                                     "health_facilities", "nhif_inpatient",
                                     "nhif_outpatient", "nhif_outpatient_cs"],
                            help="Specify to allow selection of what to scrape")

        self.args = parser.parse_args()

        self.small_batch = True if self.args.small_batch else False

        self.site_url = None
        self.site_pages_no = None
        self.fields = None

        self.doc_id = 1  # Id for each entry, to be incremented
        self.es_index = ES["index"]  # Elasticsearch index
        self.es_doc = None  # Elasticsearch doc_type

        self.s3 = boto3.client("s3", **{
            "aws_access_key_id": AWS["aws_access_key_id"],
            "aws_secret_access_key": AWS["aws_secret_access_key"],
            "region_name": AWS["region_name"]
        })

        self.s3_handler = S3ObjectHandler(self.s3)

        self.data_key = DATA_DIR + "data.json"  # Storage key for latest data
        # Storage key for data to archive
        self.data_archive_key = DATA_DIR + "archive/data-{}.json"

        try:
            # client host for aws elastic search service
            if "aws" in ES["host"]:
                # set up authentication credentials
                awsauth = AWS4Auth(AWS["aws_access_key_id"],
                                   AWS["aws_secret_access_key"],
                                   AWS["region_name"], "es")
                self.es_client = Elasticsearch(
                    hosts=[{"host": ES["host"], "port": int(ES["port"])}],
                    http_auth=awsauth,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    serializer=JSONSerializerPython2()
                )

            else:
                self.es_client = Elasticsearch(
                    "{}:{}".format(ES["host"], ES["port"]))
        except Exception as err:
            error = {
                "ERROR": "ES Client Set Up",
                "SOURCE": "Invalid parameters for ES Client",
                "MESSAGE": str(err)
            }
            self.print_error(error)

        self.results = []
        self.results_es = []

        self.scraping_started = time.time()
        self.scraping_ended = time.time()
        self.stat_log = {}

    def run_scraper(self):
        '''
        This function works to display some output and run scrape_site()
        '''
        self.scraping_started = time.time()
        scraper_name = re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__)

        _scraper_name = re.sub(" Scraper", "", scraper_name).lower()
        _scraper_name = re.sub(" ", "_", _scraper_name)

        if self.args.scraper and "doctors" in self.args.scraper:
            self.args.scraper.append("foreign_doctors")

        if not self.args.scraper or \
                (self.args.scraper and _scraper_name in self.args.scraper):

            log.info("[%s]", re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__))
            log.info("Started Scraper.")

            self.scrape_site()
            
            self.scraping_ended = time.time()
            time_taken_in_secs = self.scraping_ended - self.scraping_started
            m, s = divmod(time_taken_in_secs, 60)
            h, m = divmod(m, 60)        
            time_taken = "%dhr:%02dmin:%02dsec" % (h, m, s) if time_taken_in_secs > 60 else '{} seconds'.format(time_taken_in_secs)
            self.stat_log = {
                'Scraping took': time_taken,
                'Last successfull Scraping was': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                'Total documents scraped': len(self.results)
            }
            log.info("[%s] Scraper completed. %s documents retrieved.",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(self.results))

            return self.results

    def scrape_site(self):
        '''
        This functions scrapes the entire website by calling each page.
        '''
        self.set_site_pages_no()

        if not self.site_pages_no:
            error = {
                "ERROR": "scrape_site()",
                "SOURCE": self.site_url,
                "MESSAGE": "No pages found."
            }
            self.print_error(error)
            return

        for page_num in range(1, self.site_pages_no + 1):
            # Check if is NHIF and if so just use page_num else format site_url
            nhif = set(re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__).lower().split()) &\
                set(NHIF_SERVICES)

            url = page_num if nhif else self.site_url.format(page_num)

            results, results_es = self.scrape_page(url, 5)

            if type(results) != list:
                error = {
                    "ERROR": "scrape_site()",
                    "SOURCE": url,
                    "MESSAGE": "page: {} \ndata: {}".format(page_num, results)
                }
                self.print_error(error)
                return

            self.results.extend(results)
            self.results_es.extend(results_es)

        if self.results:
            self.archive_data(json.dumps(self.results))
            self.elasticsearch_delete_docs()
            self.elasticsearch_index(self.results_es)

        return self.results

    def scrape_page(self, page_url, page_retries):
        '''
        Scrape the page for the data.
        '''
        try:
            soup = self.make_soup(page_url)
            table = soup.find("table", {"class": "zebra"}).find("tbody")
            rows = table.find_all("tr")

            results = []
            results_es = []
            for row in rows:
                # only the columns we want
                # -1 because fields/columns has extra index; id
                columns = row.find_all("td")[:len(self.fields) - 1]
                columns = [text.text.strip() for text in columns]
                columns.append(self.doc_id)

                entry = dict(zip(self.fields, columns))
                meta, entry = self.elasticsearch_format(entry)
                results_es.append(meta)
                results_es.append(entry)
                results.append(entry)

                self.doc_id += 1
                
            return results, results_es

        except Exception as err:
            if page_retries >= 5:
                error = {
                    "ERROR": "scrape_page()",
                    "SOURCE": page_url,
                    "MESSAGE": str(err)
                }
                self.print_error(error)
                return
            else:
                page_retries += 1
                error = {
                    "ERROR": "Try {}/5 has failed...".format(page_retries),
                    "SOURCE": page_url,
                    "MESSAGE": "{} \nGoing to sleep for {} seconds.".format(err, page_retries * 5)
                }
                self.print_error(error)

                time.sleep(page_retries * 5)
                self.scrape_page(page_url, page_retries)

    def set_site_pages_no(self):
        '''
        Set the total number of pages to be scraped
        '''
        try:
            soup = self.make_soup(self.site_url.format(1))
            text = soup.find("div", {"id": "tnt_pagination"}).getText()
            # What number of pages looks like
            pattern = re.compile("(\d+) pages?")
            self.site_pages_no = int(pattern.search(text).group(1))
        except Exception as err:
            error = {
                "ERROR": "get_total_page_numbers()",
                "SOURCE": self.site_url,
                "MESSAGE": str(err)
            }
            self.print_error(error)

        # If small batch is set, that would be the number of pages.
        if self.small_batch and self.site_pages_no and self.site_pages_no > SMALL_BATCH:
            self.site_pages_no = SMALL_BATCH

        return self.site_pages_no

        # TODO: Print how many pages we found

    def make_soup(self, url):
        '''
        Get page, make and return a BeautifulSoup object
        '''
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def elasticsearch_format(self, entry):
        """
        Format entry into elasticsearch ready document
        :param entry: the data to be formatted
        :return: dictionaries of the entry's metadata and the formatted entry
        """
        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": self.es_index,
                "_type": self.es_doc,
                "_id": entry["id"]
            }
        }
        return meta_dict, entry

    def elasticsearch_index(self, results):
        '''
        Upload data to Elastic Search
        '''
        try:
            # sanity check
            if not self.es_client.indices.exists(index=self.es_index):
                self.es_client.indices.create(index=self.es_index)
                log.info("Elasticsearch: Index successfully created.")

            # bulk index the data and use refresh to ensure that our data will
            # be immediately available
            response = self.es_client.bulk(
                index=self.es_index, body=results, refresh=True)
            log.info("Elasticsearch: Index successful.")
            return response
        except Exception as err:
            error = {
                "ERROR": "elasticsearch_index()",
                "SOURCE": type(self).__name__,
                "MESSAGE": str(err)
            }
            self.print_error(error)

    def elasticsearch_delete_docs(self):
        '''
        Delete documents that were uploaded to elasticsearch in the last scrape
        '''
        try:
            delete_query = {"query": {"match_all": {}}}
            try:
                response = self.es_client.delete_by_query(
                    index=self.es_index, doc_type=self.es_doc,
                    body=delete_query, _source=True)
                return response
            except Exception as err:
                error = {
                    "ERROR": "elasticsearch_delete_docs()",
                    "SOURCE": type(self).__name__,
                    "MESSAGE": str(err)
                }
                self.print_error(error)

        except Exception as err:
            error = {
                "ERROR": "elasticsearch_delete_docs()",
                "SOURCE": type(self).__name__,
                "MESSAGE": str(err)
            }
            self.print_error(error)

    def archive_data(self, payload):
        '''
        Upload scraped data to AWS S3
        '''
        try:
            date = datetime.today().strftime("%Y%m%d")
            self.data_key = DATA_DIR + self.data_key
            self.data_archive_key = DATA_DIR + self.data_archive_key

            if AWS["s3_bucket"]:
                # Check if bucket exists and has the expected file structure
                self.s3_handler.handle_s3_objects(
                    bucket_name=AWS["s3_bucket"], key=self.data_key)

                old_etag = self.s3.get_object(
                    Bucket=AWS["s3_bucket"], Key=self.data_key)["ETag"]
                new_etag = hashlib.md5(payload.encode("utf-8")).hexdigest()
                if eval(old_etag) != new_etag:
                    file_obj = StringIO(payload.encode("utf-8"))
                    self.s3.upload_fileobj(file_obj,
                                           AWS["s3_bucket"], self.data_key)

                    # archive historical data
                    self.s3.copy_object(Bucket=AWS["s3_bucket"],
                                        CopySource="{}/".format(
                                            AWS["s3_bucket"]) + self.data_key,
                                        Key=self.data_archive_key.format(date))
                    log.info("Archive: Data has been updated.")
                    return
                else:
                    log.info("Archive: Data scraped does not differ from archived data.")
            else:
                # archive to local dir
                with open(self.data_key, "w") as data:
                    json.dump(payload, data)
                # archive historical data to local dir
                with open(self.data_archive_key.format(date), "w") as history:
                    json.dump(payload, history)
                log.info("Archived: Data has been updated.")

        except Exception as err:
            error = {
                "ERROR": "archive_data()",
                "SOURCE": self.data_key,
                "MESSAGE": str(err)
            }

            self.print_error(error)

    def print_error(self, message):
        '''
        Print error messages in the terminal.
        If slack webhook is set up, post the errors to Slack.
        '''

        error = "- ERROR: " + message['ERROR']
        source = ("- SOURCE: " + message['SOURCE']) if "SOURCE" in message else ""
        error_msg = "- MESSAGE: " + message['MESSAGE']
        msg = "\n".join([error, source, error_msg])

        log.error(msg)

        response = None
        if SLACK["url"]:
            try:
                errors = {
                    "author": message['ERROR'],
                    "pretext": message['SOURCE'],
                    "message": message['MESSAGE'],
                }
            except:
                errors = {
                    "pretext": "",
                    "author": message,
                    "message": message,
                }

            response = requests.post(
                SLACK["url"],
                data=json.dumps({
                    "attachments": [
                        {
                            "username": "Slack Logger",
                            "author_name": "{}".format(errors["author"]),
                            "color": "danger",
                            "pretext": "[SCRAPER] New Alert for {} : {}".format(errors["author"], errors["pretext"]),
                            "fields": [
                                {
                                    "title": "Message",
                                    "value": "{}".format(errors["message"]),
                                    "short": False
                                },
                                {
                                    "title": "Machine Location",
                                    "value": "{}".format(getpass.getuser()),
                                    "short": True
                                },
                                {
                                    "title": "Time",
                                    "value": "{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                    "short": True},
                            ]
                        }
                    ]
                }),
                headers={"Content-Type": "application/json"}
            )
        return response

        
    def parse_date(self, datetime_string):
        '''
        Parse a string into a datetime object 
        :param datetime_string: the datetime string to parse
        :return: datetime object
        '''
        from dateutil.parser import parse   
        try:
            dateobject = parse(datetime_string)
            return dateobject
        except Exception as ex:
            log.error('Can not create a the datetime object from {}.'.format(datetime_string))
            return None
