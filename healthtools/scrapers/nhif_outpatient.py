from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper
from healthtools.config import SITES, ES, SMALL_BATCH_NHIF


class NhifOutpatientScraper(NhifOutpatientCsScraper):
    """Scraper for the NHIF accredited outpatient facilities"""
    def __init__(self):
        super(NhifOutpatientScraper, self).__init__()
        self.site_url = SITES["NHIF-OUTPATIENT"]
        self.fields = ["code", "hospital", "nhif_branch", "id"]
        self._type = "nhif-outpatient"
        self.s3_key = "data/nhif_outpatient.json"
        self.s3_historical_record_key = "data/archive/nhif_outpatient-{}.json"
        self.delete_file = "data/delete_nhif_outpatient.json"

    def get_total_number_of_pages(self):
        """
        Get the total number of pages
        """
        try:
            soup = self.make_soup(self.site_url)
            # get number of tabs to scrape
            self.num_pages_to_scrape = len(
                [tag.name for tag in soup.find("div", {"id": "collapse-s6"}).find("div", {"id": "accordion"})
                 if tag.name == 'div'])
        except Exception as err:
            self.print_error("ERROR - get_total_page_numbers() - url: {} - err: {}".format(self.site_url, str(err)))
            return
