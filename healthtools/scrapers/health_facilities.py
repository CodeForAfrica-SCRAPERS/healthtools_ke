import json
from datetime import datetime
from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import AWS
import requests
import boto3


TOKEN_URL = 'http://api.kmhfl.health.go.ke/o/token/'
SEARCH_URL = 'http://api.kmhfl.health.go.ke/api/facilities/material/?page_size=100000&' \
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
    '''
    Scraper for health facilities from kenya master health facilities list
    '''
    def __init__(self):
        super(HealthFacilitiesScraper, self).__init__()
        self.access_token = None
        self.s3_key = "data/health_facilities.json"
        self.s3_historical_record_key = "data/archive/health_facilities-{}.json"
        self.delete_file = "data/delete_health_facilities.json"
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **{
                "aws_access_key_id": AWS["aws_access_key_id"],
                "aws_secret_access_key": AWS["aws_secret_access_key"],
                "region_name": AWS["region_name"],
                "endpoint_url": AWS["cloudsearch_health_faciities_endpoint"]
            })

    def get_token(self):
        print "[Health Facilities Scraper]"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'username': 'public@mfltest.slade360.co.ke',
            'password': 'public',
            'grant_type': 'password',
            'client_id': 'xMddOofHI0jOKboVxdoKAXWKpkEQAP0TuloGpfj5',
            'client_secret': 'PHrUzCRFm9558DGa6Fh1hEvSCh3C9Lijfq8sbCMZhZqmANYV5ZP04mUXGJdsrZLXu' \
            'ZG4VCmvjShdKHwU6IRmPQld5LDzvJoguEP8AAXGJhrqfLnmtFXU3x2FO1nWLxUx'
        }
        res = requests.post(TOKEN_URL, data=data, headers=headers)
        self.access_token = json.loads(res.text)['access_token']

    def get_data(self):
        try:
            print "{{{0}}} - Started Scraper.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            headers = {'Authorization': 'Bearer ' + self.access_token}
            res = requests.get(SEARCH_URL, headers=headers)
            data = res.json()
            results = data['results']

            print "{{{0}}} - Scraper completed. {1} documents retrieved." \
            "".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),len(data['results']))
            self.push_to_elasticsearch(results[0:2])
            self.archive_data(json.dumps(results))
            print "{{{0}}} - Completed Scraper.".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        except Exception, err:
            print "ERROR IN - index_for_search() - %s" % (err)

    def format_doc(self, entry):
        return {
            "id":entry['code'],
            "name":entry['name'].replace("\"", "'"),
            "facility_type_name":entry['facility_type_name'],
            "approved":entry['approved'],
            "sub_county_name":entry['sub_county_name'],
            "service_names":entry['service_names'],
            "county_name":entry['county_name'],
            "open_public_holidays":entry['open_public_holidays'],
            "keph_level_name":entry['keph_level_name'],
            "open_whole_day":entry['open_whole_day'],
            "owner_name":entry['owner_name'],
            "constituency_name":entry['constituency_name'],
            "regulatory_body_name":entry['regulatory_body_name'],
            "operation_status_name":entry['operation_status_name'],
            "open_late_night":entry['open_late_night'],
            "open_weekends":entry['open_weekends'],
            "ward_name":entry['ward_name'].decode("string_escape").replace('\\', '')
            }

    def scrape_data(self):
        self.get_token()
        self.get_data()

