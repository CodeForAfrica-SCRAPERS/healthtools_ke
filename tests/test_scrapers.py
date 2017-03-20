from unittest import TestCase
from healthtools_ke.scraper import DoctorsScraper, ForeignDoctorsScraper
import json

class TestDoctorsScraper(TestCase):
    def setUp(self):
        self.doctors_scraper = DoctorsScraper()
        self.foreign_doctors_scraper = ForeignDoctorsScraper()

    def test_it_gets_the_total_number_of_pages(self):
        self.doctors_scraper.get_total_number_of_pages()
        self.assertIsNotNone(self.doctors_scraper.num_pages_to_scrape)

    def test_it_scrapes_doctors_page(self):
        entries = self.doctors_scraper.scrape_page("http://medicalboard.co.ke/online-services/retention/?currpage=1")
        self.assertTrue(len(entries[0]["fields"]) == 10)

    def test_it_scrapes_foreign_doctors_page(self):
        entries = self.foreign_doctors_scraper.scrape_page("http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage=1")
        self.assertTrue(len(entries[0]["fields"]) == 10)

    def test_it_scrapes_whole_doctors_site(self):
        self.doctors_scraper.scrape_site()

    def test_it_scrapes_whole_foreign_doctors_site(self):
        self.foreign_doctors_scraper.scrape_site()