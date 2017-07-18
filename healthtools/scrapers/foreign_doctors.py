from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, ES


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
        self.s3_key = "data/foreign_doctors.json"
        self.s3_historical_record_key = "data/archive/foreign_doctors-{}.json"
        self.doctor_type = "foreign_doctor"

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
                "_index": ES["index"],
                "_type": "doctors",
                "_id": entry["id"]
            }
        }
        return meta_dict, entry
