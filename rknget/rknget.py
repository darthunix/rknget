#!/usr/bin/env python3

import sys
import yaml
import logging
import os

sys.path.append('../')
from rkn import rknsoapwrapper, dumpparse, blocking, procutils

CONFIG_PATH = 'config.yml'

PROCNAME = __file__.split(os.path.sep)[-1].split('.')[0]

# Parsing arguments
def confpath_argv():
    """
    Parses argv, loades config.yml
    :return: config path
    """
    if len(sys.argv) == 1:
        return CONFIG_PATH

    if len(sys.argv) == 3 and sys.argv[2] == '-c':
        return sys.argv[3]

    return None


# Print help
def print_help():
    print('Usage: ' + sys.argv[0] + ' (with ./config.yml)\n' +
          'Usage: ' + sys.argv[0] + ' -c [CONFIG PATH]')


# Importing configuration
def initConf(configpath):
    """
    Loades YAML config
    :return: Configuration tree
    """
    return yaml.load(open(configpath))


# Initialising logger, returns logger
def initLog(logpath='log.log', stdoutlvl='DEBUG', logfilelvl='INFO', **kwargs):

    logger = logging.getLogger()
    logger.setLevel(logging.getLevelName(stdoutlvl))
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


def createFolders(*args):
    """
    Creates nesessary folders
    :param args: paths tuple
    :return: Nothingzzzя
    """
    for path in args:
        try:
            os.makedirs(path, mode=0o755, exist_ok=True)
        finally:
            pass


def buildConnStr(engine, host, port, dbname, user, password, **kwargs):
    return engine + '://' + \
           user + ':' + password + '@' + \
           host + ':' + str(port) + '/' + dbname


def main():
    configPath = confpath_argv()
    if configPath is None:
        print_help()
        return 0

    config = initConf(configPath)

    logger = initLog(**config['Logging'])
    logger.debug('Starting with config:\n' + str(config))

    connstr = buildConnStr(**config['DB'])

    createFolders(config['Global']['tmppath'])

    try:
        running = procutils.checkRunning(connstr, PROCNAME)
    except Exception as e:
        logger.critical('Couldn\'t obtain information from the database\n' + str(e))
        return 9
    if running and not config['Global'].get('forcerun'):
        logger.critical('The same program is running at this moment. Halting...')
        return 0
    log_id = procutils.addLogEntry(connstr, PROCNAME)

    try:
        dumpinfo = dumpparse.getLastDumpInfo(connstr)

        # Checking dump info
        logger.debug('Obtaining dumpfile from ' + config['DumpLoader']['url'])
        rknSW = rknsoapwrapper.RknSOAPWrapper(**config['DumpLoader'])
        dumpDate = rknSW.getLastDumpDateEx()
        if not dumpDate:
            raise Exception('Couldn\'t obtain dumpdates info', errno=2)
        if dumpinfo is not None and \
            dumpinfo['parse_time'].timestamp() > min(dumpDate['lastDumpDate'],
                                                     dumpDate['lastDumpDateUrgently']):
            result = 'Last dump is relevant'
            logger.info(result)
            # Updating the state in database
            procutils.finishJob(connstr, log_id, 0, result)
            return 0

        # Obtaining dump file
        logger.info('Blocklist is outdated, requesting a new dump')
        dumpFile = rknSW.getDumpFile(open(config['Global']['reqPath'], 'rb').read(),
                                     open(config['Global']['reqPathSig'], 'rb').read()
                                     )
        if config['Global']['savetmp']:
            open(file=config['Global']['tmppath']+'/dump.xml.zip', mode='wb').write(dumpFile)
        # If you do wanna use downloaded file, take this instead of 'Loading' block above
        # dumpFile = open(file=config['Global']['tmppath']+'/dump.xml.zip', mode='rb').read()

        # Parsing dump file
        dumpparse.parse(dumpFile, connstr)
        # Freeing memory
        del dumpFile
        logger.info('Dump have been parsed to database successfully')
        # Blocking
        rowsdict = dict()
        # It may slow down but is safe
        blocking.unblockResources(connstr)
        # Fairly blocking first
        logger.debug('Blocking fairly (as is)')
        rows = blocking.blockResourcesFairly(connstr)
        rowsdict['fairly'] = rows
        logger.info('Blocked fairly ' + str(rows) + ' rows')
        for src, dst in config['Blocking']:
            logger.info('Blocking ' + str(dst) + ' from ' + str(src))
            rows = blocking.blockResourcesExcessively(connstr, src, dst)
            if rows is not None:
                logger.info('Blocked ' + str(rows) + ' rows')
                rowsdict[str(dst) + '->' + str(src)] = rows
            else:
                logger.warning('Nothing have been blocked from' + str(src) + ' to ' + str(dst))
        # Blocking custom resouces
        if config['Miscellaneous']['custom']:
            logger.info('Blocking custom resources')
            rows = blocking.blockCustom(connstr)
            logger.info('Blocked ' + str(rows))
            rowsdict['Custom'] = rows

        # Updating the state in the database
        result = 'Blocking results\n' + '\n'.join(k + ':' + str(v) for k,v in rowsdict.items())
        procutils.finishJob(connstr, log_id, 0, result)
        logger.info('Blocking was finished, enjoy your 1984th')

    except Exception as e:
        procutils.finishJob(connstr, log_id, 1, str(e))
        logger.error(str(e))
        return getattr(e, 'errno', 1)

    return 0


if __name__ == "__main__":
    result = main()
    exit(code=result)
