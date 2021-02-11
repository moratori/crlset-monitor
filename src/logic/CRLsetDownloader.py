#!/usr/bin/evv python3

import subprocess
import os
import datetime
import shutil
import hashlib
from logging import getLogger

LOGGER = getLogger(__name__)


class CRLsetDownloader:

    def __init__(self, cnfg, cnfs):

        self.tool = cnfg.crlsettool.path
        self.crlset = cnfg.rawcrlset.path
        self.oldcrlset = cnfg.oldcrlset.path
        self.tmpcrlset = self.crlset + ".tmp"
        self.timeout = cnfs.downloader.timeout

    def save_old_crlset(self):

        LOGGER.info("新旧CRLsetに差異があるか確認します")

        old_crlset_hash = ""
        new_crlset_hash = ""

        with open(self.crlset, "rb") as old, open(self.tmpcrlset, "rb") as new:
            old_crlset_hash = hashlib.sha256(old.read()).hexdigest()
            new_crlset_hash = hashlib.sha256(new.read()).hexdigest()

        LOGGER.info("新しいCRLsetファイルのハッシュ: %s" %
                    str(new_crlset_hash))
        LOGGER.info("古いCRLsetファイルのハッシュ: %s" %
                    str(old_crlset_hash))

        if old_crlset_hash != new_crlset_hash:

            LOGGER.info("古いCRLsetを退避します")
            current_time = datetime.datetime.utcnow().\
                strftime("%Y-%m-%d_%H-%M-%S")
            dst = os.path.join(self.oldcrlset,
                               "crlset_%s" % current_time)
            shutil.copy2(self.crlset, dst)

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

                try:
                    self.save_old_crlset()
                except Exception as ex:
                    LOGGER.warning("古いCRLsetの保管に失敗しました")
                    LOGGER.info(str(ex))

                LOGGER.info("CRLsetのファイル名を変更します: %s -> %s" %
                            (self.tmpcrlset, self.crlset))
                os.replace(self.tmpcrlset, self.crlset)

            else:
                LOGGER.error("CRLsetのダウンロードに失敗しました")

        return ret.returncode
