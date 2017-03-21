from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, CLOUDSEARCH_DOCTORS_ENDPOINT, S3_CONFIG
import boto3


class ForeignDoctorsScraper(Scraper):
    '''
    Scraper for foreign doctors on the medical board website
    '''

    def __init__(self):
        super(ForeignDoctorsScraper, self).__init__()
        self.site_url = SITES["FOREIGN_DOCTORS"]
        self.fields = [
            "name", "reg_no", "postal_address", "qualifications",
            "facility", "practice_type", "id"
        ]
        self.cloudsearch = boto3.client(
            "cloudsearchdomain", **CLOUDSEARCH_DOCTORS_ENDPOINT)
        self.s3 = boto3.client("s3", **S3_CONFIG)
        self.s3_key = "foreign_doctors.json"

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        entry["reg_date"] = "0000-01-01T00:00:00.000Z"
        entry["reg_no"] = entry["speciality"] = entry["sub_speciality"] = "-"
        return {"id": entry["id"], "type": "add", "fields": entry}
