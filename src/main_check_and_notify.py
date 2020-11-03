#!/usr/bin/env python3

"""
CRLsetコマンドを用いて最新のCRLsetをダウンロードする
"""

import os
import common.framework.application.baseapplication as appframe
import logic.SerialDifferenceChecker as checker
import logic.Notifier as notifier

from typing import List
from typing import Tuple

global LOGGER


class CheckAndNotify(appframe.BaseApplication):

    def __init__(self):
        super().__init__(__name__, __file__)

    def validate_config(self):
        pass

    def setup_resource(self):
        pass

    def teardown_application(self):
        pass

    def teardown_resource(self):
        pass

    def setup_application(self):

        self.rootcerts_dir = self.cnfg.rootcerts.path
        self.crlset = self.cnfg.rawcrlset.path
        self.seriallist = self.cnfg.seriallist.path
        self.tool = self.cnfg.crlsettool.path

        if not os.path.isfile(self.tool):
            LOGGER.error("crlsetコマンドが存在しません")
            raise Exception("crlsetコマンドが存在しません")

        if not os.access(self.tool, os.X_OK):
            LOGGER.error("crlsetコマンドが実行可能ではありません")
            raise Exception("crlsetコマンドが実行可能ではありません")

        if not os.path.isdir(self.rootcerts_dir):
            LOGGER.error("ルート証明書用のディレクトリが存在しません: %s" %
                         self.cnfg.rootcerts.path)
            raise Exception("ルート証明書を配置するディレクトリが存在しません")

        if not os.path.isfile(self.crlset):
            LOGGER.error("CRLsetが存在しません: %s" % self.cnfg.rawcrlset.path)
            raise Exception("CRLsetが存在しません")

        if not os.path.isdir(self.seriallist):
            LOGGER.error("シリアル番号管理用ディレクトリが存在しません: %s" %
                         self.cnfg.seriallist.path)
            raise Exception("シリアル番号管理用ディレクトリが存在しません")

    def run_application(self):

        notify_target: List[Tuple[str, List[str], List[str]]] = []

        diffcheck = checker.SerialDifferenceChecker(self.cnfg, self.cnfs)

        for fname in os.listdir(self.rootcerts_dir):

            if not fname.endswith(".pem"):
                LOGGER.warning(
                    ".pemをファイル名としないルート証明書はスキップします")
                continue

            fullpath = os.path.join(self.rootcerts_dir, fname)
            LOGGER.info("processing for: %s" % fullpath)

            try:
                revoked_serials = diffcheck.get_revoked_serials(fullpath)

                if revoked_serials is None:
                    continue

                LOGGER.info("revoked serials: %s" % revoked_serials)

                (added, reduced) = \
                    diffcheck.get_difference_with_previous_version(
                        fname, revoked_serials)

                LOGGER.info("新たに追加されたシリアル: %s" % added)
                LOGGER.info("削除されたシリアル: %s" % reduced)

                if len(added) != 0 or len(reduced) != 0:
                    notify_target.append(
                        (fname.replace(".pem", ""), added, reduced))

                diffcheck.save_current_serials(fname, revoked_serials)
            except Exception as ex:
                LOGGER.error(str(ex))

        LOGGER.info("通知対象: %s" % notify_target)

        notifier.Notifier(self.cnfg, self.cnfs, notify_target).notify()


if __name__ == "__main__":
    app = CheckAndNotify()
    LOGGER = app.create_toplevel_logger()
    app.start()
