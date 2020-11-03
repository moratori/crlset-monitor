#!/usr/bin/env python3

import subprocess
import os
from logging import getLogger
from typing import List
from typing import Optional
from typing import Tuple

LOGGER = getLogger(__name__)


class SerialDifferenceChecker:

    def __init__(self, cnfg, cnfs):
        self.tool = cnfg.crlsettool.path
        self.crlset = cnfg.rawcrlset.path
        self.seriallist = cnfg.seriallist.path
        self.timeout = cnfs.serialdump.timeout

    def get_revoked_serials(self, rootfile: str) -> Optional[List[str]]:

        ret = subprocess.run(
            [self.tool, "dump", self.crlset, rootfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            timeout=self.timeout)

        if ret.returncode != 0:
            LOGGER.warning("crlset command abnormal end: %s" % ret.returncode)
            return None

        LOGGER.info("crlset command successfully end: %s" % ret.returncode)

        serials = []

        for line in ret.stdout.split("\n"):
            serial = line.strip()
            if serial != "":
                serials.append(serial)

        return sorted(serials)

    def get_difference_with_previous_version(self,
                                             serial_list_fname: str,
                                             revoked_serials: List[str]) \
            -> Tuple[List[str], List[str]]:

        fullpath = os.path.join(self.seriallist,
                                serial_list_fname)

        added: List[str] = []
        reduced: List[str] = []

        if not os.path.isfile(fullpath):
            return (added, reduced)

        loaded = []
        with open(fullpath, "r", encoding="utf8") as handle:
            for line in handle:
                serial = line.strip()
                if serial != "":
                    loaded.append(serial)

        for thisone in revoked_serials:
            if thisone not in loaded:
                added.append(thisone)

        for alredy in loaded:
            if alredy not in revoked_serials:
                reduced.append(alredy)

        return added, reduced

    def save_current_serials(self,
                             serial_list_fname: str,
                             revoked_serials: List[str]):
        fullpath = os.path.join(self.seriallist,
                                serial_list_fname)

        with open(fullpath, "w", encoding="utf8") as handle:
            handle.write("\n".join(revoked_serials))
