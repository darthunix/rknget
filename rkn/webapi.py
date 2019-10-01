#!/usr/bin/env python3

# Extended reporting via this module:
#import cgitb

import cgi
import os

from webmain import WebMainApi


class WebPlainApi(WebMainApi):

    _DELIMETER="\n"
    _HASHSIGN=":"

    def _serialize(self, obj):
        if type(obj) == dict:
            return self._serialize(
                [self._serialize(k)+self._HASHSIGN+self._serialize(v) for k,v in obj.items()])
        elif type(obj) in {list,tuple,set}:
            return self._DELIMETER.join(map(self._serialize,obj))
        else:
            return str(obj)

    def _getParamsDict(self):
        fields = cgi.FieldStorage()
        return {key: fields.getvalue(key) for key in fields.keys()}

    def _getReqMethod(self):
        return os.environ['REQUEST_METHOD']

    def _printContent(self, data):
        print("Content-Type: text/plain\r\n\r\n" + data)

    def _formatContent(self, data):
        return self._serialize(data)


if __name__ == "__main__":
    result = WebPlainApi().main()
    exit(code=result)
