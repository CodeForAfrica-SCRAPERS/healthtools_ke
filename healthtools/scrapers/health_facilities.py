import json
from cStringIO import StringIO
from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import ES, SMALL_BATCH_HF, AWS
import requests
from datetime import datetime

TOKEN_URL = "http://api.kmhfl.health.go.ke/o/token/"
SEARCH_URL = "http://api.kmhfl.health.go.ke/api/facilities/material/?page_size=100000&" \
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
        self.access_token = None
        self.s3_key = "data/health_facilities.json"
        self.s3_historical_record_key = "data/archive/health_facilities-{}.json"
        self.payload = []
        self.count = 0

    def get_token(self):
        print "[Health Facilities Scraper]"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "username": "public@mfltest.slade360.co.ke",
            "password": "public",
            "grant_type": "password",
            "client_id": "xMddOofHI0jOKboVxdoKAXWKpkEQAP0TuloGpfj5",
            "client_secret": "PHrUzCRFm9558DGa6Fh1hEvSCh3C9Lijfq8sbCMZhZqmANYV5ZP04mUXGJdsrZLXuZG4VCmvjShdKHwU6IRmPQld5LDzvJoguEP8AAXGJhrqfLnmtFXU3x2FO1nWLxUx"
            }
        try:
            res = requests.post(TOKEN_URL, data=data, headers=headers)
            self.access_token = json.loads(res.text)["access_token"]
        except Exception as err:
            self.print_error("ERROR IN - get_token() - Health Facilities Scraper - {}".format(str(err)))

    def upload(self, payload):
        return self.upload_data(payload)

    def get_data(self):
        try:
            print "[{0}] - Started Scraper.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            headers = {"Authorization": "Bearer " + self.access_token}
            r = requests.get(SEARCH_URL, headers=headers)
            data = r.json()
            if self.small_batch:
                for i, record in enumerate(data["results"]):
                    if i < SMALL_BATCH_HF:
                        meta, elastic_data = self.index_for_elasticsearch(record)
                        self.payload.append(meta)
                        self.payload.append(elastic_data)
                    else:
                        self.count = i
                        break
            else:
                for i, record in enumerate(data["results"]):
                    meta, elastic_data = self.index_for_elasticsearch(record)
                    self.payload.append(meta)
                    self.payload.append(elastic_data)
                    self.count = i
            self.delete_elasticsearch_docs(ES["index"])  # delete elasticsearch data
            self.upload(self.payload)  # upload data to elasticsearch
            print "{{{0}}} - Scraper completed. {1} records retrieved.".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.count)
            # save the data
            self.archive_data(json.dumps(self.payload))

            print "{{{0}}} - Completed Scraper.".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        except Exception as err:
            self.print_error("ERROR IN - index_for_search() Health Facilities Scraper - {}".format(err))

    def index_for_elasticsearch(self, record):
        meta_data = {"index": {
            "_index": ES["index"],
            "_type": "health-facilities",
            "_id": record["code"]
            }}
        health_facilities = {
            "id": record["code"],
            "name": record["name"].replace("\"", "'"),
            "facility_type_name": record["facility_type_name"],
            "approved": record["approved"],
            "sub_county_name": record["sub_county_name"],
            "service_names": record["service_names"],
            "county_name": record["county_name"],
            "open_public_holidays": record["open_public_holidays"],
            "keph_level_name": record["keph_level_name"],
            "open_whole_day": record["open_whole_day"],
            "owner_name": record["owner_name"],
            "constituency_name": record["constituency_name"],
            "regulatory_body_name": record["regulatory_body_name"],
            "operation_status_name": record["operation_status_name"],
            "open_late_night": record["open_late_night"],
            "open_weekends": record["open_weekends"],
            "ward_name": record["ward_name"].decode("string_escape").replace("\\", "")
            }
        return meta_data, health_facilities

    def scrape_data(self):
        self.get_token()
        self.get_data()
