from scrapers.engine import DoctorsScraper, ForeignDoctorsScraper, ClinicalOfficersScraper

if __name__ == "__main__":
    doctors_scraper = DoctorsScraper()
    foreign_doctors_scraper = ForeignDoctorsScraper()
    clinical_officers_scraper= ClinicalOfficersScraper()

    # scraping you softly with these bots...
    doctors_scraper.scrape_site()
    foreign_doctors_scraper.scrape_site()
    clinical_officers_scraper.scrape_site()