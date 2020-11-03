#!/usr/bin/env python3

"""
プロジェクトに必要な定数を定義する
"""

import os
from typing import List

if __name__ != "__main__":

    PROJECT_ROOT: str = \
        os.path.dirname(os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../../")))

    APPCACHE: str = os.path.join(PROJECT_ROOT, "appcache")
    LOGS_DIR: str = os.path.join(PROJECT_ROOT, "logs")
    STATIC_DIR: str = os.path.join(PROJECT_ROOT, "static")
    TEMPLATES_DIR: str = os.path.join(PROJECT_ROOT, "templates")
    CONFIG_DIR: str = os.path.join(PROJECT_ROOT, "conf")

    DIRECTORIES: List[str] = [
        PROJECT_ROOT,
        APPCACHE,
        LOGS_DIR,
        STATIC_DIR,
        TEMPLATES_DIR,
        CONFIG_DIR
    ]
