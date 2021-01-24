#!/usr/bin/env python3

import csv
from logging import getLogger
from typing import List

LOGGER = getLogger(__name__)


class CCADBLoader:

    def __init__(self, cnfg, cnfs):
        self.icalist = cnfg.icalist.path
        self.data = []

    def load_icalist(self) -> None:

        LOGGER.info("中間認証局の情報ファイルをロードします: %s" % (self.icalist))

        result = []
        with open(self.icalist, "r", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            for line in reader:
                result.append(line)
        self.data = result

        LOGGER.info("ロードが完了しました")
        LOGGER.debug(self.data)

    def lookup_icaname_with_serial(self, target_serial: str) -> List[str]:
        result: List[str] = []

        for ca in self.data:
            icaname = ca[5]
            serial = ca[7]
            if serial.strip().lower() == target_serial.strip().lower():
                result.append(icaname)

        return result
