from db import procdata

"""
This module works with Log
"""

def checkRunning(procname):
    """
    Checks if this instance has already been started not so far
    :return: True if the same program is running, else False
    """
    return procdata.checkRunning(procname)


def addLogEntry(procname):
    """
    :return: Log id for this process instance
    """
    return procdata.addLogEntry(procname)


def finishJob(log_id, exit_code, result):
    """
    :return: Log id for this process instance
    """
    return procdata.finishJob(log_id, exit_code, result)

