from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, CLOUDSEARCH_COS_ENDPOINT, S3_CONFIG
from datetime import datetime
import boto3


class ClinicalOfficersScraper(Scraper):
    '''
    Scraper for the clinical officers council website
    '''

    def __init__(self):
        super(ClinicalOfficersScraper, self).__init__()
        self.site_url = SITES["CLINICAL_OFFICERS"]
        self.fields = [
            "name", "reg_date", "reg_no", "valid_dates",
            "address", "qualifications", "id",
        ]
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **CLOUDSEARCH_COS_ENDPOINT)
        self.s3 = boto3.client("s3", **S3_CONFIG)
        self.s3_key = "clinical_officers.json"

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        date_obj = datetime.strptime(entry['reg_date'], "%d-%m-%y %H:%M")
        entry['reg_date'] = datetime.strftime(
            date_obj, "%Y-%m-%dT%H:%M:%S.000Z")
        return {"id": entry["id"], "type": "add", "fields": entry}

    def generate_id(self):
        '''
        Generate an id for an entry
        '''
        _id = "31291493112" + str(self.document_id)
        return int(_id)
