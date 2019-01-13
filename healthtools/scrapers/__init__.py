# import logging

from healthtools.scrapers.base_scraper import Scraper

from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_inpatient import NhifInpatientScraper
from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper

# log = logging.getLogger(__name__)
