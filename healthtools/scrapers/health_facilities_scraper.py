from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, AWS
from datetime import datetime
import requests
import json
import boto3
import scraperwiki
scraperwiki.config = { db: 'data.sqlite', default_table_name: 'data' }

TOKEN_URL = 'http://api.kmhfl.health.go.ke/o/token/'
SEARCH_URL = 'http://api.kmhfl.health.go.ke/api/facilities/material/?page_size=10000&' \
             'fields=id,regulatory_status_name,facility_type_name,facility_type_parent,owner_name,owner_type_name,' \
             'owner_type,operation_status_name,county,constituency,constituency_name,ward_name,average_rating,' \
             'facility_services,is_approved,has_edits,latest_update,regulatory_body_name,owner,date_requested,' \
             'date_approved,latest_approval_or_rejection,sub_county_name,sub_county_id,county_name,constituency_id,' \
             'county_id,keph_level_name,facility_contacts,coordinates,lat_long,latest_approval,county_code,constituency_code' \
             ',ward_code,service_catalogue_active,facility_units,officer_in_charge,created,updated,deleted,active,search,' \
             'name,official_name,code,registration_number,abbreviation,description,number_of_beds,number_of_cots,' \
             'open_whole_day,open_public_holidays,open_normal_day,open_weekends,open_late_night,is_classified,' \
             'is_published,regulated,approved,rejected,bank_name,branch_name,bank_account,facility_catchment_population,' \
             'town_name,nearest_landmark,plot_number,location_desc,closed,closed_date,closing_reason,date_established,' \
             'license_number,created_by,updated_by,facility_type,operation_status,ward,parent,regulatory_body,' \
             'keph_level,sub_county,town,regulation_status,contacts&format=json'


class HealthFacilitiesScraper(Scraper):
    def __init__(self):
        self.access_token = None
        self.fields = [
            "name", "facility_type_name", "approved", "sub_county_name",
            "service_names", "county_name", "open_public_holidays",
            "keph_level_name", "open_whole_day", "owner_name",
            "constituency_name", "regulatory_body_name", "operation_status_name", "open_late_night", "open_weekends", "ward_name"
        ]
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **{
                "aws_access_key_id": AWS["aws_access_key_id"],
                "aws_secret_access_key": AWS["aws_secret_access_key"],
                "region_name": AWS["region_name"],
                "endpoint_url": AWS["cloudsearch_doctors_endpoint"]
            })

    def get_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'username': 'public@mfltest.slade360.co.ke',
            'password': 'public',
            'grant_type': 'password',
            'client_id': 'xMddOofHI0jOKboVxdoKAXWKpkEQAP0TuloGpfj5',
            'client_secret': 'PHrUzCRFm9558DGa6Fh1hEvSCh3C9Lijfq8sbCMZhZqmANYV5ZP04mUXGJdsrZLXuZG4VCmvjShdKHwU6IRmPQld5LDzvJoguEP8AAXGJhrqfLnmtFXU3x2FO1nWLxUx'
        }
        r = requests.post(TOKEN_URL, data=data, headers=headers)
        self.access_token = json.loads(r.text)['access_token']
        print self.access_token

    def get_data(self):
        try:
            headers = {'Authorization': 'Bearer ' + self.access_token}
            r = requests.get(SEARCH_URL, headers=headers)
            data = r.json()
            print "DEBUG - get_data() - %s - %s" % (len(data['results']), r.reason)
            payload = ''
            for i, record in enumerate(data['results']):
                scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
                payload += self.index_for_cloudsearch(record) + ','
                #Every 100th entry push to cloudsearch or if we have reached the end push to cloudsearch
                if i % 100 == 0 or i == (len(data['results']) - 1):
                    payload = '[%s]' % payload[:-1] #remove last comma
                    print i
                    self.push_to_cloud_search(payload)
                    payload = ''
        except Exception, err:
            print "ERROR - index_for_search() - %s" % (err)

    def index_for_cloudsearch(self, record):
        return index_template.health_facilities_template  % (
            record['code'],
            record['name'].replace("\"","'"),
            record['facility_type_name'],
            record['service_names'],
            record['sub_county_name'],
            record['service_names'],
            record['county_name'],
            record['open_public_holidays'],
            record['keph_level_name'],
            record['open_whole_day'],
            record['owner_name'],
            record['constituency_name'],
            record['regulatory_body_name'],
            record['operation_status_name'],
            record['open_late_night'],
            record['open_weekends'],
            record['ward_name'].decode("string_escape").replace('\\',''),
      )

    def push_to_cloud_search(self, payload):
        try:
          response = self.cloudsearch.upload_documents(
              documents=payload, contentType="application/json"
          )
        print "DEBUG - index_for_search() - %s - %s" % (len(payload), response.get("status"))
        except Exception, err:
          print "ERROR - index_for_search() - %s - %s" % (len(payload), err)

