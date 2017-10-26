import time
import logging

from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, SMALL_BATCH_NHIF

log = logging.getLogger(__name__)

class NhifOutpatientScraper(Scraper):
    """
    Scraper for the NHIF accredited outpatient facilities
    """
    def __init__(self):
        super(NhifOutpatientScraper, self).__init__()
        self.site_url = SITES["NHIF_OUTPATIENT"]
        self.fields = ["code", "hospital", "nhif_branch", "id"]
        self.es_doc = "nhif-outpatient"
        self.data_key = "nhif_outpatient.json"
        self.data_archive_key = "archive/nhif_outpatient-{}.json"

    def scrape_page(self, tab_num, page_retries):
        """
        Get entries from each tab panel
        :param tab_num: the
        :return: tuple consisting of entries and records to be deleted
        """
        try:
            soup = self.make_soup(self.site_url)
            # tab numbers start from 4 in the website
            data = soup.find("div", {"id": "collapse-{}".format(tab_num + 3)})
            counties = data.find_all('a')
            # ignore the last link as it is a reference to the site url
            tabs = [(county["href"].split("#")[1], county.getText()) for county in counties[:-1]]
            results = []
            results_es = []
            for tab in tabs:
                table = data.find('div', {"id": tab[0]}).tbody

                if self.small_batch:
                    rows = table.find_all("tr")[:SMALL_BATCH_NHIF]
                else:
                    rows = table.find_all("tr")

                for row in rows:
                    columns = row.find_all("td")
                    columns = [text.text.strip() for text in columns]
                    columns.append(self.doc_id)

                    entry = dict(zip(self.fields, columns))
                    entry["county"] = tab[1]
                    meta, entry = self.elasticsearch_format(entry)
                    results_es.append(meta)
                    results_es.append(entry)
                    results.append(entry)

                    self.doc_id += 1
            return results, results_es
        except Exception as err:
            if page_retries >= 5:
                error = {
                    "ERROR": "Failed to scrape data from NHIH Outpatient page.",
                    "SOURCE": "scrape_page() url: %s" % tab_num,
                    "MESSAGE": str(err)
                }
                self.print_error(error)
                return err
            else:
                page_retries += 1
                log.warning("Try %d/5 has failed... \n%s \nGoing to sleep for %d seconds.",
                      page_retries, err, page_retries*5)
                time.sleep(page_retries*5)
                self.scrape_page(tab_num, page_retries)

    def set_site_pages_no(self):
        """
        Get the total number of pages
        """
        try:
            soup = self.make_soup(self.site_url)
            # get number of tabs to scrape
            self.site_pages_no = len(
                [tag.name for tag in soup.find("div", {"id": "collapse-s6"}).find("div", {"id": "accordion"})
                 if tag.name == 'div'])
        except Exception as err:
            error = {
                    "ERROR": "NHIF Outpatient: set_site_pages_no()",
                    "SOURCE": "url: %s" % self.site_url,
                    "MESSAGE": str(err)
                }
            self.print_error(error)
            return
