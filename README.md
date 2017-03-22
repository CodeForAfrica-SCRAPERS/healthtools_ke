# Healthtools Kenya

This is a suite of scrapers that retrieve medical officers data in Kenya and archive it.
They retrieve data from the following sites:

- Doctors: http://medicalboard.co.ke/online-services/retention/
- Foreign doctors: http://medicalboard.co.ke/online-services/foreign-doctors-license-register
- Clinical officers: http://clinicalofficerscouncil.org/online-services/retention/

They currently run on morph.io.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installing

Clone the repo from Github by running `$ git clone git@github.com:CodeForAfrica-SCRAPERS/healthtools_ke.git`

Change directory into package `$ cd healthtools_ke`

Install the dependencies by running `$ pip install requirements.txt`

You can set the required environment variables like so
```
$ export MORPH_AWS_REGION=<aws_region>
$ export MORPH_AWS_ACCESS_KEY_ID= <aws_access_key_id>
$ export MORPH_AWS_SECRET_KEY= <aws_secret_key>
```

You can now run the scrapers `$ python scraper.py` (It might take a while and you might need to change the endpoints in config.py if you haven't authorization for them)

## Running the tests

Use nosetests to run tests (with stdout) like this:
```$ nosetests --nocapture```
