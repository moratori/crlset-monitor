#!/usr/bin/evv python3

import subprocess
import os
from logging import getLogger

LOGGER = getLogger(__name__)


class CRLsetDownloader:

    def __init__(self, cnfg, cnfs):

        self.tool = cnfg.crlsettool.path
        self.crlset = cnfg.rawcrlset.path
        self.tmpcrlset = self.crlset + ".tmp"
        self.timeout = cnfs.downloader.timeout

    def download_crlset(self) -> int:

        LOGGER.info("CRLsetをダウンロードします")

        with open(self.tmpcrlset, "wb") as out:

            ret = subprocess.run([self.tool, "fetch"],
                                 stdout=out,
                                 stderr=subprocess.PIPE,
                                 encoding="utf8",
                                 timeout=self.timeout)

            LOGGER.info(ret.stderr)
            LOGGER.info("return code = %s" % ret.returncode)

            if ret.returncode == 0:
                LOGGER.info("CRLsetのダウンロードに成功しました")
                LOGGER.info("CRLsetのファイル名を変更します: %s -> %s" %
                            (self.tmpcrlset, self.crlset))
                os.replace(self.tmpcrlset, self.crlset)

        return ret.returncode
