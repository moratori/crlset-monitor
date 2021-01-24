#!/usr/bin/env python3

"""
CCADBをダウンロードして保存する
"""

import os
import common.framework.application.baseapplication as appframe
import logic.CCADBDownloader as downloader

global LOGGER


class CCADBDownloader(appframe.BaseApplication):

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

        if not os.path.isdir(os.path.dirname(self.cnfs.icalist.path)):
            LOGGER.error("中間証明書の一覧を保存するディレクトリがありません")
            raise Exception("中間証明書の一覧を保存するディレクトリがありません")

    def run_application(self):
        downloader.CCADBDownloader(
            self.cnfg,
            self.cnfs).download_ccadb()


if __name__ == "__main__":
    app = CCADBDownloader()
    LOGGER = app.create_toplevel_logger()
    app.start()
