#!/usr/bin/env python3

import requests
import json
import time
import tweepy

import logic.CCADBLoader as ccadbloader

from logging import getLogger
from typing import List
from typing import Tuple
from typing import Optional

LOGGER = getLogger(__name__)


class Notifier:

    def __init__(self, cnfg, cnfs,
                 notify_target: List[Tuple[str, List[str], List[str]]]):
        self.cnfg = cnfg
        self.cnfs = cnfs
        self.slack_url = cnfs.notify.slack
        self.notify_wait = cnfs.notify.wait
        self.crtsh_base_url = cnfs.notify.crtsh_base_url
        self.myaccount = cnfs.notify.twitter_account

        self.consumer_key = cnfs.notify.twitter_consumer_key
        self.consumer_secret = cnfs.notify.twitter_consumer_secret
        self.access_token = cnfs.notify.twitter_access_token
        self.access_token_secret = \
            cnfs.notify.twitter_access_token_secret
        self.twitter_message_length = \
            cnfs.notify.twitter_message_length

        self.notify_target = notify_target

    def _make_notify_slack_message(self, caname: str, added: List[str]):
        template = "⚠ Intermediate cert was revoked by Chrome's CRLset:\n%s\n\nThat chain up to following root: %s"

        return template % ("\n".join(added), caname)

    def _make_notify_twitter_message(self, caname: str, added: List[str]):
        template1 = "⚠ Intermediate cert was revoked by Chrome's CRLset:\n%s\n\nThat chain up to following root: %s"
        template2 = "⚠ Some intermediate cert were revoked by CRLset. That chain up to following root: %s"

        serials = "\n".join(added)
        tmp_mes = template1 % (serials, caname)

        if len(tmp_mes) > self.twitter_message_length:
            return template2 % (caname)

        return tmp_mes

    def _notify_slack(self, message: str):
        result = requests.post(
            self.slack_url,
            json.dumps(dict(text=message)),
            headers={'Content-Type': 'application/json'})

        LOGGER.info("slack post http status code: %d" % result.status_code)

        return result

    def _notify_twitter(self, message: str,
                        in_reply_to_status_id: Optional[int]):
        auth = tweepy.OAuthHandler(self.consumer_key,
                                   self.consumer_secret)

        auth.set_access_token(self.access_token,
                              self.access_token_secret)

        api = tweepy.API(auth)
        if in_reply_to_status_id is None:
            ret = api.update_status(message)
        else:
            ret = api.update_status(
                message,
                in_reply_to_status_id=in_reply_to_status_id)

        LOGGER.debug("tweepy update_status: %s" % str(ret))

        return ret

    def _replay_detailed_cert_info(self, org_tweet, added: List[str]):

        ccadb = None

        try:
            ccadb = ccadbloader.CCADBLoader(self.cnfg, self.cnfs)
            ccadb.load_icalist()
        except Exception as ex:
            LOGGER.warning("CCADBの読み込みに失敗しました: %s" % (str(ex)))

        for serial in added:
            try:
                certname = "unknown"
                if ccadb is not None:
                    try:
                        tmp = ccadb.lookup_icaname_with_serial(serial)
                        if len(tmp) == 1:
                            certname = tmp[0]
                        else:
                            LOGGER.warning("CCADBでは一意に証明書を特定できませんでした")
                    except Exception as ex:
                        LOGGER.warning(
                            "CCADBのLookup中にエラーが発生しました: %s" % (str(ex)))

                crtsh_url = self.crtsh_base_url % serial
                template = "%s \nserial: %s\nname:%s\n%s"
                message = template % (
                    self.myaccount,
                    serial,
                    certname,
                    crtsh_url)

                self._notify_twitter(message, org_tweet.id)
            except Exception as ex:
                LOGGER.warn("error while replay to original tweet: %s" %
                            str(ex))
            time.sleep(self.notify_wait)

    def _notify_added_serials(self, caname: str, added: List[str]):
        try:
            twitter_message = self._make_notify_twitter_message(caname, added)
            slack_message = self._make_notify_slack_message(caname, added)

            self._notify_slack(slack_message)
            ret_twitter = self._notify_twitter(twitter_message, None)
        except Exception as ex:
            LOGGER.error("error while notifying: %s" % str(ex))

        self._replay_detailed_cert_info(ret_twitter, added)

    def _notify_reduced_serials(self, caname: str, added: List[str]):
        # reduced は一旦通知対象にはしない
        pass

    def notify(self):

        for (caname, added, reduced) in self.notify_target:
            if len(added) != 0:
                self._notify_added_serials(caname, added)
            if len(reduced) != 0:
                self._notify_reduced_serials(caname, reduced)
            time.sleep(self.notify_wait)
