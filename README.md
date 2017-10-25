# HealthTools Kenya Scraper

This is a suite of scrapers that retrieve actionable information for citizens to use. All the data scraped by this is accessible through our [HealthTools API](https://github.com/CodeForAfricaLabs/HealthTools.API).

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

### How the Scrapers Work

To get the data we follow a couple of steps:

**1. Start by scraping the websites:** This is done in most cases using beautiful soup.  
**2. Elasticsearch update:** Replace data on elasticsearch with the new one. We only delete the documents after succesful   completion of the scraping and not before. In the doctors' case, because we pull together foreign and local doctors, we won't update elasticsearch until both have been scraped succesfully.  
**3. Archive the data:** We archive the data in a "latest" .json file so that the url doesn't have to change to get the latest version in a "dump" format. A date-stamped archive is also stored as we later intend to do some analysis on the changes over time.


Should the scraper fail at any of these points, we print out an error, and if set up, a Slack notification is sent.


### Installing

Clone the repo from Github by running `$ git clone git@github.com:CodeForAfrica-SCRAPERS/healthtools_ke.git`.

Change directory into the package `$ cd healthtools_ke`.

Install the dependencies by running `$ pip install -r requirements.txt`.

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

#### Error Handling

As with anything beyond our control (the websites we are scraping), we try to catch all errors and display useful and actionable information about them.

As such, we capture the following details:

- Timestamp
- Machine name
- Module / Scraper name + function name
- Error message

This data is printed in terminal in the following way:

    [ Timestamp ] { Module / Scraper Name }
    [ Timestamp ] Scraper has started.
    [ Timestamp ] ERROR: { Module / Scraper Name } / { function name }
    [ Timestamp ] ERROR: { Error message }


We also provide a Slack notification option detailed below.

*Slack Notification:*

We use Slack notifications when the scrapers run into an error.

Set up Incoming Webhooks [here](https://slack.com/signin?redir=%2Fservices%2Fnew%2Fincoming-webhook) and set the global environment for the `MORPH_WEBHOOK_URL`

If you set up elasticsearch locally run it `$ elasticsearch`

You can now run the scrapers `$ python scraper.py` (It might take a while)


### Development

In development, instead of scraping entire websites, you can scrape only a small batch to ensure your scrapers are working as expected.

Set the `SMALL_BATCH`, `SMALL_BATCH_HF` (for health facilities scrapers), and `SMALL_BATCH_NHIF` (for NHIF scrapers) in the config file that will ensure the scraper doesn't scrape entire sites but just the number of pages that you would like it to scrape defined by this variable.

Usage `$ python scraper.py --help`
    Example `$ python scraper.py --small-batch --scraper doctors clinical_officers ` to run the scrapers.


## Tests

Use nosetests to run tests (with stdout) like this:
```$ nosetests --nocapture``` or ```$ nosetests -s```

_**NB: Make sure if you use elasticsearch locally, it's running**_
