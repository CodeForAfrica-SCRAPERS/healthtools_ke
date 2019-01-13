# HealthTools Kenya Scraper

This is a suite of scrapers that retrieve actionable information for citizens to use. All the data scraped by this is accessible through our [HealthTools API](https://github.com/CodeForAfricaLabs/HealthTools.API).

They retrieve data from the following sites:

- Doctors: http://medicalboard.co.ke/online-services/retention/
- Foreign Doctors: http://medicalboard.co.ke/online-services/foreign-doctors-license-register
- Health Facilities: http://kmhfl.health.go.ke
- NHIF accredited inpatient facilities: http://www.nhif.or.ke/healthinsurance/inpatientServices
- NHIF accredited outpatient facilities: http://www.nhif.or.ke/healthinsurance/outpatientServices
- NHIF accredited outpatient facilities for civil servants: http://www.nhif.or.ke/healthinsurance/medicalFacilities


They currently run on [morph.io](http://morph.io) but you are able to set it up on your own server.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### How the Scrapers Work

To get the data we follow a couple of steps:

**1. Scrape website:** This is done in most cases using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).  
**2. Elastic Index update:** Replace data on elasticsearch with the new one. We only delete the documents after succesful completion of the scraping and not before. In the doctors' case, because we pull together foreign and local doctors, we won't update elasticsearch until both have been scraped succesfully.  
**3. Archive data:** We archive the data in a `latest.json` file so that the url doesn't have to change to get the latest version in a "dump" format. A date-stamped archive is also stored as we later intend to do some analysis on the changes over time.

Should the scraper fail at any of these points, we log the error, and if set up, a Slack notification is sent.


---

# Development

Clone repo and install the requirements this way:

```sh
$ git clone git@github.com:CodeForAfrica-SCRAPERS/healthtools_ke.git
$ cd healthtools_ke
$ mkvirtualenv healthtools-ke
(healthtools-ke)$ pip install -r requirements.txt
```

Other requirements include:

- **[Elastic](https://www.elastic.co/):** Index the data scraped.
- **Slack Webhook (*Optional*):** For error logging.
- **S3 Bucket (*Optional*):** Used to archive data.


## Elastic Setup

All the data scraped is uploaded to [Elastic](https://www.elastic.co/) for access by the [HealthTools API](https://github.com/CodeForAfricaLabs/HealthTools.API).

- For mac users, run `$ brew install elasticsearch` on your terminal.
- For linux and windows users, follow instructions from this [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html).

_**N/B:** Make sure if you use Elastic locally, it's running._


## Error Handling

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

### Slack Notifications (Optional):

To setup Slack notifications when the scrapers run into an error, start by creating an Incoming Webhook following these steps [here](https://slack.com/signin?redir=%2Fservices%2Fnew%2Fincoming-webhook) and set the `MORPH_WEBHOOK_URL` environment variable.

## Configuration

The following configurations are available for the scraper via env variables:

```sh
# Elastic host and port
$ export MORPH_ES_HOST="127.0.0.1"
$ export MORPH_ES_PORT=9200

# AWS Keys for ES Service (optional) and S3 (optional)
$ export MORPH_AWS_ACCESS_KEY_ID=""
$ export MORPH_AWS_SECRET_KEY=""

# AWS Region for S3 (optional)
$ export MORPH_AWS_REGION=""

# AWS S3 Bucket (optional)
$ export MORPH_S3_BUCKET=""

# Slack Webhook (optional)
$ export MORPH_WEBHOOK_URL=""
```

## Usage

In development, instead of scraping entire websites, you can scrape only a small batch (a few pages) to ensure your scrapers are working as expected.

Set the `SMALL_BATCH`, `SMALL_BATCH_HF` (for health facilities scrapers), and `SMALL_BATCH_NHIF` (for NHIF scrapers) in the config file that will ensure the scraper doesn't scrape entire sites but just the number of pages that you would like it to scrape defined by this variable.

Usage `$ python scraper.py --help`
    Example `$ python scraper.py --small-batch --scraper doctors` to run the scrapers.


## Tests

Use nosetests to run tests (with stdout) like this:

```sh
$ nosetests --nocapture
$ # Or
$ nosetests -s
```

---

# Deployment

TODO

---

# License

MIT License

Copyright (c) 2018 Code for Africa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
