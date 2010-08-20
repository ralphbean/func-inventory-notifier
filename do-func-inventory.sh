#!/bin/bash

# List of addresses who should get mail
addrs=ralph.bean@gmail.com
now=`date +'%m-%d-%y %H:%m:%S'`

# Just a util for getting a random tmpfile
function gettmpfile()
{
      local tmppath=${1:-/tmp}
      local tmpfile=$2${2:+-}
      tmpfile=$tmppath/$tmpfile$RANDOM$RANDOM.tmp
      if [ -e $tmpfile ]
      then
        # if file already exists, recurse and try again
        tmpfile=$(gettmpfile $1 $2)
      fi
      echo $tmpfile
}

tmpfile=$(gettmpfile)

# Check and see if any git changes were made
git --git-dir=/var/lib/func/inventory/.git log \
        -p --since="70 minutes ago" --color > $tmpfile

# Were any made?
nlines=`wc -l $tmpfile | awk ' { print $1 } '`

if [ "$nlines" -eq "0" ] ; then
    logger "[func-master-flex]  No changes detected.  Sleeping."
else
    logger "[func-master-flex] CHANGE DETECTED in func-inventory."

    # HTML Colorize this biz
    /root/configuration-projects/func-master-flex/ansi2html.sh \
            < $tmpfile > $tmpfile.html

    # Send an HTML mail
    echo "Subject: func-inventory report ($now)" > $tmpfile.header
    echo "From: 'func-master-flex' <root@craftsman>" >> $tmpfile.header
    echo "MIME-Version: 1.0" >> $tmpfile.header
    echo "Content-Type: text/html" >> $tmpfile.header
    echo "Content-Disposition: inline" >> $tmpfile.header
    for addr in $addrs; do
        (cat $tmpfile.header
         cat $tmpfile.html) | sendmail $addr
    done
fi
