import os

# sites to be scraped
SITES = {
    "DOCTORS": "http://medicalboard.co.ke/online-services/retention/",
    "FOREIGN_DOCTORS": "http://medicalboard.co.ke/online-services/foreign-doctors-license-register",
    "CLINICAL_OFFICERS": "http://clinicalofficerscouncil.org/online-services/retention/",
}

# Doctors document endpoint
CLOUDSEARCH_DOCTORS_ENDPOINT = {
    "endpoint_url" : "http://doc-cfa-healthtools-ke-doctors-m34xee6byjmzcgzmovevkjpffy.eu-west-1.cloudsearch.amazonaws.com/",
    "aws_access_key_id": os.getenv("MORPH_AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("MORPH_AWS_SECRET_KEY"),
    "region_name": os.getenv("MORPH_AWS_REGION")
}

# Clinical document endpoint
CLOUDSEARCH_COS_ENDPOINT = {
    "endpoint_url" : "http://doc-cfa-healthtools-ke-doctors-m34xee6byjmzcgzmovevkjpffy.eu-west-1.cloudsearch.amazonaws.com/",
    "aws_access_key_id": os.getenv("MORPH_AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("MORPH_AWS_SECRET_KEY"),
    "region_name": os.getenv("MORPH_AWS_REGION")
}
