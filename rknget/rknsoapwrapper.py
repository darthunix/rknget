import zeep.client
import zeep.transports
import time
import logging

class RknSOAPWrapper:
    """
    Class provides dump loading from RKN service via WSDL
    """

    _rknsoapclient = None
    _retryAttempts = 5
    _sleeptimeout = 60
    _dumpFmtVersion = '2.4'
    _logger = logging.getLogger()

    def __init__(self, url, retryAttempts=5, sleeptimeout=60, conntimeout=60, dumpfmtver='2.4', **kwargs):
        """
        Initiates WSDL service
        Throws exception if web service is unavailable
        """
        transport = zeep.transports.Transport(timeout=conntimeout)
        self._rknsoapclient = zeep.client.Client(wsdl=url,
                                                 transport=transport)
        self._rknsoapclient.options(raw_response=True)

        self._retryAttempts = retryAttempts
        self._sleeptimeout = sleeptimeout
        self._dumpFmtVersion = str(dumpfmtver)

    def _wsdlCall(self, method, **kwargs):
        """Makes WSDL request
        :return: xml response or None if failed
        """
        i = 0
        while i < self._retryAttempts:
            self._logger.debug("WSDL Call attempt #" + str(i+1))
            try:
                sp = self._rknsoapclient.service[method]
                if len(kwargs):
                    response = sp(**kwargs)
                else:
                    response = sp()
                if response:
                    return response
            except Exception as e:
                time.sleep(self._sleeptimeout)
            finally:
                i += 1

        # if i >= self._retryAttempts:
        return None

    def getLastDumpDateEx(self):
        """Obtains RKN dump state info
        :return: dict {lastDumpDate: UTS (ms), lastDumpDateUrgently: UTS (ms)}
        """
        return self._wsdlCall('getLastDumpDateEx')

    def getDumpFile(self, reqFileBase64, sigFileBase64):
        """Obtains RKN dump code
        Loads dump file
        :return: dump file zipped
        """

        dumpReqAnswer = self._wsdlCall('sendRequest',
                                       requestFile=reqFileBase64,
                                       signatureFile=sigFileBase64,
                                       dumpFormatVersion=self._dumpFmtVersion
                                       )
        if not dumpReqAnswer['result']:
            raise Exception('Couldn\'t send a request, reason: ' + dumpReqAnswer['resultComment'])

        j = 0
        while j < self._retryAttempts:
            self._logger.debug("Dump obtaining attempt #" + str(j + 1))
            resultAnswer = self._wsdlCall('getResult', code=dumpReqAnswer['code'])
            if not resultAnswer['result'] and resultAnswer['resultCode'] == 0:
                time.sleep(self._sleeptimeout)
            else:
                break
            j += 1
        if not resultAnswer['result']:
            raise Exception('Couldn\'t process a request, reason: ' + dumpReqAnswer['resultComment'])

        return resultAnswer['registerZipArchive']
