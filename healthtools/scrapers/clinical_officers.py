from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, ES
from datetime import datetime


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

        self._type = "clinical-officers"
        self.s3_key = "data/clinical_officers.json"
        self.s3_historical_record_key = "data/archive/clinical_officers-{}.json"

    def format_for_elasticsearch(self, entry):
        """
        Format entry into elasticsearch ready document
        :param entry: the data to be formatted
        :return: dictionaries of the entry's metadata and the formatted entry
        """
        try:
            date_obj = datetime.strptime(entry["reg_date"], "%Y-%m-%d")
        except:
            date_obj = datetime.strptime(entry["reg_date"], "%d-%m-%Y")
        entry["reg_date"] = datetime.strftime(
            date_obj, "%Y-%m-%dT%H:%M:%S.000Z")
        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": ES["index"],
                "_type": self._type,
                "_id": entry["id"]
                }
            }
        return meta_dict, entry
