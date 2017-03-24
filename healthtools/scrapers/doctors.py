from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, CLOUDSEARCH_DOCTORS_ENDPOINT, S3_CONFIG
from datetime import datetime
import boto3


class DoctorsScraper(Scraper):
    '''
    Scraper for regular doctors on the medical board website
    '''

    def __init__(self):
        super(DoctorsScraper, self).__init__()
        self.site_url = SITES["DOCTORS"]
        self.fields = [
            "name", "reg_date", "reg_no", "postal_address", "qualifications",
            "speciality", "sub_speciality", "id",
        ]
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **CLOUDSEARCH_DOCTORS_ENDPOINT)
        self.s3 = boto3.client("s3", **S3_CONFIG)
        self.s3_key = "data/doctors.json"
        self.s3_historical_record_key = "data/archive/doctors-{}.json"
        self.delete_file = "delete_doctors.json"

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        date_obj = datetime.strptime(entry['reg_date'], "%Y-%m-%d")
        entry['reg_date'] = datetime.strftime(
            date_obj, "%Y-%m-%dT%H:%M:%S.000Z")
        entry["facility"] = entry["practice_type"] = "-"
        return {"id": entry["id"], "type": "add", "fields": entry}

    def generate_id(self):
        '''
        Generate an id for an entry
        '''
        _id = "415320151819" + str(self.document_id)
        return int(_id)
