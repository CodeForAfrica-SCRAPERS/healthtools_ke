import os

from unittest import TestCase

from healthtools.scrapers.base_scraper import Scraper
from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.scrapers.nhif_inpatient import NhifInpatientScraper
from healthtools.scrapers.nhif_outpatient import NhifOutpatientScraper
from healthtools.scrapers.nhif_outpatient_cs import NhifOutpatientCsScraper


class BaseTest(TestCase):
    """
    Base class for scraper unittests
    """
    def setUp(self):
        # get test data directory
        self.TEST_DIR = os.path.dirname(os.path.abspath(__file__)) + "/"

        # set up test scrapers
        self.base_scraper = Scraper()
        self.doctors_scraper = DoctorsScraper()
        self.foreign_doctors_scraper = ForeignDoctorsScraper()
        self.clinical_officers_scraper = ClinicalOfficersScraper()
        self.health_facilities_scraper = HealthFacilitiesScraper()
        self.nhif_inpatient_scraper = NhifInpatientScraper()
        self.nhif_outpatient_scraper = NhifOutpatientScraper()
        self.nhif_outpatient_cs_scraper = NhifOutpatientCsScraper()

        # set up test indices
        index = "healthtools-test"
        self.doctors_scraper.es_index = index
        self.foreign_doctors_scraper.es_index = index
        self.clinical_officers_scraper.es_index = index
        self.health_facilities_scraper.es_index = index
        self.nhif_inpatient_scraper.es_index = index
        self.nhif_outpatient_scraper.es_index = index
        self.nhif_outpatient_cs_scraper.es_index = index

        # set up tests data keys and archive keys
        self.doctors_scraper.data_key = "test/" + self.doctors_scraper.data_key
        self.doctors_scraper.data_archive_key = "test/" + self.doctors_scraper.data_archive_key
        self.foreign_doctors_scraper.data_key = "test/" + self.foreign_doctors_scraper.data_key
        self.foreign_doctors_scraper.data_archive_key = "test/" + self.foreign_doctors_scraper.data_archive_key
        self.clinical_officers_scraper.data_key = "test/" + self.clinical_officers_scraper.data_key
        self.clinical_officers_scraper.data_archive_key = "test/" + self.clinical_officers_scraper.data_archive_key
        self.health_facilities_scraper.data_key = "test/" + self.health_facilities_scraper.data_key
        self.health_facilities_scraper.data_archive_key = "test/" + self.health_facilities_scraper.data_archive_key
        self.nhif_inpatient_scraper.data_key = "test/" + self.nhif_inpatient_scraper.data_key
        self.nhif_inpatient_scraper.data_archive_key = "test/" + self.nhif_inpatient_scraper.data_archive_key
        self.nhif_outpatient_scraper.data_key = "test/" + self.nhif_outpatient_scraper.data_key
        self.nhif_outpatient_scraper.data_archive_key = "test/" + self.nhif_outpatient_scraper.data_archive_key
        self.nhif_outpatient_cs_scraper.data_key = "test/" + self.nhif_outpatient_cs_scraper.data_key
        self.nhif_outpatient_cs_scraper.data_archive_key = "test/" + self.nhif_outpatient_cs_scraper.data_archive_key
