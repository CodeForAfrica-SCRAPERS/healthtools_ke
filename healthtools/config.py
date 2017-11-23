import os

AWS = {
    "aws_access_key_id": os.getenv("MORPH_AWS_ACCESS_KEY"),
    "aws_secret_access_key": os.getenv("MORPH_AWS_SECRET_KEY"),
    "region_name": os.getenv("MORPH_AWS_REGION", "eu-west-1"),
    "s3_bucket": os.getenv("MORPH_S3_BUCKET", None)
}

ES = {
    "host": os.getenv("MORPH_ES_HOST", "127.0.0.1"),
    "port": os.getenv("MORPH_ES_PORT", 9200),
    "index": os.getenv("MORPH_ES_INDEX", "healthtools-dev")
}

SLACK = {
    "url": os.getenv("MORPH_WEBHOOK_URL")
}


SMALL_BATCH = 5  # No of pages from clinical officers, doctors and foreign doctors sites, scrapped in development mode
# No of records scraped from health-facilities sites in development mode
SMALL_BATCH_HF = 100
SMALL_BATCH_NHIF = 1  # No of nhif accredited facilities scraped in development mode

if AWS["s3_bucket"]:
    DATA_DIR = "data/"
else:
    # Where we archive the data in case of no s3 Bucket
    DATA_DIR = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))) + "/data/"
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
        os.mkdir(DATA_DIR + "archive")
        os.mkdir(DATA_DIR + "test")
        os.mkdir(DATA_DIR + "test/archive")

# sites to be scraped
SITES = {
    "DOCTORS": "https://medicalboard.co.ke/online-services/retention/?currpage={}",
    "FOREIGN_DOCTORS": "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage={}",
    "CLINICAL_OFFICERS": "http://clinicalofficerscouncil.org/online-services/retention/?currpage={}",
    "TOKEN_URL": "http://api.kmhfl.health.go.ke/o/token/",
    "NHIF_INPATIENT": "http://www.nhif.or.ke/healthinsurance/inpatientServices",
    "NHIF_OUTPATIENT": "http://www.nhif.or.ke/healthinsurance/outpatientServices",
    "NHIF_OUTPATIENT_CS": "http://www.nhif.or.ke/healthinsurance/medicalFacilities"
}

NHIF_SERVICES = ["inpatient", "outpatient", "outpatient-cs"]

# config logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": "ext://sys.stdout"
        }

    },

    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

