from sqlalchemy import or_, and_

from db.dbhandler import DatabaseHandler
from db.scheme import *


class BlockData(DatabaseHandler):
    """
    Successor class, which provides blocked resources data
    """

    def __init__(self, connstr):
        super(BlockData, self).__init__(connstr)

    def _getBlockedResourcesQuery(self, entityname):
        """
        :param entitytype: resource entitytype
        :return: query
        """
        # Distinct is not needed for set()
        # distinct(Resource.value). \
        return self._session.query(Resource.value). \
            join(Entitytype, Resource.entitytype_id == Entitytype.id). \
            filter(Entitytype.name == entityname). \
            filter(Resource.is_blocked == True)

    def getBlockedResourcesSet(self, entityname):
        """
        :param entitytype: resource entitytype
        :return: resources' values set
        """
        query = self._getBlockedResourcesQuery(entityname)

        resSet = {resrow.value for resrow in query.all()}

        return resSet


    def _getFairlyBlockedResourcesQuery(self, entityname):
        """
        :param entitytype: resource entitytype
        :return: query
        """
        # Distinct is not needed for set()
        # distinct(Resource.value). \

        fairness = {
            'http': 'default', 'https': 'default',
            'domain': 'domain',
            'domain-mask': 'domain-mask',
            'ip': 'ip', 'ipsubnet': 'ip', 'ipv6': 'ip', 'ipv6subnet': 'ip'
        }

        return self._session.query(Resource.value). \
            join(Entitytype, Resource.entitytype_id == Entitytype.id). \
            join(Content, Resource.content_id == Content.id). \
            join(BlockType, Content.blocktype_id == BlockType.id). \
            filter(Entitytype.name == entityname). \
            filter(Resource.is_blocked == True). \
            filter(BlockType.name == fairness[entityname])

    def getFairlyBlockedResourcesSet(self, entityname):
        """
        :param entitytype: resource entitytype
        :return: resources' values set
        """
        query = self._getFairlyBlockedResourcesQuery(entityname)

        resSet = {resrow.value for resrow in query.all()}

        return resSet


