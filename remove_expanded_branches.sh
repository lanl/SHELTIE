#!/bin/bash

#switch into the specified dir
cd "$1"

ON_A_PROD_BRANCH=`git branch --list productivity_log_* | grep '\*'`

if [ ! -z "${ON_A_PROD_BRANCH}" ]; then
    echo "You are currently on a productivity_log branch. Change branches before running this cleanup script."
    exit
fi

#get rid of the extra files (seems to interfere with branch removal)
rm productivity_log_*

BRANCH_LIST=`git branch --list productivity_log_*`
echo "$BRANCH_LIST"

for BR in $BRANCH_LIST
do
    git branch -D $BR &> /dev/null
done
