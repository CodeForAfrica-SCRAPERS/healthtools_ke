from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.config import SITES


class NhifOutpatientCsScraper(NhifOutpatientScraper):
    """Scraper for the NHIF outpatient facilities extended to civil servants"""
    def __init__(self):
        super(NhifOutpatientCsScraper, self).__init__()
        self.site_url = SITES["NHIF_OUTPATIENT_CS"]
        self.fields = ["code", "hospital", "nhif_branch", "job_group", "cover", "id"]
        self.es_doc = "nhif-outpatient-cs"
        self.data_key = "nhif_outpatient_cs.json"
        self.data_archive_key = "archive/nhif_outpatient_cs-{}.json"

    def set_site_pages_no(self):
        """
        Get the total number of pages
        """
        self.site_pages_no = 1
        try:
            soup = self.make_soup(self.site_url)
            # get number of tabs to scrape
            self.site_pages_no = len(
                [tag.name for tag in soup.find("div", {"id": "accordion"}) if tag.name == 'div'])
        except Exception as err:
            error = {
                    "ERROR": "NHIF Outpatient CS: set_site_pages_no()",
                    "SOURCE": "url: %s" % self.site_url,
                    "MESSAGE": str(err)
                }
            self.print_error(error)
            return
