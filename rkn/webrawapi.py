#!/usr/bin/env python3
from webmain import WebMainApi


class WebRawApi(WebMainApi):

    def _printContent(self, data):
        print("Content-Type: text/plain\r\n\r\n" + data)

    def _formatContent(self, data):
        return str(data)


if __name__ == "__main__":
    result = WebRawApi().main()
    exit(code=result)
