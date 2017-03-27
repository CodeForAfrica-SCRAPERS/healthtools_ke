from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper

if __name__ == "__main__":
    doctors_scraper = DoctorsScraper()
    foreign_doctors_scraper = ForeignDoctorsScraper()
    clinical_officers_scraper= ClinicalOfficersScraper()

    # scraping you softly with these bots...
    doctors_result = doctors_scraper.scrape_site()
    if doctors_result:
        foreign_docs_result = foreign_doctors_scraper.scrape_site()
    clinical_officers_result = clinical_officers_scraper.scrape_site()
