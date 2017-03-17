from unittest import TestCase
from ..scraper import DoctorsScraper


class TestDoctorsScraper(TestCase):
    def setUp(self):
        self.doctors_scraper = DoctorsScraper()

    def test_it_gets_the_total_number_of_pages(self):
        self.doctors_scraper.get_total_number_of_pages()
        self.assertIsNotNone(self.doctors_scraper.num_pages_to_scrape)

    def test_it_scrapes_page(self):
        entries = self.doctors_scraper.scrape_page("http://medicalboard.co.ke/online-services/retention/?currpage=1")
        self.assertTrue(len(entries[0]) == 8)
