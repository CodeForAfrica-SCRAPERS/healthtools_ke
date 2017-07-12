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

        self._type = "doctors"
        self.s3_key = "data/foreign_doctors.json"
        self.s3_historical_record_key = "data/archive/foreign_doctors-{}.json"
        self.delete_file = "data/delete_foreign_doctors.json"

    def format_for_elasticsearch(self, entry):
        """
        Format entry into elasticsearch ready document
        :param entry: the data to be formatted
        :return: dictionaries of the entry's metadata and the formatted entry
        """
        entry["reg_date"] = "0000-01-01T00:00:00.000Z"
        entry["reg_no"] = entry["speciality"] = entry["sub_speciality"] = "-"
        # all bulk data need meta data describing the data
        meta_dict = {
            "index": {
                "_index": ES["index"],
                "_type": self._type,
                "_id": entry["id"]
                }
            }
        return meta_dict, entry
