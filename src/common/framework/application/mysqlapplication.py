#!/usr/bin/env python

import common.framework.application.baseapplication as appframe

from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

LOGGER = getLogger(__name__)


class MySQLApplication(appframe.BaseApplication):

    def __init__(self, module_name, script_name):
        super().__init__(module_name, script_name)

    def validate_config(self):
        self.cnfg.database.user
        self.cnfg.database.passwd
        self.cnfg.database.host
        self.cnfg.database.dbname

    def setup_resource(self):
        database_specifier = 'mysql://%s:%s@%s/%s?charset=utf8' % (
            self.cnfg.database.user,
            self.cnfg.database.passwd,
            self.cnfg.database.host,
            self.cnfg.database.dbname
        )
        self.dbengine = create_engine(database_specifier,
                                      encoding="utf-8",
                                      echo=False)

        LOGGER.debug("create db engine completed")

        session = scoped_session(sessionmaker(autocommit=False,
                                              autoflush=False,
                                              bind=self.dbengine))

        LOGGER.debug("create scoped session completed")

        self.session = session

    def setup_application(self):
        pass

    def teardown_application(self):
        pass

    def teardown_resource(self):
        self.session.close()
