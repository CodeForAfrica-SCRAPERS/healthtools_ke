import os

# sites to be scraped
SITES = {
    "DOCTORS": "http://medicalboard.co.ke/online-services/retention/?currpage={}",
    "FOREIGN_DOCTORS": "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage={}",
    "CLINICAL_OFFICERS": "http://clinicalofficerscouncil.org/online-services/retention/?currpage={}",
    "TOKEN_URL": "http://api.kmhfl.health.go.ke/o/token/"
    }

AWS = {
    "aws_access_key_id": os.getenv("MORPH_AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("MORPH_AWS_SECRET_KEY"),
    "region_name": os.getenv("MORPH_AWS_REGION"),
    # Doctors document endpoint
    "cloudsearch_doctors_endpoint": "http://doc-cfa-healthtools-ke-doctors-m34xee6byjmzcgzmovevkjpffy.eu-west-1.cloudsearch.amazonaws.com/",
    # Clinical document endpoint
    "cloudsearch_cos_endpoint": "http://doc-cfa-healthtools-ke-cos-nhxtw3w5goufkzram4er7sciz4.eu-west-1.cloudsearch.amazonaws.com/",
    # Health facilities endpoint
    "cloudsearch_health_faciities_endpoint": "https://doc-health-facilities-ke-65ftd7ksxazyatw5fiv5uyaiqi.eu-west-1.cloudsearch.amazonaws.com",

    }
ES = {
    "host": os.getenv("ES_HOST"),
    "port": os.getenv("ES_PORT"),
    "user": os.getenv("ES_USER"),
    "pass": os.getenv("ES_PASS"),
    "index": "healthtools",
    "doctors_type": "doctors",
    "cos_type": "clinical-officers"
    }

TEST_DIR = os.getcwd() + "/healthtools/tests"
