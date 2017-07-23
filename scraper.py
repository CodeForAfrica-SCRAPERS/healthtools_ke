from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_inpatient import NhifInpatientScraper
from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper

if __name__ == "__main__":

    # Initialize the Scrapers
    doctors_scraper = DoctorsScraper()
    foreign_doctors_scraper = ForeignDoctorsScraper()
    clinical_officers_scraper = ClinicalOfficersScraper()
    healthfacilities_scraper = HealthFacilitiesScraper()

    nhif_inpatient_scraper = NhifInpatientScraper()
    nhif_outpatient_scraper = NhifOutpatientScraper()
    nhif_outpatient_cs_scraper = NhifOutpatientCsScraper()

    # Run the scrapers

    '''
    Doctors Scraper
    ---------------
    Doctors are a combination of local and foreign doctors. If the local
    doctors' scraper fails, we shouldn't scrape the foreign doctors.
    '''
    doctors_result = doctors_scraper.scrape_site()
    if doctors_result:
        foreign_doctors_scraper.document_id = len(doctors_result)
        foreign_docs_result = foreign_doctors_scraper.scrape_site()

    '''
    Clinical Officers Scraper
    -------------------------
    Scrapes the clinical officers website.
    '''
    clinical_officers_result = clinical_officers_scraper.scrape_site()

    '''
    Health Facilities Scraper
    -------------------------
    Scrapes the government's Kenya Health Facilities Master List.
    '''
    healthfacilities_result = healthfacilities_scraper.scrape_data()

    '''
    NHIF Scraper
    -------------------------
    Scrapes the NHIF website for accredited hospital / facitilities.
    '''
    nhif_inpatient_result = nhif_inpatient_scraper.scrape_site()
    nhif_outpatient_result = nhif_outpatient_scraper.scrape_site()
    nhif_outpatient_cs_result = nhif_outpatient_cs_scraper.scrape_site()
