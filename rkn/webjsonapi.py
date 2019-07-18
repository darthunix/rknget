#!/usr/bin/env python3
import json


#!/usr/bin/env python3
from webmain import WebMainApi


class WebJSONApi(WebMainApi):

    def _printContent(self, data):
        print("Content-type:application/json\r\n\r\n")

    def _formatContent(self, data):
        return json.dumps(data, default=str)


if __name__ == "__main__":
    result = WebJSONApi().main()
    exit(code=result)
