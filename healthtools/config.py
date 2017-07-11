import os

# sites to be scraped
SITES = {
    "DOCTORS": "http://medicalboard.co.ke/online-services/retention/?currpage={}",
    "FOREIGN_DOCTORS": "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage={}",
    "CLINICAL_OFFICERS": "http://clinicalofficerscouncil.org/online-services/retention/?currpage={}",
    "TOKEN_URL": "http://api.kmhfl.health.go.ke/o/token/",
    "NHIF-MEDICAL-FACILITIES": "http://www.nhif.or.ke/healthinsurance/medicalFacilities",
    "NHIF-INPATIENT": "http://www.nhif.or.ke/healthinsurance/inpatientServices"
}

AWS = {
    "aws_access_key_id": os.getenv("MORPH_AWS_ACCESS_KEY"),
    "aws_secret_access_key": os.getenv("MORPH_AWS_SECRET_KEY"),
    "region_name": os.getenv("MORPH_AWS_REGION", "eu-west-1"),
    "s3_bucket": os.getenv("MORPH_S3_BUCKET", None)
}

ES = {
    "host": os.getenv("MORPH_ES_HOST", "127.0.0.1"),
    "port": os.getenv("MORPH_ES_PORT", 9200),
    "index": os.getenv("MORPH_ES_INDEX", "healthtools-ke")
}

SLACK = {
    "url": os.getenv("MORPH_WEBHOOK_URL")
}

TEST_DIR = os.getcwd() + "/healthtools/tests"

SMALL_BATCH = 5  # No of pages from clinical officers, doctors and foreign doctors sites, scrapped in development mode
SMALL_BATCH_HF = 100  # No of records scraped from health-facilities sites in development mode
SMALL_BATCH_NHIF = 10  # No of nhif accredited facilities scraped in development mode

DATA_DIR = os.getcwd() + "/data/"
