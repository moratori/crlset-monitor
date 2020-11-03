#!/usr/bin/env python3

import requests
import json
import time
import tweepy
from logging import getLogger
from typing import List
from typing import Tuple

LOGGER = getLogger(__name__)


class Notifier:

    def __init__(self, cnfg, cnfs,
                 notify_target: List[Tuple[str, List[str], List[str]]]):

        self.slack_url = cnfs.notify.slack
        self.notify_wait = cnfs.notify.wait

        self.consumer_key = cnfs.notify.twitter_consumer_key
        self.consumer_secret = cnfs.notify.twitter_consumer_secret
        self.access_token = cnfs.notify.twitter_access_token
        self.access_token_secret = \
            cnfs.notify.twitter_access_token_secret

        self.notify_target = notify_target

    def _make_notify_slack_message(self, caname: str, added: List[str]):
        template = "CRLset changed for %s\nAdded new serials: %d\n%s"

        return template % (caname, len(added), "\n".join(added))

    def _make_notify_twitter_message(self, caname: str, added: List[str]):
        template = "CRLset changed for %s\nAdded new serials: %d\n"

        tmp_mes = template % (caname, len(added))
        serials = "\n".join(added)

        if len(tmp_mes) + len(serials) > 140:
            return tmp_mes

        return tmp_mes + serials

    def _notify_slack(self, caname: str, added: List[str]):
        message = self._make_notify_slack_message(caname, added)

        result = requests.post(
            self.slack_url,
            json.dumps(dict(text=message)),
            headers={'Content-Type': 'application/json'})

        LOGGER.info("slack post http status code: %d" % result.status_code)

    def _notify_twitter(self, caname: str, added: List[str]):
        message = self._make_notify_twitter_message(caname, added)

        auth = tweepy.OAuthHandler(self.consumer_key,
                                   self.consumer_secret)

        auth.set_access_token(self.access_token,
                              self.access_token_secret)

        api = tweepy.API(auth)
        ret = api.update_status(message)

        LOGGER.debug("tweepy update_status: %s" % str(ret))

    def notify(self):

        # reduced は一旦通知対象にはしない
        for (caname, added, reduced) in self.notify_target:
            if len(added) != 0:
                try:
                    self._notify_slack(caname, added)
                    self._notify_twitter(caname, added)
                except Exception as ex:
                    LOGGER.error("error while notifying: %s" % str(ex))
            time.sleep(self.notify_wait)
