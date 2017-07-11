from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_accredited_facilities import NhifAccreditedFacilitiesScraper
from healthtools.scrapers.nhif_accredited_inpatient_facilities import NhifInpatientScraper

if __name__ == "__main__":

    # Initialize the Scrapers
    doctors_scraper = DoctorsScraper()
    foreign_doctors_scraper = ForeignDoctorsScraper()
    clinical_officers_scraper = ClinicalOfficersScraper()
    healthfacilities_scraper = HealthFacilitiesScraper()
    nhif_accredited_facilities = NhifAccreditedFacilitiesScraper()
    nhif_accredited_inpatient = NhifInpatientScraper()

    # scraping you softly with these bots...
    nhif_accredited_inpatient_result = nhif_accredited_inpatient.scrape_site()
    nhif_accredited_result = nhif_accredited_facilities.scrape_site()
    doctors_result = doctors_scraper.scrape_site()
    if doctors_result:
        foreign_doctors_scraper.document_id = len(doctors_result) + 1
        foreign_docs_result = foreign_doctors_scraper.scrape_site()
    clinical_officers_result = clinical_officers_scraper.scrape_site()
    healthfacilities_result = healthfacilities_scraper.scrape_data()
