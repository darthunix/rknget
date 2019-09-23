import xml.etree.ElementTree

from datetime import datetime

from api import parseutils
import dataprocessing


class RKNDumpFormatException(BaseException):
    pass


#class RKNDumpFormatException(Exception):
#    def __init__(self, message, errors):
#        # Call the base class constructor with the parameters it needs
#        super().__init__(message)
#        # Now for your custom code...
#        self.errors = errors


def parsedRecently(update_time, connstr):
    """
    Checks if dump info becomes obsolete
    :param update_time: dump update time in seconds
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    :return:
    """
    parsed_time = dataprocessing.getLastParsedTime()
    if parsed_time:
        return parsed_time.timestamp() > float(update_time)
    return False


def parse(xmldump, connstr):
    """
    :param xmldump: dump.xml
    :param connstr: smth like "engine://user:pswd@host:port/dbname"
    Parses xml from binary dump has been loaded on init.
    Has much hardcode caused by shitty dump format

    """
    xmlroot = xml.etree.ElementTree.XML(xmldump)

    if xmlroot is None:
        raise RKNDumpFormatException("Parse error: no incorrect dump!")

    counter = 0

    # Getting ID:Hash dict
    outerHashes = dataprocessing.getOuterIDHashes()

    # Creating new dump info record
    dump_id = dataprocessing.addDumpInfoRecord(**xmlroot.attrib)

    # Filling tables
    for content in xmlroot.iter('content'):
        dump_outer_id = int(content.attrib['id'])
        dump_hash = content.attrib['hash']
        # BTW, we don't consider hashes in dump to be null.
        if outerHashes.get(dump_outer_id) == dump_hash:
            outerHashes.pop(dump_outer_id)
            # Don't touch the entries not having been changed
            continue
        else:
            if outerHashes.get(dump_outer_id) is not None:
                # Divergence
                dataprocessing.delContent(dump_outer_id)
                outerHashes.pop(dump_outer_id)
            # We've got new content entry. Importing decision
            des = content.find('decision')
            if des is None:
                raise RKNDumpFormatException("Parse error: no Decision for content id: " + content.attrib['id'])
            decision_id = dataprocessing.addDecision(**des.attrib)  # date, number, org
            # Importing content
            content_id = dataprocessing.addContent(dump_id, decision_id, **content.attrib)

        # resourses parsing...
        # walking through the available tags
        for tag in ('url', 'domain', 'ip', 'ipSubnet', 'ipv6', 'ipv6Subnet'):
            for element in content.iter(tag):

                entitytype = None

                if tag == 'url':
                    if str(element.text).find('https') == 0:
                        entitytype = 'https'
                    else:
                        entitytype = 'http'
                    value = parseutils.urlHandler(element.text)

                elif tag == 'domain':
                    # Why wouldn't be used content.attrib['blockType'] instead?
                    # Because domain tags don't depend on content blocktype.
                    if not parseutils.isdomain(element.text):
                        continue
                    if '*.' in str(element.text):
                        entitytype = 'domain-mask'
                        # Truncating *.
                        value = parseutils.punencodedom(
                            parseutils.domainCorrect(element.text)[2:])
                    else:
                        entitytype = 'domain'
                        value = parseutils.punencodedom(
                            parseutils.domainCorrect(element.text))

                elif tag == 'ip':
                    if parseutils.checkIp(element.text):
                        entitytype = 'ip'
                        value = element.text

                elif tag == 'ipSubnet':
                    if parseutils.checkIpsub(element.text):
                        entitytype = 'ipsubnet'
                        value = element.text

                elif tag == 'ipv6':
                    if parseutils.checkIpv6(element.text):
                        entitytype = 'ipv6'
                        value = element.text

                elif tag == 'ipv6Subnet':
                    if parseutils.checkIpv6sub(element.text):
                        entitytype = 'ipv6subnet'
                        value = element.text

                else:
                    continue

                if entitytype is not None:
                    dataprocessing.addResource(content_id=content_id,
                                         last_change=element.attrib.get('ts'),
                                         entitytype=entitytype,
                                         value=value)

    # There are content rows have been removed remain.

    dataprocessing.updateContentPresence(dump_id, set(outerHashes.keys()))
    # Set dump entry parsed.
    dataprocessing.setDumpParsed(dump_id)

    dataprocessing.commitChanges()

    return True
