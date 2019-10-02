#!/usr/bin/env python3
import api.caching
from settings import apiconf

class WebMainApi:
    """
    The abstract class for printing CGI data, but hasn't had its procedures implemented.
    """

    def _getParamsDict(self):
        pass

    def _getReqMethod(self):
        pass

    def _printContent(self, data):
        pass

    def _formatContent(self, data):
        pass

    def main(self):
        params = self._getParamsDict()
        reqmethod = self._getReqMethod()
        fields = params.copy()
        modval = fields.pop('module', None)
        if modval.split('.')[0] != 'api':
            self._printContent('Not an API')
            return 1
        metval = fields.pop('method', None)

        # Shoot your leg through!!!
        module = __import__(modval, fromlist=[metval])
        if reqmethod == 'GET' \
            and modval not in apiconf.getable:
            return 2

        if modval in apiconf.cacheable:
            # Trying to fetch from the cache
            data = api.caching.getDataCached(
                getattr(module, metval), **fields)
        else:
            data = getattr(module, metval)(**fields)

        self._printContent(self._formatContent(data))
        return 0
