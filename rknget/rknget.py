#!/usr/bin/env python3

import sys
import os
import io
import zipfile
from datetime import datetime

import rknsoapwrapper
sys.path.append('../')
from common import webconn, utils


def main():
    configPath = utils.confpath_argv()
    if configPath is None:
        utils.print_help()
        return 0

    config = utils.initConf(configPath, __file__)

    logger = utils.initLog(**config['Logging'])
    logger.debug('Starting with config:\n' + str(config))

    utils.createFolders(config['Global']['tmppath'])

    try:
        running = webconn.call(module='api.procutils',
                               method='checkRunning',
                               procname=config['Global']['procname'],
                               **config['API'])
    except Exception as e:
            logger.critical('Couldn\'t obtain information from the database\n' + str(e))
            return 9
    if running and not config['Global'].get('forcerun'):
        logger.critical('The same program is running at this moment. Halting...')
        return 0
    # Getting PID
    log_id = webconn.call(module='api.procutils',
                          method='addLogEntry',
                          procname=config['Global']['procname'],
                          **config['API'])
    try:
        if config['Miscellaneous']['uselocaldump']:
            dumpFile = open(file=config['Global']['dumpPath'],
                            mode='rb').read()
        else:
            # Checking dump info
            logger.debug('Obtaining dumpfile from ' + config['DumpLoader']['url'])
            rknSW = rknsoapwrapper.RknSOAPWrapper(**config['DumpLoader'])
            dumpDate = rknSW.getLastDumpDateEx()
            if not dumpDate:
                raise Exception('Couldn\'t obtain dumpdates info', errno=2)

            # Loaded dump unix timestamp in seconds
            update_ts = max(dumpDate['lastDumpDate'],
                            dumpDate['lastDumpDateUrgently'])/1000
            logger.info('Latest dump timestamp is: ' +
                         str(datetime.fromtimestamp(update_ts))
                         )
            # Last parsed dump lag in seconds
            dump_ts = webconn.call(module='api.monitoring',
                                   method='getLastDumpTS',
                                   **config['API'])
            logger.info('Parsed dump timestamp is: ' +
                         str(datetime.fromtimestamp(dump_ts))
                         )
            # 5 seconds rule
            if update_ts + 5 > dump_ts:
                result = 'The latest dump is relevant'
                logger.info(result)
                # Updating the state in database
                webconn.call(module='api.dumpparse',
                             method='updateDumpCheckTime',
                             **config['API'])
                # Finalising
                webconn.call(module='api.procutils',
                             method='finishJob',
                             log_id=log_id,
                             exit_code=0,
                             result=result,
                             **config['API'])
                return 0

            # Obtaining dump file
            logger.info('Blocklist is outdated, requesting a new dump')
            dumpFile = rknSW.getDumpFile(open(config['Global']['reqPath'], 'rb').read(),
                                         open(config['Global']['reqPathSig'], 'rb').read()
                                         )
            if config['Global']['savedump']:
                logger.info('Saving file to ' + config['Global']['dumpPath'])
                open(file=config['Global']['dumpPath'], mode='wb').write(dumpFile)

        # Parsing dump file
        logger.info('Parsing the dump')
        xmldump = zipfile.ZipFile(io.BytesIO(dumpFile)).read('dump.xml').decode('cp1251')
        # Freeing memory
        del dumpFile

        parse_result = webconn.call(module='api.dumpparse',
                                    method='parse',
                                    xmldump=xmldump,
                                    **config['API'])
        if not parse_result:
            raise Exception('Dump hasn\'t been parsed', errno=3)
        # Freeing memory
        del xmldump
        result = 'Dump have been parsed to database successfully'
        logger.info(result)

        # Updating the state in the database
        webconn.call(module='api.procutils',
                     method='finishJob',
                     log_id=log_id,
                     exit_code=0,
                     result=result,
                     **config['API'])
        logger.info('Blocking was finished, enjoy your 1984th')

    except Exception as e:
        webconn.call(module='api.procutils',
                     method='finishJob',
                     log_id=log_id,
                     exit_code=1,
                     result=str(e),
                     **config['API'])
        logger.error(str(e))
        return getattr(e, 'errno', 1)

    return 0


if __name__ == "__main__":
    result = main()
    exit(code=result)
