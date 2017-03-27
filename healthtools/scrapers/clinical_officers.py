from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, AWS
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
            "cloudsearchdomain", **{
                "aws_access_key_id": AWS["aws_access_key_id"],
                "aws_secret_access_key": AWS["aws_secret_access_key"],
                "region_name": AWS["region_name"],
                "endpoint_url": AWS["cloudsearch_cos_endpoint"]
            })

        self.s3_key = "data/clinical_officers.json"
        self.s3_historical_record_key = "data/archive/clinical_officers-{}.json"
        self.delete_file = "data/delete_clinical_officers.json"

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
