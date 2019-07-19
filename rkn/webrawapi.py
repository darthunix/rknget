#!/usr/bin/env python3
import cgi
from webmain import WebMainApi


class WebRawApi(WebMainApi):

    def _getParamsDict(self):
        fields = cgi.FieldStorage()
        return {key: fields.getvalue(key) for key in fields.keys()}

    def _printContent(self, data):
        print("Content-Type: text/plain\r\n\r\n" + data)

    def _formatContent(self, data):
        return str(data)


if __name__ == "__main__":
    result = WebRawApi().main()
    exit(code=result)
