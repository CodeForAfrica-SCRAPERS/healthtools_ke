import json
import logging
import os
import requests

from logging import StreamHandler
from logging.handlers import HTTPHandler

from urlparse import urlparse
from urllib import urlencode
import urllib2 as urlrequest

from healthtools.config import (AWS, ES, SLACK, DATA_DIR,
                                SMALL_BATCH, NHIF_SERVICES)

                            
class SlackHandler(StreamHandler):
    """
    url: 
    channel: Set which channel you want to post to, e.g. "#general".
    username: The username that will post to Slack. Defaults to "Python logger".
    icon_url: URL to an image to use as the icon for the logger user
    icon_emoji: emoji to use as the icon. Overrides icon_url. If neither 
        icon_url nor icon_emoji is set, a red exclamation will be used.
    """

    def __init__(self, url=None, username=None, icon_url=None, icon_emoji=None, channel=None):
        StreamHandler.__init__(self, stream=None)

        self.url = url
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji
        self.channel = channel

    def emit(self, record):
        if isinstance(self.formatter, SlackFormatter):
            payload = {
                'attachments': [
                    self.format(record),
                ],
            }
        else:
            payload = {
                'text': self.format(record),
            }

        if self.username:
            payload['username'] = self.username
        if self.icon_url:
            payload['icon_url'] = self.icon_url
        if self.icon_emoji:
            payload['icon_emoji'] = self.icon_emoji
        if self.channel:
            payload['channel'] = self.channel

        ret = {
            'payload': json.dumps(payload),
        }

        if self.filters and isinstance(self.filters[0], SlackLogFilter):
            if record.notify_slack:
                payload = json.loads(ret['payload'])
                attachments = payload['attachments']
                print("\n-----------record.notify_slack==True----------")
                print payload
                print ("\n")
                print attachments[0]
                print ("\n")
                # '{"text": "This is posted to #general and comes from *monkey-bot*.",
                # "channel": "#general", "link_names": 1, "username": "monkey-bot", "icon_emoji": ":monkey_face:"}'
                response = requests.post(
                    SLACK["url"],
                    data=json.dumps({
                        "username": payload['username'],
                        "channel": payload['channel'],
                        "attachments": attachments
                    #     "attachments": [
                    #     {
                    #         "author_name": attachments['ERROR'],
                    #         "color": attachments['color'],
                    #         "pretext": "[SCRAPER] New Alert for {} : {}".format(attachments['ERROR'], errors["pretext"]),
                    #         "fields": [
                    #             {
                    #                 "title": "Message",
                    #                 "value": "{}".format(errors["message"]),
                    #                 "short": False
                    #             },
                    #             {
                    #                 "title": "Machine Location",
                    #                 "value": "{}".format(getpass.getuser()),
                    #                 "short": True
                    #             },
                    #             {
                    #                 "title": "Time",
                    #                 "value": "{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    #                 "short": True},
                    #         ]
                    #     }
                    # ]
                    }),
                    headers={"Content-Type": "application/json"}
                )
                print response

        return ret


class SlackFormatter(logging.Formatter):
    def format(self, record):
        ret = {}
        if record.levelname == 'INFO':
            ret['color'] = 'good'
        elif record.levelname == 'WARNING':
            ret['color'] = 'warning'
        elif record.levelname == 'ERROR':
            ret['color'] = '#E91E63'
        elif record.levelname == 'CRITICAL':
            ret['color'] = 'danger'

        ret['author_name'] = record.levelname
        ret['title'] = record.name
        ret['ts'] = record.created
        ret['text'] = super(SlackFormatter, self).format(record)
thhh
        print ("------------SlackFormatter-------------")
        print (super(SlackFormatter, self).format(record))
        print("\n")
        return ret


class SlackLogFilter(logging.Filter):
    """
    Logging filter to decide when logging to Slack is requested, using
    the `extra` kwargs:
        `logger.info("...", extra={'notify_slack': True})`
    """

    def filter(self, record):
        return getattr(record, 'notify_slack', False)


# Simple
# sh = SlackHandler()
# sh.setFormatter(SlackFormatter())
# logging.basicConfig(handlers=[sh])
# logging.error('error message')


# Using logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sh = SlackHandler(username='HealthTools Scraper',
                  url=SLACK["url"], channel="#ht_scraper_errors")
sh.setLevel(logging.DEBUG)

f = SlackFormatter()
sh.setFormatter(f)
logger.addHandler(sh)


sf = SlackLogFilter()
sh.addFilter(sf)

# logger.debug('debug message')
# logger.info('info message')
# logger.info('info message to slack', extra={'notify_slack': True})
# logger.warn('warn message')
message = {
    "ERROR": "scrape_site()",
    "SOURCE": "ww.abc.com",
    "MESSAGE": "No pages found."
}

try:
    errors = {
        "author": message['ERROR'],
        "pretext": message['SOURCE'],
        "message": message['MESSAGE'],
        }
except:
    errors = {
        "pretext": "",
        "author": message,
        "message": message,
    }

logger.error(errors, extra={'notify_slack': True})
# logger.critical('critical message')

# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# fh = logging.FileHandler('log_filename.txt')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(formatter)
# logger.addHandler(fh)

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)
# logger.addHandler(ch)
# logger.debug('This is a test log message.')
