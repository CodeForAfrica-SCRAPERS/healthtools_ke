import unittest
from healthtools_ke.scrapers.engine import DoctorsScraper, ForeignDoctorsScraper, ClinicalOfficersScraper
import json


class TestDoctorsScraper(unittest.TestCase):
    def setUp(self):
        self.doctors_scraper = DoctorsScraper()
        self.foreign_doctors_scraper = ForeignDoctorsScraper()
        self.clinical_officers_scraper= ClinicalOfficersScraper()

    def test_it_gets_the_total_number_of_pages(self):
        self.doctors_scraper.get_total_number_of_pages()
        self.assertIsNotNone(self.doctors_scraper.num_pages_to_scrape)

    def test_it_scrapes_doctors_page(self):
        entries = self.doctors_scraper.scrape_page(
            "http://medicalboard.co.ke/online-services/retention/?currpage=1")
        self.assertTrue(len(entries[0]["fields"]) == 10)

    def test_it_scrapes_foreign_doctors_page(self):
        entries = self.foreign_doctors_scraper.scrape_page(
            "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage=1")
        self.assertTrue(len(entries[0]["fields"]) == 10)

    def test_it_scrapes_clinical_officers_page(self):
        entries = self.clinical_officers_scraper.scrape_page(
            "http://clinicalofficerscouncil.org/online-services/retention/?currpage=1")
        self.assertTrue(len(entries[0]["fields"]) == 7)

    def test_it_scrapes_whole_doctors_site(self):
        all_entries = self.doctors_scraper.scrape_site()
        self.assertTrue(len(all_entries) > 0)

    def test_it_scrapes_whole_foreign_doctors_site(self):
        all_entries = self.foreign_doctors_scraper.scrape_site()
        self.assertTrue(len(all_entries) > 0)

    def test_it_scrapes_whole_clinical_officers_site(self):
        all_entries = self.clinical_officers_scraper.scrape_site()
        self.assertTrue(len(all_entries) > 0)

    def test_doctors_scraper_uploads_to_cloudsearch(self):
        with open("tests/dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
            response = self.doctors_scraper.upload_data(data)
            self.assertEqual(response.get('status'), "success")

    def test_foreign_doctors_scraper_uploads_to_cloudsearch(self):
        with open("tests/dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
            response = self.foreign_doctors_scraper.upload_data(data)
            self.assertEqual(response.get('status'), "success")

    def test_clinical_officers_scraper_uploads_to_cloudsearch(self):
        with open("tests/dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
            response = self.clinical_officers_scraper.upload_data(data)
            self.assertEqual(response.get('status'), "success")

    def test_doctors_scraper_archives_to_s3(self):
        with open("tests/dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
            self.doctors_scraper.archive_data(data)
        uploaded_data = self.doctors_scraper.s3.get_object(
            Bucket="cfa-healthtools-ke",
            Key=self.doctors_scraper.s3_key
        )['Body'].read()
        self.assertEqual(uploaded_data, data)
        self.doctors_scraper.s3.delete_object(
            Bucket="cfa-healthtools-ke",
            Key=self.doctors_scraper.s3_key)

    def test_foreign_doctors_scraper_archives_to_s3(self):
        with open("tests/dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
            self.foreign_doctors_scraper.archive_data(data)
        uploaded_data = self.foreign_doctors_scraper.s3.get_object(
            Bucket="cfa-healthtools-ke",
            Key=self.foreign_doctors_scraper.s3_key
        )['Body'].read()
        self.assertEqual(uploaded_data, data)
        self.foreign_doctors_scraper.s3.delete_object(
            Bucket="cfa-healthtools-ke",
            Key=self.foreign_doctors_scraper.s3_key)

    def test_clinical_officers_scraper_archives_to_s3(self):
        with open("tests/dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
            self.clinical_officers_scraper.archive_data(data)
        uploaded_data = self.clinical_officers_scraper.s3.get_object(
            Bucket="cfa-healthtools-ke",
            Key=self.clinical_officers_scraper.s3_key
        )['Body'].read()
        self.assertEqual(uploaded_data, data)
        self.clinical_officers_scraper.s3.delete_object(
            Bucket="cfa-healthtools-ke",
            Key=self.clinical_officers_scraper.s3_key)
