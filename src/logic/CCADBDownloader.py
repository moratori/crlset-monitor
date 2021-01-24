#!/usr/bin/evv python3

import requests
from logging import getLogger

LOGGER = getLogger(__name__)


class CCADBDownloader:

    def __init__(self, cnfg, cnfs):

        self.icalist = cnfg.icalist.path
        self.url = cnfs.downloader.url
        self.timeout = cnfs.downloader.timeout

    def download_ccadb(self) -> int:

        LOGGER.info("ccadbをダウンロードします: %s" % self.url)

        req = requests.get(self.url, timeout=self.timeout)
        status_code = req.status_code

        LOGGER.info("httpステータスコード: %s" % str(status_code))

        if status_code == requests.codes.ok:
            LOGGER.info("結果をファイルに保存します")
            with open(self.icalist, "w", encoding="utf-8") as handle:
                handle.write(req.text)
        else:
            LOGGER.warning("ステータスコードが異常なので保存しません")

        return status_code
