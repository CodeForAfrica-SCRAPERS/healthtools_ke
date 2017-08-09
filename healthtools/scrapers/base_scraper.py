from bs4 import BeautifulSoup
from cStringIO import StringIO
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from json_serializer import JSONSerializerPython2
from healthtools.config import AWS, ES, SLACK, DATA_DIR, SMALL_BATCH, NHIF_SERVICES
import requests
import boto3
import re
import json
import hashlib
import sys
import getpass
import time


class Scraper(object):
    '''
    Base Scraper:
    -------------
    This is the default scraper inherited by the rest.
    '''
    def __init__(self):

        self.small_batch = True if "small_batch" in sys.argv else False

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
        self.data_key = DATA_DIR + "data.json"  # Storage key for latest data
        self.data_archive_key = DATA_DIR + "archive/data-{}.json"  # Storage key for data to archive

        try:
            # client host for aws elastic search service
            if "aws" in ES["host"]:
                # set up authentication credentials
                awsauth = AWS4Auth(AWS["aws_access_key_id"], AWS["aws_secret_access_key"], AWS["region_name"], "es")
                self.es_client = Elasticsearch(
                    hosts=[{"host": ES["host"], "port": int(ES["port"])}],
                    http_auth=awsauth,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    serializer=JSONSerializerPython2()
                )

            else:
                self.es_client = Elasticsearch("{}:{}".format(ES["host"], ES["port"]))
        except Exception as err:
            self.print_error("ERROR: Invalid parameters for ES Client: {}".format(str(err)))

        self.results = []
        self.results_es = []

    def run_scraper(self):
        '''
        This function works to display some output and run scrape_site()
        '''
        print "[{}] ".format(re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__))
        print "[{}] Started Scraper.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        self.scrape_site()

        print "[{}] Scraper completed. {} documents retrieved.".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(self.results))

        return self.results

    def scrape_site(self):
        '''
        This functions scrapes the entire website by calling each page.
        '''
        self.set_site_pages_no()

        for page_num in range(1, self.site_pages_no + 1):
            # Check if is NHIF and if so just use page_num else format site_url
            nhif = set(re.sub(r"(\w)([A-Z])", r"\1 \2", type(self).__name__).lower().split()) &\
                set(NHIF_SERVICES)

            url = page_num if nhif else self.site_url.format(page_num)

            try:
                results, results_es = self.scrape_page(url, 0)

                if type(results) != list:
                    self.print_error("ERROR: scrape_site() \nsource: {} \npage: {} \ndata: {}".
                                     format(url, page_num, results))
                    return

                self.results.extend(results)
                self.results_es.extend(results_es)

            except Exception as err:
                self.print_error("ERROR: scrape_site() \nsource: {} \npage: {} \nerr: {}".format(url, page_num, err))
                return

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
                self.print_error("ERROR: Failed to scrape data from page. \nurl: {} \nmsg: {}".format(page_url, str(err)))
                return err
            else:
                page_retries += 1
                print("Try {}/5 has failed... \nERROR: {} \nGoing to sleep for {} seconds.".
                      format(page_retries, err, page_retries*5))
                time.sleep(page_retries*5)
                self.scrape_page(page_url, page_retries)

    def set_site_pages_no(self):
        '''
        Set the total number of pages to be scraped
        '''
        try:
            # If small batch is set, that would be the number of pages.
            if self.small_batch:
                self.site_pages_no = SMALL_BATCH
            else:
                soup = self.make_soup(self.site_url.format(1))
                text = soup.find("div", {"id": "tnt_pagination"}).getText()
                # What number of pages looks like
                pattern = re.compile("(\d+) pages?")
                self.site_pages_no = int(pattern.search(text).group(1))
        except Exception as err:
            self.print_error("ERROR: get_total_page_numbers() - url: {} - err: {}".format(self.site_url, str(err)))
            return

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
                "_index": ES["index"],
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
                print("[{0}] Elasticsearch: Index successfully created.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            # bulk index the data and use refresh to ensure that our data will be immediately available
            response = self.es_client.bulk(index=ES["index"], body=results, refresh=True)
            print("[{0}] Elasticsearch: Index successful.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            return response
        except Exception as err:
            self.print_error("ERROR: elasticsearch_index() - {} \nmsg: {}".format(type(self).__name__, str(err)))

    def elasticsearch_delete_docs(self):
        '''
        Delete documents that were uploaded to elasticsearch in the last scrape
        '''
        try:
            delete_query = {"query": {"match_all": {}}}
            try:
                response = self.es_client.delete_by_query(index=self.es_index, doc_type=self.es_doc, body=delete_query, _source=True)
                return response
            except Exception as err:
                self.print_error("ERROR: elasticsearch_delete_docs() - {} - {}".format(type(self).__name__, str(err)))

        except Exception as err:
            self.print_error("ERROR: elasticsearch_delete_docs() - {} - {}".format(type(self).__name__, str(err)))

    def archive_data(self, payload):
        '''
        Upload scraped data to AWS S3
        '''
        data_key = DATA_DIR + self.data_key
        data_archive_key = DATA_DIR + self.data_archive_key
        try:
            date = datetime.today().strftime("%Y%m%d")
            self.data_key = DATA_DIR + self.data_key
            self.data_archive_key = DATA_DIR + self.data_archive_key
            if AWS["s3_bucket"]:
                old_etag = self.s3.get_object(
                    Bucket=AWS["s3_bucket"], Key=self.data_key)["ETag"]
                new_etag = hashlib.md5(payload.encode("utf-8")).hexdigest()
                if eval(old_etag) != new_etag:
                    file_obj = StringIO(payload.encode("utf-8"))
                    self.s3.upload_fileobj(file_obj,
                                           AWS["s3_bucket"], self.data_key)

                    # archive historical data
                    self.s3.copy_object(Bucket=AWS["s3_bucket"],
                                        CopySource="{}/".format(AWS["s3_bucket"]) + self.data_key,
                                        Key=self.data_archive_key.format(date))
                    print "[{0}] Archive: Data has been updated.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    return
                else:
                    print "[{0}] Archive: Data scraped does not differ from archived data.".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                # archive to local dir
                with open(self.data_key, "w") as data:
                    json.dump(payload, data)
                # archive historical data to local dir
                with open(self.data_archive_key.format(date), "w") as history:
                    json.dump(payload, history)
                print("[{0}] Archived: Data has been updated.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        except Exception as err:
            self.print_error(
                "ERROR: archive_data() - {} - {}".format(self.data_key, str(err)))

    def print_error(self, message):
        '''
        Print error messages in the terminal.
        If slack webhook is set up, post the errors to Slack.
        '''
        print("[{0}] - ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + message)
        response = None
        if SLACK["url"]:
            errors = message.split("-", 3)
            try:
                severity = errors[2].split(":")[1]
            except:
                severity = errors[1]
            response = requests.post(
                SLACK["url"],
                data=json.dumps({
                    "attachments":[
                        {
                            "author_name": "{}".format(errors[1]),
                            "color": "danger",
                            "pretext": "[SCRAPER] New Alert for{}:{}".format(errors[1], errors[0]),
                            "fields": [
                                {
                                    "title": "Message",
                                    "value": "{}".format(errors[2]),
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
                                {
                                    "title": "Severity",
                                    "value": "{}".format(severity),
                                    "short": True
                                }
                            ]
                        }
                    ]
                }),
                headers={"Content-Type": "application/json"}
            )
        return response
