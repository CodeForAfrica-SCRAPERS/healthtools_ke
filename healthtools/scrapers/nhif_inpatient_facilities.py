from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, ES, SMALL_BATCH_NHIF


class NhifInpatientScraper(Scraper):
    """Scraper for the NHIF accredited inpatient facilities"""
    def __init__(self):
        super(NhifInpatientScraper, self).__init__()
        self.site_url = SITES["NHIF-INPATIENT"]
        self.fields = ["hospital", "postal_addr", "beds", "branch", "category", "id"]
        self._type = "nhif-inpatient"
        self.s3_key = "data/nhif_accredited_inpatient_facilities.json"
        self.s3_historical_record_key = "data/archive/nhif_accredited_inpatient_facilities-{}.json"
        self.delete_file = "data/delete_nhif_accredited_inpatient_facilities.json"

    def scrape_page(self, tab_num):
        """
        Get entries from each tab panel
        :param tab_num: the
        :return: tuple consisting of entries and records to be deleted
        """
        try:
            soup = self.make_soup(self.site_url)
            regions = soup.findAll("a", {"data-toggle": "tab"})
            tabs = [(region["href"].split("#")[1], region.getText()) for region in regions]
            entries = []
            delete_batch = []
            for tab in tabs:
                table = soup.find("div", {"id": tab[0]}).tbody
                if self.small_batch:
                    rows = table.find_all("tr")[:SMALL_BATCH_NHIF]
                else:
                    rows = table.find_all("tr")
                for row in rows:
                    columns = row.find_all("td")
                    columns = [text.text.strip() for text in columns]
                    columns.append(self.document_id)

                    entry = dict(zip(self.fields, columns))
                    # nairobi region isn't included correctly
                    if tab[1] == "":
                        entry["region"] = "Nairobi Region"
                    else:
                        entry["region"] = tab[1]
                    meta, entry = self.format_for_elasticsearch(entry)
                    entries.append(meta)
                    entries.append(entry)

                    delete_batch.append({
                        "delete": {
                            "_index": ES["index"],
                            "_type": self._type,
                            "_id": entry["id"]
                        }
                    })
                    self.document_id += 1
            return entries, delete_batch
        except Exception as err:
            if self.retries >= 5:
                self.print_error("ERROR - Failed to scrape data from tab - {} - {}".format(tab_num, str(err)))
                return err
            else:
                self.retries += 1
                self.scrape_page(tab_num)

    def get_total_number_of_pages(self):
        """
        Get the total number of pages
        """
        try:
            soup = self.make_soup(self.site_url)
            # get number of tabs to scrape
            self.num_pages_to_scrape = len(
                [tag.name for tag in soup.find("div", {"class": "tab-content"}) if tag.name == 'div'])
        except Exception as err:
            self.print_error("ERROR - get_total_page_numbers() - url: {} - err: {}".format(self.site_url, str(err)))
            return
