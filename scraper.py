from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
if __name__ == "__main__":
    healthfacilities_scraper = HealthFacilitiesScraper()
    doctors_scraper = DoctorsScraper()
    foreign_doctors_scraper = ForeignDoctorsScraper()
    clinical_officers_scraper = ClinicalOfficersScraper()
    healthfacilities_scraper.scrape_data()
    # scraping you softly with these bots...
    clinical_officers_result = clinical_officers_scraper.scrape_site()
    doctors_result = doctors_scraper.scrape_site()
    if doctors_result:
        foreign_doctors_scraper.document_id = len(doctors_result) + 1
        foreign_docs_result = foreign_doctors_scraper.scrape_site()
