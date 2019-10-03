# Obsoleted

from db import resourceblocking


def unblockResources():
    resourceblocking.unblockAllResources()


def blockResourcesFairly():
    """
    Enables blocking resoures according to its blocktype and presence in the dump
    :return: blocked rows count
    """
    return resourceblocking.blockFairly()


def blockResourcesExcessively(src_entity, dst_entity):
    """
    Blocks dst_entities from src_entities data.
    :return: blocked rows count
    """
    return resourceblocking.blockExcessively(src_entity, dst_entity)


def blockCustom():
    """
    Blocks custom resources.
    :return: blocked rows count
    """
    return resourceblocking.blockCustom()


def unblockSet(resSet):
    """
    Unblocking set of resources.
    It may cause violations and bad consequences!
    :param resSet: the set of resources
    :return: blocked rows count
    """
    return resourceblocking.unblockSet(resSet)
