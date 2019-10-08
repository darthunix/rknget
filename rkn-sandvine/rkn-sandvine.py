#!/usr/bin/env python3

import sys
import urllib.parse
from multiprocessing.pool import Pool, TimeoutError
from time import sleep
from functools import reduce

sys.path.append('../')
from common import webconn, utils


def exportToFileFormatted(path, dataset):
    """
    No format yet, huh
    :param path: path to export
    :param dataset: the data set
    :return: write result
    """
    return open(file=path, mode='w').write(
        '\n'.join(dataset))


# Function taken from rkn.api.parseutils
def getdomain(urlstr):
    # Domains are case insensitive, URLs are case sensitive
    return urllib.parse.urlparse(urlstr).netloc.split(':')[0].lower()


def exportHTTP(path, cutproto=False, extra=None, **apiconf):
    """
    :param cutproto: Truncates 'https://'
    """
    dataset = webconn.call(module='api.restrictions',
                           method='getBlockedHTTP',
                           cutproto=cutproto,
                           srcenttys=extra,
                           **apiconf)
    return exportToFileFormatted(path, dataset)


def exportHTTPS(path, cutproto=False, extra=None, **apiconf):
    """
    :param cutproto: Truncates 'https://'
    """
    dataset = webconn.call(module='api.restrictions',
                           method='getBlockedHTTPS',
                           cutproto=cutproto,
                           srcenttys=extra,
                           **apiconf)
    return exportToFileFormatted(path, dataset)


def exportDomains(path, collapse=True, extra = None, ** apiconf):
    """
    :param collapse: Collapse excessive.
    """
    dataset = webconn.call(module='api.restrictions',
                           method='getBlockedDNS',
                           collapse=collapse,
                           srcenttys=extra,
                           **apiconf)
    return exportToFileFormatted(path, dataset)


def exportWDomains(path, collapse=True, wc_asterize=False,
                          extra = None, ** apiconf):
    """
    :param collapse: Collapse excessive.
    :param wc_asterize: Appends *. prefix.
    """
    dataset = webconn.call(module='api.restrictions',
                           method='getBlockedWildcardDNS',
                           collapse=collapse,
                           wc_asterize=wc_asterize,
                           srcenttys=extra,
                           **apiconf)
    return exportToFileFormatted(path, dataset)


def exportIPs(path, collapse=True, subnet_fmt=False, ipv6=False, extra=None, **apiconf):
    dataset = webconn.call(module='api.restrictions',
                           method='getBlockedPrefixes',
                           collapse=collapse,
                           ipv6=ipv6,
                           srcenttys=extra,
                           **apiconf)
    if not subnet_fmt:
        if ipv6:
            # Truncating /128
            dataset = [ip.split('/128')[0] for ip in dataset]
        else:
            # Truncating /32
            dataset = [ip.split('/32')[0] for ip in dataset]

    return exportToFileFormatted(path, dataset)


def exportIPv4s(path, collapse=True, subnet_fmt=False, extra=None, **apiconf):
    return exportIPs(path, collapse, subnet_fmt, ipv6=False, extra=extra, **apiconf)


def exportIPv6s(path, collapse=True, subnet_fmt=False, extra=None, **apiconf):
    return exportIPs(path, collapse, subnet_fmt, ipv6=True, extra=extra, **apiconf)


PROC_DICT = {
    'http': exportHTTP,
    'https': exportHTTPS,
    'domain': exportDomains,
    'wdomain': exportWDomains,
    'ipv4': exportIPv4s,
    'ipv6': exportIPv6s
}


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
        logger.info('Initializing export threads pool...')
        threadpool = Pool(processes=int(config['Global']['threads']))
        resultpool = dict()

        for entity, options in config['Sandvine']['export'].items():
            logger.debug(entity + ' export started...')
            proc = PROC_DICT.get(entity)
            if proc is None:
                logger.warn('No such procedure built-in: ' + 'entity')
                continue
            resultpool[entity] = threadpool.\
                apply_async(proc, kwds={**options, **config['API']})

        # I know about wait() and get()
        timeout = int(config['Global']['wait_timeout'])
        runtime = 0
        pollsec = int(config['Global']['poll_timeout'])
        ready = dict()

        while runtime < timeout:

            for entity in resultpool.keys():
                ready[entity] = resultpool[entity].ready()

            if reduce(lambda a,b: a and b, ready.values()):
                logger.info('All tasks completed')
                break

            sleep(pollsec)
            runtime = runtime + pollsec
            logger.debug('Progress ' + str(runtime) + '/' + str(timeout) + ' sec: ' +
                         '|'.join([' ' + k + [' -- ', ' OK '][v] for k, v in ready.items()])
                         )

        logger.info('Export results:')
        for entity in resultpool.keys():
            try:
                logger.info(entity + ': ' + str(resultpool[entity].get(1)) + ' bytes written')
            except TimeoutError:
                logger.warn(entity + 'has been timed out')
        threadpool.terminate()

        if not reduce(lambda a, b: a or b, ready.values()):
            result = 'All exports failed'
            logger.error(result)
            raise Exception(result, errno=13)
        if reduce(lambda a, b: a and b, ready.values()):
            result = 'All exports were successfull'
            logger.info(result)
        else:
            result = 'Some exports failed'
            logger.warn(result)

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
