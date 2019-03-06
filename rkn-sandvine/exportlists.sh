#!/bin/bash

./rkn-sandvine.py
EXPATH="tmp"
EXLIST="domains.lst https.lst ips.lst ipv6s.lst urls.lst wdomains.lst"
EXUSER=root
ID_RSA_PATH=id_rsa
SRVLIST="10.1.20.114 10.1.20.115 10.1.20.82 10.1.20.83"
SRVPATH="/usr/local/sandvine/etc"
RELOADCMD="svcli -c reload maps"

for s in $SRVLIST; do \
  echo "Serving node $s..."
  for i in $EXLIST; do \
    scp -C -i $ID_RSA_PATH "$EXPATH/$i" "$EXUSER@$s:$SRVPATH/";
    ssh -i $ID_RSA_PATH "$EXUSER@$s" "$RELOADCMD";
  done
done
