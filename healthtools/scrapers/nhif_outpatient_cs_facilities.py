from healthtools.scrapers.base_scraper import Scraper
from healthtools.config import SITES, ES, SMALL_BATCH_NHIF


class NhifOutpatientCsScraper(Scraper):
    """Scraper for the NHIF outpatient facilities extended to civil servants"""
    def __init__(self):
        super(NhifOutpatientCsScraper, self).__init__()
        self.site_url = SITES["NHIF-OUTPATIENT_CS"]
        self._type = "nhif-outpatient-cs"
        self.fields = ["code", "hospital", "nhif_branch", "job_group", "cover", "id"]
        self.s3_key = "data/nhif_outpatient_cs_facilities.json"
        self.s3_historical_record_key = "data/archive/nhif_outpatient_cs_facilities-{}.json"
        self.delete_file = "data/delete_nhif_outpatient_cs_facilities.json"

    def scrape_page(self, tab_num):
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
            entries = []
            delete_batch = []
            for tab in tabs:
                table = data.find('div', {"id": tab[0]}).tbody
                if self.small_batch:
                    rows = table.find_all("tr")[:SMALL_BATCH_NHIF]
                else:
                    rows = table.find_all("tr")
                for row in rows:
                    columns = row.find_all("td")
                    columns = [text.text.strip() for text in columns]
                    columns.append(self.document_id)

                    entry = dict(zip(self.fields, columns))
                    entry["county"] = tab[1]
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
                [tag.name for tag in soup.find("div", {"id": "accordion"}) if tag.name == 'div'])
        except Exception as err:
            self.print_error("ERROR - get_total_page_numbers() - url: {} - err: {}".format(self.site_url, str(err)))
            return
