#!/usr/bin/env python3
from webmain import WebApi


class WebRawApi(WebApi):

    self._DELIMETER="\n"
    self._HASHSIGN=":"

    def serialize(obj):
        if type(obj) == dict:
            return self._serialize(
                [self._serialize(k)+self._HASHSIGN+self._serialize(v) for k,v in obj.items()])
        elif type(obj) in {list,tuple,set}:
            return self._DELIMETER.join(map(self._serialize,obj))
        else:
            return str(obj)


    def _printContent(data):
        print("Content-Type: text/plain\r\n\r\n" + data)


    def _formatContent(data):
        return self._serialize(data)


if __name__ == "__main__":
    result = WebRawApi()
    exit(code=result)
