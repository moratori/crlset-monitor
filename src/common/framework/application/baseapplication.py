#!/usr/bin/env python

import ast
import os
import shelve
import threading
import configparser
import namedtupled
import sys
import traceback

from logging import getLogger
from abc import ABCMeta, abstractmethod

import common.framework.logger as logger
import common.framework.config as config


LOGGER = getLogger(__name__)


class BaseApplication(metaclass=ABCMeta):

    SCRIPT_EXT = ".py"
    CONF_EXT = ".ini"
    GENERAL_CONF_NAME = "general" + CONF_EXT

    RET_NORMAL_END = 0
    RET_KEY_INTERRUPTED_END = 1
    RET_ABNORMAL_END = 100

    def __init__(self, module_name, script_name):
        try:
            self.module_name = module_name
            self.script_name = script_name
            self._prepare_config_dir()
            self.load_config()
            self._prepare_appcache()
            self.validate_config()
            self.__toplevel_logger = None
            self.create_toplevel_logger()
        except Exception as ex:
            print(traceback.format_exc(), file=sys.stderr)
            sys.exit(BaseApplication.RET_ABNORMAL_END)

    @abstractmethod
    def validate_config(self):
        pass

    @abstractmethod
    def setup_resource(self):
        pass

    @abstractmethod
    def setup_application(self):
        pass

    @abstractmethod
    def run_application(self, **args):
        pass

    @abstractmethod
    def teardown_application(self):
        pass

    @abstractmethod
    def teardown_resource(self):
        pass

    def _prepare_appcache(self):
        dbname = os.path.join(config.APPCACHE,
                              os.path.basename(self.script_name))

        self.__appcache = shelve.open(dbname, flag="c", writeback=False)
        self.__appcache_mutex = threading.BoundedSemaphore(value=1)

    def set_cache(self, key, value):
        with self.__appcache_mutex:
            self.__appcache[key] = value

    def del_cache(self, key):
        with self.__appcache_mutex:
            del self.__appcache[key]

    def get_cache(self, key):
        return self.__appcache[key]

    def get_cache_keys(self):
        return self.__appcache.keys()

    def _convert_config_type(self, config):
        if isinstance(config, str):
            return ast.literal_eval(config)
        elif isinstance(config, dict):
            result = dict()
            for (key, value) in config.items():
                result[key] = self._convert_config_type(value)
            return result
        else:
            raise Exception("unknown config type: %s" % type(config))

    def load_config(self):
        specific_config_basename = \
            os.path.basename(self.script_name).\
            replace(BaseApplication.SCRIPT_EXT,
                    BaseApplication.CONF_EXT)

        general_conf = configparser.ConfigParser()
        specific_conf = configparser.ConfigParser()

        general_conf.read(os.path.join(config.CONFIG_DIR,
                                       BaseApplication.GENERAL_CONF_NAME))
        specific_conf.read(os.path.join(config.CONFIG_DIR,
                                        specific_config_basename))

        self.cnfg = namedtupled.map(self._convert_config_type(
            general_conf._sections))

        self.cnfs = namedtupled.map(self._convert_config_type(
            specific_conf._sections))

    def _prepare_config_dir(self):
        for directory in config.DIRECTORIES:
            if not os.path.isdir(directory):
                os.mkdir(directory)

    def create_toplevel_logger(self):
        if self.__toplevel_logger is None:
            self.__toplevel_logger = \
                logger.setup_logger(self.module_name,
                                    self.script_name,
                                    self.cnfg.logging.loglevel,
                                    self.cnfg.logging.rotation_timing,
                                    self.cnfg.logging.backupcount)
        return self.__toplevel_logger

    def start(self, **args):
        retcode = BaseApplication.RET_NORMAL_END
        try:
            LOGGER.info("start application!")

            LOGGER.info("start setup resource")
            self.setup_resource()
            LOGGER.info("end setup resource")

            LOGGER.info("start application setup")
            self.setup_application()
            LOGGER.info("end application setup")

            LOGGER.info("start main routine")
            result = self.run_application(**args)
            LOGGER.info("end main routine")

            LOGGER.info("end application without unexpected error")
            if (type(result) is int):
                retcode = result
        except KeyboardInterrupt:
            LOGGER.warn("keyboard interrupted")
            retcode = BaseApplication.RET_KEY_INTERRUPTED_END
        except Exception as ex:
            LOGGER.error("unexpected exception <%s> occurred" % (str(ex)))
            LOGGER.error(traceback.format_exc())
            retcode = BaseApplication.RET_ABNORMAL_END
        finally:
            LOGGER.info("start cleanup")
            try:
                LOGGER.info("start teardown application")
                self.teardown_application()
                LOGGER.info("end teardown application")
            except Exception as ex:
                LOGGER.warning("unexpected exception <%s> occurred" %
                               str(ex))
            try:
                LOGGER.info("start teardown resource")
                self.teardown_resource()
                LOGGER.info("end teardown resource")
            except Exception as ex:
                LOGGER.warning("unexpected exception <%s> occurred" %
                               str(ex))
            try:
                LOGGER.info("start persistent app cache")
                self.__appcache.close()
                LOGGER.info("end persistent app cache")
            except Exception as ex:
                LOGGER.warning("unexpected exception <%s> occurred" %
                               str(ex))
            LOGGER.info("end cleanup")

        sys.exit(retcode)
