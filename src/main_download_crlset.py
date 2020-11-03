#!/usr/bin/env python3

"""
CRLsetコマンドを用いて最新のCRLsetをダウンロードする
"""

import os
import common.framework.application.baseapplication as appframe
import logic.CRLsetDownloader as downloader

global LOGGER


class CRLsetDownloader(appframe.BaseApplication):

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

        if not os.path.isfile(self.cnfg.crlsettool.path):
            LOGGER.error("crlsetコマンドが存在しません")
            raise Exception("crlsetコマンドが存在しません")

        if not os.access(self.cnfg.crlsettool.path, os.X_OK):
            LOGGER.error("crlsetコマンドが実行可能ではありません")
            raise Exception("crlsetコマンドが実行可能ではありません")

    def run_application(self):
        downloader.CRLsetDownloader(
            self.cnfg,
            self.cnfs).download_crlset()


if __name__ == "__main__":
    app = CRLsetDownloader()
    LOGGER = app.create_toplevel_logger()
    app.start()
