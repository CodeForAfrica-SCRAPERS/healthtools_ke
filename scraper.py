import json
from time import time, gmtime, strftime
import logging
import logging.config

from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.base_scraper import Scraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_inpatient import NhifInpatientScraper
from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper
from healthtools.config import LOGGING


def setup_logging(default_level=logging.INFO):
    """
    Setup logging configuration
    """
    try:
        logging.config.dictConfig(LOGGING)
    except Exception as ex:
        logging.basicConfig(level=default_level)



logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
import time

scraper_id = 0

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
    start_execution = time()

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

    total_runtime = time() - start_execution
    m, s = divmod(total_runtime, 60)
    h, m = divmod(m, 60)
    time_taken = "%dhr:%02dmin:%02dsec" % (
        h, m, s) if total_runtime > 60 else '{} seconds'.format(total_runtime)

    scraping_statistics = {
        'Total time Scraping took': time_taken,
        'Last successfull Scrape was': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        'doctors_scraper': doctors_scraper.stat_log,
        'foreign_doctors_scraper': foreign_doctors_scraper.stat_log,
        'clinical_officers_scraper': clinical_officers_scraper.stat_log,
        'healthfacilities_scraper': healthfacilities_scraper.stat_log,
        'nhif_inpatient_scraper': nhif_inpatient_scraper.stat_log,
        'nhif_outpatient_cs_scraper': nhif_outpatient_cs_scraper.stat_log,
        'nhif_outpatient_scraper': nhif_outpatient_scraper.stat_log,
    }

    # initialize a scraper to index scraper statistics
    scraper_stats = Scraper()
    scraper_stats.data_key = "stats.json"
    scraper_stats.data_archive_key = "stats/stats-{}.json"
    scraper_stats.archive_data(json.dumps(scraping_statistics))
    # record end time
    end_time = time.time()
    timeSent = (end_time - start_time) / (60)
    if(response_time_in_minutes >= 30):
        log.warning('Scraper: {} ran for about {} minutes'.format(scraper_id, timeSent))

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
        log.warning('Scraper: {} is running for more than 30 minutes'.format(scraper_id))

