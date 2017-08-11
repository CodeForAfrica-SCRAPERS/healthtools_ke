from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES


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
        self.es_doc = "doctors"
        self.data_key = "foreign_doctors.json"
        self.data_archive_key = "archive/foreign_doctors-{}.json"

    def format_for_elasticsearch(self, entry):
        """
        Format entry into elasticsearch ready document
        :param entry: the data to be formatted
        :return: dictionaries of the entry's metadata and the formatted entry
        """
        entry["reg_date"] = "0000-01-01T00:00:00.000Z"
        entry["reg_no"] = entry["speciality"] = entry["sub_speciality"] = "-"
        entry["doctor_type"] = "foreign_doctor"

        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": self.es_index,
                "_type": self.es_doc,
                "_id": entry["id"]
            }
        }
        return meta_dict, entry
