from functools import reduce


# Not used
def mergednsmap(iswc, dnslst):
    """
    Not used to avoid 2 function calls, and array walking twice
    :param iswc: Is wildcards needed, True/False
    :param dnslst: the list of domains-as-suffix-list
    :return: the set of domains
    """
    merger = lambda lst: ".".join(lst[:-2].__reversed__()) if lst[-1] == iswc else None
    return set(map(merger,dnslst)) - {None}


def dnslistmerged(dnslist, wc_asterize=False):
    """
    Makes textual domain from suffixes list for each in he given list
    :param dnslist: the list of domains-as-suffix-list
    :param wc_asterize: appending *. to each wildcard domain
    :return: two sets, domains and wdomains
    """
    domains = set()
    wdomains = set()
    # Setting wildcard asterisk prefix if required
    wc_sign = ''
    if wc_asterize:
        wc_sign = '*.'

    for d in dnslist:
        if d[-1]:
            wdomains.add(wc_sign + ".".join(d[:-2].__reversed__()))
        else:
            domains.add(".".join(d[:-2].__reversed__()))
    return domains, wdomains


def mapdnstree(dnstree):
    """
    Restores each domain in the given DNSD tree as a list of suffixes.
    Each entry of the returned list is finished with "" as a terminator
    and boolean indicator of wildcardness:
    [['com','domain','sub','',False], ...]
    :param dnstree: DNS tree
    :return: domain entries as suffixes list
    """
    return [
        [k,v] for k,v in dnstree.items()
        if type(v) != dict
            ] + \
        reduce(lambda x,y: x+y,
           map(lambda x: [[x[0]]+i for i in x[1]],
               [[k,mapdnstree(v)] for k,v in dnstree.items()
                if type(v) == dict]
               ),
           [])


def mkdnstree(domains, wdomains):
    """
    Makes DNS tree starting from 0LD as empty string.
    Each leaf ends up with auxiliary {'': bool} attribute
    to differ an entry from its subdomain and to distinguish
    wildcard domains which excludes entire subtree itself.
    :param domains: domains iterable
    :param wdomains: wdomains iterable
    :return:
    """
    dnstree = {"": {}}
    for d in domains:
        dnstree_ptr = dnstree.setdefault("")
        for i in d.split('.').__reversed__():
            dnstree_ptr = dnstree_ptr.setdefault(i, {})
        dnstree_ptr[""] = False

    for w in wdomains:
        dnstree_ptr = dnstree.setdefault("")
        for i in w.split('.').__reversed__():
            dnstree_ptr = dnstree_ptr.setdefault(i, {})
        dnstree_ptr.clear()
        dnstree_ptr[""] = True
    return dnstree


def strcut(x, s):
    """
    Beheads x of s, e.g.: 'stringstr', 'str' -> 'ingstr'
    :param x: stripped string
    :param s: stripping string
    """
    return x[len(s):] if x.find(s) == 0 else x
