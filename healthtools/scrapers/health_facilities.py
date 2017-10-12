import json
import math
from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SMALL_BATCH_HF
import requests
from datetime import datetime

TOKEN_URL = "http://api.kmhfl.health.go.ke/o/token/"
SEARCH_URL = "http://api.kmhfl.health.go.ke/api/facilities/material/\
?format=json&page={}&page_size=5000"


class HealthFacilitiesScraper(Scraper):
    def __init__(self):
        super(HealthFacilitiesScraper, self).__init__()
        self.es_doc = "health-facilities"
        self.data_key = "health_facilities.json"
        self.data_archive_key = "archive/health_facilities-{}.json"

        self.access_token = None
        self.total_pages = 0

    def scrape_site(self, page_no=1):
        self.get_token()
        self.get_data(page_no)
        if self.results:
            self.elasticsearch_delete_docs()
            self.elasticsearch_index(self.results_es)
        try:
            while page_no < self.total_pages:
                self.get_data(page_no + 1)
                if self.results:
                    self.elasticsearch_index(self.results_es)
                page_no += 1
        except Exception as err:
            error = {
                "ERROR": "scrape_site()",
                "MESSAGE": str(err)
            }
            self.print_error(error)
        self.archive_data(json.dumps(self.results))
        return self.results

    def get_token(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "username": "public@mfltest.slade360.co.ke",
            "password": "public",
            "grant_type": "password",
            "client_id": "xMddOofHI0jOKboVxdoKAXWKpkEQAP0TuloGpfj5",
            "client_secret": "PHrUzCRFm9558DGa6Fh1hEvSCh3C9Lijfq8sbCMZhZqmANYV5ZP04mUXGJdsrZLXuZG4VCmvjShdKHwU6IRmPQld5LDzvJoguEP8AAXGJhrqfLnmtFXU3x2FO1nWLxUx"
        }
        try:
            response = requests.post(TOKEN_URL, data=data, headers=headers)
            self.access_token = json.loads(response.text)["access_token"]
            print("[{0}] Access token received.".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except Exception as err:
            error = {
                "ERROR": "get_token()",
                "MESSAGE": str(err)
            }
            self.print_error(error)

    def get_data(self, page_no):
        self.results_es = []
        try:
            url = SEARCH_URL.format(page_no)
            if self.small_batch:
                url = SEARCH_URL.format(SMALL_BATCH_HF)
            headers = {"Authorization": "Bearer " + self.access_token}
            r = requests.get(url, headers=headers)
            data = r.json()
            total_hits = data["count"]
            self.total_pages = int(math.ceil(total_hits/float(5000)))

            for entry in data["results"]:
                entry["id"] = self.doc_id
                meta, entry = self.elasticsearch_format(entry)
                self.results_es.append(meta)
                self.results_es.append(entry)
                self.results.append(entry)

                self.doc_id += 1

        except Exception as err:
            error = {
                "ERROR": "get_data()",
                "MESSAGE": str(err)
            }
            self.print_error(error)

    def elasticsearch_format(self, entry):
        meta_dict = {
            "index": {
                "_index": self.es_index,
                "_type": self.es_doc,
                "_id": self.doc_id
            }
        }
        entry["ward_name"] = entry["ward_name"].decode("string_escape").replace("\\", "")
        return meta_dict, entry
