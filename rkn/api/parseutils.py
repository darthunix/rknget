import urllib.parse
import re
import ipaddress


def punencodedom(urlstr):
    """
    IDNA encoding can fail for too long labels (>63 characters)
    See: https://en.wikipedia.org/wiki/Internationalized_domain_name
    """
    return urlstr.encode('idna').decode()


def getdomain(urlstr):
    # Domains are case insensitive, URLs are case sensitive
    return urllib.parse.urlparse(urlstr).netloc.split(':')[0].lower()


# More goddamn hardcode to the Hardcode God!
def urlHandler(urlstr):
    parsedUrl = list(urllib.parse.urlparse(urlstr))
    # Erroneous proto is assumed to be http.
    if parsedUrl[0] != 'http' and parsedUrl[0] != 'https':
        parsedUrl[0] = 'http'
    domain = parsedUrl[1].split(':')[0]
    if parsedUrl[1].find(':') != -1:
        port = ':' + parsedUrl[1].split(':')[1]
    else:
        port = ''
    # Domains are case insensitive, URLs are case sensitive
    domain = punencodedom(domain).lower()

    # Some magic with url parts after domain
    # Truncating fragment
    urllet = ''.join(list(map(
        lambda urlpart, char:
            char + urllib.parse.quote(string=urlpart, safe=''':/?#[]@!$&'()*+,;=%~''')
            if urlpart != '' else '',
        parsedUrl[2:-1], ['', ';', '?']
    )))
    # If the char appears once and is the last.
    if urlstr.find('?') == len(urlstr) - 1 or urlstr.find(';') == len(urlstr) - 1:
        urllet = urllet + urlstr[-1]

    return parsedUrl[0] + '://' + domain + port + urllet


def domainCorrect(s):
    """
    Corrects given domain.
    :param s: str
    :return: corrected domains
    """
    badchars = ('\\', '\'', '"')
    for c in badchars:
        if s.find(c) != -1:
            s = ''.join(s.split(c))
    return s


# Robust, but 5 times slower
def checkIp(s):
    """
    :param s: IP
    :return: true if the string is a public ip
    """
    try:
        ipaddress.IPv4Address(s)
        return not ipaddress.ip_network(s).is_private
    except ValueError:
        return False


def checkIpsub(s):
    """
    :param s: IP
    :return: true if the string is a public ip
    """
    try:
        ipaddress.IPv4Network(s)
        return not ipaddress.ip_network(s).is_private
    except ValueError:
        return False


def checkIpv6(s):
    """
    :param s: IP
    :return: true if the string is a public ip
    """
    try:
        ipaddress.IPv6Address(s)
        return not ipaddress.ip_network(s).is_private
    except ValueError:
        return False


def checkIpv6sub(s):
    """
    :param s: IP
    :return: true if the string is a public ip
    """
    try:
        ipaddress.IPv6Network(s)
        return not ipaddress.ip_network(s).is_private
    except ValueError:
        return False


__ipregex = re.compile('''\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}''')


# 5x faster, but may be unreliable
def _isip(s):
    return __ipregex.fullmatch(s) is not None


def _isipsub(s):
    try:
        ip, sub = s.split('/')
        if int(sub) <= 32 and isip(ip):
            return True
    except:
        return False


__domregex = re.compile('''^.+\..*[^.]$''')


def isdomain(s):
    return __domregex.fullmatch(s) is not None


def getSubnetIPs(s):
    try:
        return ipaddress.ip_network(s).hosts()
    except ValueError:
        return None
