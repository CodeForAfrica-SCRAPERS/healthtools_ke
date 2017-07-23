# Healthtools Kenya

This is a suite of scrapers that retrieve actionable information for citizens to use.

They retrieve data from the following sites:

- Doctors: http://medicalboard.co.ke/online-services/retention/
- Foreign Doctors: http://medicalboard.co.ke/online-services/foreign-doctors-license-register
- Clinical Officers: http://clinicalofficerscouncil.org/online-services/retention/
- Health Facilities: http://kmhfl.health.go.ke
- NHIF accredited outpatient facilities for civil servants: http://www.nhif.or.ke/healthinsurance/medicalFacilities
- NHIF accredited inpatient facilities: http://www.nhif.or.ke/healthinsurance/inpatientServices
- NHIF accredited outpatient facilities: http://www.nhif.or.ke/healthinsurance/outpatientServices

They currently run on [morph.io](http://morph.io) but you are able to set it up on your own server.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

Clone the repo from Github by running `$ git clone git@github.com:CodeForAfrica-SCRAPERS/healthtools_ke.git`.

Change directory into the package `$ cd healthtools_ke`.

Install the dependencies by running `$ pip install requirements.txt`.

You can set the required environment variables like so

    $ export MORPH_AWS_REGION=<aws_region>
    $ export MORPH_AWS_ACCESS_KEY_ID=<aws_access_key_id>
    $ export MORPH_AWS_SECRET_KEY=<aws_secret_key>
    $ export MORPH_S3_BUCKET=<s3_bucket_name> # If not set, data will be archived locally in the project's folder in a folder called data
    $ export MORPH_ES_HOST=<elastic_search_host_endpoint> # Do not set this if you would like to use elastic search locally on your machine
    $ export MORPH_ES_PORT=<elastic_search_host_port> # Do not set this if you would like to use elastic search default port 9200
    $ export MORPH_WEBHOOK_URL=<slack_webhook_url> # Do not set this if you don't want to post error messages on Slack

#### Elasticsearch

All the data scraped is saved as an archive and into Elasticsearch for access by the [HealthTools API](https://github.com/CodeForAfricaLabs/HealthTools.API).

For linux and windows users, follow instructions from this [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html).

For mac users, run `$ brew install elasticsearch` on your terminal.

#### Slack

We use Slack notifications when the scrapers run into an error.

Set up Incoming Webhooks [here](https://slack.com/signin?redir=%2Fservices%2Fnew%2Fincoming-webhook) and set the global environment for the `MORPH_WEBHOOK_URL`

If you set up elasticsearch locally run it `$ elasticsearch`

You can now run the scrapers `$ python scraper.py` (It might take a while)

### Development

In development, instead of scraping entire websites, you can scrape only a small batch to ensure your scrapers are working as expected.

Set the `SMALL_BATCH`, `SMALL_BATCH_HF` (for health facilities scrapers), and `SMALL_BATCH_NHIF` (for NHIF scrapers) in the config file that will ensure the scraper doesn't scrape entire sites but just the number of pages that you would like it to scrape defined by this variable.

Use `$ python scraper.py small_batch` to run the scrapers.


## Tests

Use nosetests to run tests (with stdout) like this:
```$ nosetests --nocapture```

_**NB: <ake sure if you use elasticsearch locally, it's running**_
