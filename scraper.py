import logging
from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_inpatient import NhifInpatientScraper
from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper


logging.basicConfig(level=logging.INFO)
import time

scraper_id = 0
# error message for 
error = {
    "ERROR": "scrapers()",
    "SOURCE": "Scraper time tracker",
    "MESSAGE": ""
}
# create a scrapper to log error message 
scraper = Scraper()

def scrapers():
    '''
    Function to run every scraper
    '''
    # record the start time
    start_time = time.time()
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

    doctors_result = doctors_scraper.run_scraper()
    if doctors_result:
        foreign_doctors_scraper.doc_id = len(doctors_result)
        foreign_docs_result = foreign_doctors_scraper.run_scraper()

    '''
    Clinical Officers Scraper
    -------------------------
    Scrapes the clinical officers website.
    '''
    clinical_officers_result = clinical_officers_scraper.run_scraper()

    '''
    Health Facilities Scraper
    -------------------------
    Scrapes the government's Kenya Health Facilities Master List.
    '''
    healthfacilities_result = healthfacilities_scraper.run_scraper()

    '''
    NHIF Scraper
    -------------------------
    Scrapes the NHIF website for accredited hospital / facitilities.
    '''
    nhif_inpatient_result = nhif_inpatient_scraper.run_scraper()
    nhif_outpatient_result = nhif_outpatient_scraper.run_scraper()
    nhif_outpatient_cs_result = nhif_outpatient_cs_scraper.run_scraper()

    # record end time
    end_time = time.time()
    response_time_in_minutes = (end_time - start_time) / (60)
    if(response_time_in_minutes >= 30):
        error['MESSAGE'] = 'Scraper: {} took about {} minutes'.format(scraper_id, response_time_in_minutes)
        scraper.print_error(error)

if __name__ == "__main__":
    import multiprocessing
    # Start the scrapers
    scraping = multiprocessing.Process(target=scrapers)
    scraping.start()
    scraping.join(30*60)

    # log error if scraping is still running after 30 minutes
    if scraping.is_alive():
        # create a random Id for this scrap instance
        import random
        scraper_id = random.randint(1, 100000)
        error['MESSAGE'] = 'Scraper: {} is taking more than 30 minutes'.format(scraper_id)
        scraper.print_error(error)
