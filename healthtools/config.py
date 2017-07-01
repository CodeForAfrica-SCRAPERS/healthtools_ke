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
    "s3_bucket": os.getenv("MORPH_S3_BUCKET", None)
}

ES = {
    "host": os.getenv("MORPH_ES_HOST", "127.0.0.1"),
    "port": os.getenv("MORPH_ES_PORT", 9200),
    "index": os.getenv("MORPH_ES_INDEX", "healthtools-ke")
}

TEST_DIR = os.getcwd() + "/healthtools/tests"
