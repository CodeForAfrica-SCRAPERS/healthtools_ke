# Healthtools Kenya

This is a suite of scrapers that retrieve medical officers data in Kenya and archive it.
They retrieve data from the following sites:

- Doctors: http://medicalboard.co.ke/online-services/retention/
- Foreign doctors: http://medicalboard.co.ke/online-services/foreign-doctors-license-register
- Clinical officers: http://clinicalofficerscouncil.org/online-services/retention/
- Health Facilities: http://kmhfl.health.go.ke

They currently run on morph.io.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

Clone the repo from Github by running `$ git clone git@github.com:CodeForAfrica-SCRAPERS/healthtools_ke.git`

Change directory into package `$ cd healthtools_ke`

Install the dependencies by running `$ pip install requirements.txt`

You can set the required environment variables like so

    $ export MORPH_AWS_REGION=<aws_region>
    $ export MORPH_AWS_ACCESS_KEY_ID=<aws_access_key_id>
    $ export MORPH_AWS_SECRET_KEY=<aws_secret_key>
    $ export MORPH_S3_BUCKET=<s3_bucket_name> # If not set, data will be archived locally in the project's folder in a folder called data
    $ export MORPH_ES_HOST=<elastic_search_host_endpoint> # Do not set this if you would like to use elastic search locally on your machine
    $ export MORPH_ES_PORT=<elastic_search_host_port> # Do not set this if you would like to use elastic search default port 9200
    $ export MORPH_WEBHOOK_URL=<slack_webhook_url> # Do not set this if you don't want to post error messages on Slack

**If you want to use elasticsearch locally on your machine use the following instructions to set it up**

For linux and windows users, follow instructions from this [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html)

For mac users run `brew install elasticsearch` on your terminal

**If you want to post messages on slack**

Set up `Incoming Webhooks` [here](https://slack.com/signin?redir=%2Fservices%2Fnew%2Fincoming-webhook) and set the global environment for the `MORPH_WEBHOOK_URL`

If you set up elasticsearch locally run it `$ elasticsearch`

You can now run the scrapers `$ python scraper.py` (It might take a while)

**FOR DEVELOPMENT PURPOSES**

Set the **BATCH** and **HF_BATCH** (for health facilities) in the config file that will ensure the scraper doesn't scrape entire sites but just the number of pages that you would like it to scrape defined by this variable.

use `$ python scraper.py small_batch` to run the scrapers


## Running the tests
_**make sure if you use elasticsearch locally, it's running**_

Use nosetests to run tests (with stdout) like this:
```$ nosetests --nocapture```
