from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, AWS
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
            "cloudsearchdomain", **{
                "aws_access_key_id": AWS["aws_access_key_id"],
                "aws_secret_access_key": AWS["aws_secret_access_key"],
                "region_name": AWS["region_name"],
                "endpoint_url": AWS["cloudsearch_doctors_endpoint"]
            })
        self.s3_key = "data/foreign_doctors.json"
        self.s3_historical_record_key = "data/archive/foreign_doctors-{}.json"
        self.delete_file = "data/delete_foreign_doctors.json"

    def format_for_cloudsearch(self, entry):
        '''
        Format entry into cloudsearch ready document
        '''
        entry["reg_date"] = "0000-01-01T00:00:00.000Z"
        entry["reg_no"] = entry["speciality"] = entry["sub_speciality"] = "-"
        return {"id": entry["id"], "type": "add", "fields": entry}
