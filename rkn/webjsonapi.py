#!/usr/bin/env python3
import json


#!/usr/bin/env python3
from webmain import WebMainApi


class WebJSONApi(WebMainApi):

    def _printContent(self, data):
        print("Content-Type: text/plain\r\n\r\n" + data)

    def _formatContent(self, data):
        return json.dumps(data, default=str)


if __name__ == "__main__":
    result = WebJSONApi().main()
    exit(code=result)
