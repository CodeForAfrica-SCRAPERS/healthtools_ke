from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES
from datetime import datetime
import logging

class DoctorsScraper(Scraper):
    '''
    Scraper for regular doctors on the medical board website
    '''

    def __init__(self):
        super(DoctorsScraper, self).__init__()
        log = logging.getLogger('__main__')
        self.site_url = SITES["DOCTORS"]
        self.fields = [
            "name", "reg_date", "reg_no", "postal_address", "qualifications",
            "speciality", "sub_speciality", "id",
        ]
        self.es_doc = "doctors"
        self.data_key = "doctors.json"
        self.data_archive_key = "archive/doctors-{}.json"

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
        entry["facility"] = entry["practice_type"] = "-"
        entry["doctor_type"] = "local_doctor"
        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": self.es_index,
                "_type": self.es_doc,
                "_id": entry["id"]
            }
        }
        return meta_dict, entry
