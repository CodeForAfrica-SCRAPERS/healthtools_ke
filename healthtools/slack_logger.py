# This is an adaptation of the python-slack-logger Python module by Code for Africa
# See https://github.com/CodeForAfricaLabs/python-slack-logger


import json
import logging
import requests
import re


class SlackHandler(logging.StreamHandler):
    """
    Python logging handler for Slack web hook integration

    url: Slack webhook
    channel: Set which channel you want to post to, e.g. "#general"
    username: The username that will post to Slack. Defaults to "Python logger"
    icon_url: URL to an image to use as the icon for the logger user
    icon_emoji: emoji to use as the icon. Overrides icon_url. If neither
        icon_url nor icon_emoji is set, a red exclamation will be used
    """

    def __init__(self, url=None, username=None, icon_url=None, icon_emoji=None, channel=None):
        logging.StreamHandler.__init__(self, stream=None)

        self.url = url
        self.username = username
        self.icon_url = icon_url
        self.icon_emoji = icon_emoji
        self.channel = channel
        self.response = None

    def emit(self, record):
        """
        Overides StreamHandler emit method
        Log the specified logging record. If a formatter is specified, it is used to format the record
        """
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
                payload = ret['payload']

                # Slack seems to strictly require double quotes
                payload = re.sub("\'", '"', payload)
                payload = re.sub('"\[{', '[{', payload)
                payload = re.sub(']"', ']', payload)

                self.response = requests.post(
                    self.url,
                    data=json.dumps(json.loads(r'%s' % payload)),
                    headers={"Content-Type": "application/json"}
                )

        return ret


class SlackFormatter(logging.Formatter):
    def format(self, record):
        """
        Do formatting for a record - if a formatter is set, use it.
        Otherwise, use the default formatter for the module
        """
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
        ret['pretext'] = "[SCRAPER] New Alert"
        ret['footer'] = "Healthtools scraper logger"
        ret['fields'] = super(SlackFormatter, self).format(record)

        return ret


class SlackLogFilter(logging.Filter):
    """
    Logging filter to decide when logging to Slack is requested, using
    the `extra` kwargs:
        `logger.info("...", extra={'notify_slack': True})`
    """

    def filter(self, record):
        return getattr(record, 'notify_slack', False)
