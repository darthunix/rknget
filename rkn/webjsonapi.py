#!/usr/bin/env python3
import json
import sys


#!/usr/bin/env python3
from webmain import WebMainApi


class WebJSONApi(WebMainApi):

    def _getParamsDict(self):
        return json.loads(sys.stdin.read())

    def _printContent(self, data):
        print("Content-type:application/json\r\n\r\n" + data)

    def _formatContent(self, data):
        return json.dumps(data, default=str)


if __name__ == "__main__":
    result = WebJSONApi().main()
    exit(code=result)
