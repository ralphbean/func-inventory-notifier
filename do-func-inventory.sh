#!/bin/bash

# List of addresses who should get mail
addrs=ralph.bean@gmail.com
now=`date +'%m-%d-%y %H:%M:%S'`

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

# Do a func inventory except the modules 'mount' and 'iptables'
#  They tend to be updated -all the time- and spam us.  :(
func-inventory --modules=filetracker,hardware,service,system,rpms


# Check and see if any git changes were made
git --git-dir=/var/lib/func/inventory/.git log \
        -p \
        --since="5 minutes ago" \
        --color \
        > $tmpfile

# Were any made?
nlines=`wc -l $tmpfile | awk ' { print $1 } '`
if [ "$nlines" -eq "0" ] ; then
    logger -s "[func-master-flex]  No changes detected.  Sleeping."
else
    logger -s "[func-master-flex] CHANGE DETECTED in func-inventory."

    # HTML Colorize this biz
    /root/configuration-projects/func-master-flex/ansi2html.sh --bg=dark \
            < $tmpfile > $tmpfile.html
    # Pretty it up.
    /usr/bin/tidy -o $tmpfile.html.tidied -f /dev/null $tmpfile.html

    # Send an HTML mail
    echo "Subject: func-inventory report ($now)" > $tmpfile.mailfile
    echo "From: 'func-master-flex' <root@craftsman>" >> $tmpfile.mailfile
    echo "MIME-Version: 1.0" >> $tmpfile.mailfile
    echo "Content-Type: text/html; charset=us-ascii" >> $tmpfile.mailfile
    echo "Content-Disposition: inline" >> $tmpfile.mailfile
    cat $tmpfile.html.tidied >> $tmpfile.mailfile
    for addr in $addrs; do
        cat $tmpfile.mailfile | /usr/sbin/sendmail $addr
    done
    rm $tmpfile.mailfile
    rm $tmpfile.html
    rm $tmpfile.html.tidied
fi
rm $tmpfile
