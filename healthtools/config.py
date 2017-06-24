import os

# sites to be scraped
SITES = {
    "DOCTORS": "http://medicalboard.co.ke/online-services/retention/?currpage={}",
    "FOREIGN_DOCTORS": "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage={}",
    "CLINICAL_OFFICERS": "http://clinicalofficerscouncil.org/online-services/retention/?currpage={}",
    "TOKEN_URL": "http://api.kmhfl.health.go.ke/o/token/"
    }

AWS = {
    "aws_access_key_id": os.getenv("MORPH_AWS_ACCESS_KEY"),
    "aws_secret_access_key": os.getenv("MORPH_AWS_SECRET_KEY"),
    "region_name": os.getenv("MORPH_AWS_REGION", "eu-west-1"),
    "s3_bucket": os.getenv("S3_BUCKET", "cfa-healthtools-ke")
}

ES = {
    "host": os.getenv("ES_HOST", None),
    "port": os.getenv("ES_PORT", '9200'),
    "index": "healthtools"
}

SLACK = {
    "url": os.getenv("WEBHOOK_URL")
}

TEST_DIR = os.getcwd() + "/healthtools/tests"

BATCH = 5
HF_BATCH = 100  # batch for health facilities
