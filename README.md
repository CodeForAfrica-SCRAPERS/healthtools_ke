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
```
$ export MORPH_AWS_REGION=<aws_region>
$ export MORPH_AWS_ACCESS_KEY_ID= <aws_access_key_id>
$ export MORPH_AWS_SECRET_KEY= <aws_secret_key>
$ export ES_HOST= <elastic_search_host_endpoint> (DO NOT SET THIS IF YOU WOULD LIKE TO USE ELASTIC SEARCH LOCALLY ON YOUR MACHINE)
$ export WEBHOOK_URL= <slack_webhook_url> (DO NOT SET THIS IF YOU DON'T WANT TO POST ERROR MESSAGES ON SLACK)
```
**If you want to use elasticsearch locally on your machine use the following instructions to set it up**

For linux and windows users, follow instructions from this [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html)

For mac users run `brew install elasticsearch` on your terminal

**If you want to post messages on slack**

Set up `Incoming Webhooks` [here](https://slack.com/signin?redir=%2Fservices%2Fnew%2Fincoming-webhook) and set the global environment for the `WEBHOOK_URL`

If you set up elasticsearch locally run it `$ elasticsearch`

You can now run the scrapers `$ python scraper.py` (It might take a while)


## Running the tests
_**make sure if you use elasticsearch locally, it's running**_

Use nosetests to run tests (with stdout) like this:
```$ nosetests --nocapture```

