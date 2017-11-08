import json
import math
import logging
from elasticsearch import Elasticsearch
from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SMALL_BATCH_HF, ES
import requests
from datetime import datetime

log = logging.getLogger(__name__)

TOKEN_URL = "http://api.kmhfl.health.go.ke/o/token/"
SEARCH_URL = "http://api.kmhfl.health.go.ke/api/facilities/material/?page_size={}&" \
             "fields=id,regulatory_status_name,facility_type_name,facility_type_parent,owner_name,owner_type_name," \
             "owner_type,operation_status_name,county,constituency,constituency_name,ward_name,average_rating," \
             "facility_services,is_approved,has_edits,latest_update,regulatory_body_name,owner,date_requested," \
             "date_approved,latest_approval_or_rejection,sub_county_name,sub_county_id,county_name,constituency_id," \
             "county_id,keph_level_name,facility_contacts,coordinates,lat_long,latest_approval,county_code,constituency_code" \
             ",ward_code,service_catalogue_active,facility_units,officer_in_charge,created,updated,deleted,active,search," \
             "name,official_name,code,registration_number,abbreviation,description,number_of_beds,number_of_cots," \
             "open_whole_day,open_public_holidays,open_normal_day,open_weekends,open_late_night,is_classified," \
             "is_published,regulated,approved,rejected,bank_name,branch_name,bank_account,facility_catchment_population," \
             "town_name,nearest_landmark,plot_number,location_desc,closed,closed_date,closing_reason,date_established," \
             "license_number,created_by,updated_by,facility_type,operation_status,ward,parent,regulatory_body," \
             "keph_level,sub_county,town,regulation_status,contacts&format=json"


class HealthFacilitiesScraper(Scraper):
    def __init__(self):
        super(HealthFacilitiesScraper, self).__init__()
        self.es_doc = "health-facilities"
        self.data_key = "health_facilities.json"
        self.data_archive_key = "archive/health_facilities-{}.json"

        self.access_token = None

    def index_to_es(self, current_result):
        current_page_data = []        
        page_count = 1
        total_pages = int(math.ceil(len(current_result) / float(10000)))
        while page_count <= total_pages:
            start_index = (page_count - 1) * 10000
            end_index = start_index + 10000
            current_page_data = current_result[start_index: end_index]
            self.elasticsearch_index(current_page_data)
            page_count += 1

    def scrape_site(self):
        doc = {
            'size': 10000,
            'query': {
                'match_all': {}
            }
        }
        existing_index_data = self.es_client.search(
            index=ES["index"], doc_type=self.es_doc, body=doc, scroll='1m')
        try:
            self.get_token()
            self.get_data()
            current_result = self.results_es
            if current_result:
                self.elasticsearch_delete_docs()
                self.index_to_es(current_result)
                self.archive_data(json.dumps(current_result))

        except Exception as err:
            existing_index_data = existing_index_data['hits']['hits']
            # add the meta and entry for the existing index
            page_data = []
            for hit in existing_index_data:
                hit = hit.get('_source')
                # reassign a new doc_id, to maintain order like 1, 2,..
                hit["id"] = self.doc_id
                meta, entry = self.elasticsearch_format(hit, True)
                page_data.append(meta)
                page_data.append(entry)

                self.doc_id += 1
            self.index_to_es(page_data)
            self.archive_data(json.dumps(page_data))
            error = {
                "ERROR": "scrape_site()",
                "MESSAGE": str(err)
            }
            self.print_error(error)
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
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        self.access_token = json.loads(response.text)["access_token"]
        log.info("Access token received.")

    def get_data(self):
        url = SEARCH_URL.format(1000000)
        if self.small_batch:
            url = SEARCH_URL.format(SMALL_BATCH_HF)
        headers = {"Authorization": "Bearer " + self.access_token}
        r = requests.get(url, headers=headers)
        data = r.json()
        for entry in data["results"]:
            entry["id"] = self.doc_id
            meta, entry = self.elasticsearch_format(entry)
            self.results_es.append(meta)
            self.results_es.append(entry)
            self.results.append(entry)

            self.doc_id += 1

    def elasticsearch_format(self, entry, isExisting=False):
        meta_dict = {
            "index": {
                "_index": self.es_index,
                "_type": self.es_doc,
                "_id": self.doc_id
            }
        }
        if not isExisting:
            entry["ward_name"] = entry["ward_name"].decode(
                "string_escape").replace("\\", "")
        return meta_dict, entry
