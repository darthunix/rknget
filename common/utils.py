"""
Common functions and patterns for the most of RKN scripts
"""
import logging
import sys
import yaml
import os
from datetime import datetime, timezone, timedelta


def initLog(logpath='log.log', stdoutlvl='DEBUG', logfilelvl='INFO', **kwargs):
    """
    Initialize two loggers: stdout and file
    :return: logger instance
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filehandler = logging.FileHandler(logpath)
    filehandler.setLevel(logging.getLevelName(logfilelvl))
    filehandler.setFormatter(formatter)
    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.getLevelName(stdoutlvl))
    streamhandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    logger.addHandler(streamhandler)

    return logger


CONFIG_PATH = 'config.yml'
# Parsing arguments
def confpath_argv():
    """
    Parses argv, loades config.yml
    :return: config path
    """
    if len(sys.argv) == 1:
        return CONFIG_PATH
    if len(sys.argv) == 3 and sys.argv[1] == '-c':
        return sys.argv[3]
    return None


# Print help
def print_help():
    print('Usage: ' + sys.argv[0] + ' (with ./config.yml)\n' +
          'Usage: ' + sys.argv[0] + ' -c [CONFIG PATH]')


# Importing configuration
def initConf(confpath, binpath):
    """
    :param confpath - YAML configuration path
    :param binpath - there must be __file__ passed
    Loades YAML config
    :return: Configuration tree
    """
    config = yaml.load(open(confpath))
    if config['Global'].get('procname') is None:
        config['Global']['procname'] = binpath.split(os.path.sep)[-1].split('.')[0]

    return config


def createFolders(*args):
    """
    Creates nesessary folders
    :param args: paths tuple
    :return: Nothing
    """
    for path in args:
        try:
            os.makedirs(path, mode=0o755, exist_ok=True)
        finally:
            pass


def getUnixTS(tz):
    """
    :param tz: TZ offset in hours
    :return: Current unix timestamp
    """
    if not tz:
        return datetime.now(timezone(timedelta(hours=3))).timestamp()
    return datetime.now(timezone(timedelta(hours=tz))).timestamp()