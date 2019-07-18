#!/usr/bin/env python3
import webmain import main as main


def _getParamsDict():
    fields = cgi.FieldStorage()
    return {key: fields.getvalue(key) for key in fields.keys()}


DELIMETER="\n"
HASHSIGN=":"
def serialize(obj):
    if type(obj) == dict:
        return serialize(
            [serialize(k)+HASHSIGN+serialize(v) for k,v in obj.items()])
    elif type(obj) in {list,tuple,set}:
        return DELIMETER.join(map(serialize,obj))
    else:
        return str(obj)


def printContent(data):
    print("Content-Type: text/plain\r\n\r\n" + data)


def formatContent(data):
    return serialize(data)


if __name__ == "__main__":
    result = main()
    exit(code=result)
