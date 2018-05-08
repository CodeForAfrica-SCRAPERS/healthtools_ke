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
        self.es_doc = "clinical-officers"
        self.data_key = "clinical_officers.json"
        self.data_archive_key = "archive/clinical_officers-{}.json"

    def elasticsearch_format(self, entry):
        """
        Format entry into elasticsearch ready document
        :param entry: the data to be formatted
        :return: dictionaries of the entry's metadata and the formatted entry
        """
        date_obj = self.parse_date(entry["reg_date"])
        entry["reg_date"] = datetime.strftime(date_obj, "%Y-%m-%dT%H:%M:%S.000Z")
        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": self.es_index,
                "_type": self.es_doc,
                "_id": entry["id"]
            }
        }
        return meta_dict, entry
