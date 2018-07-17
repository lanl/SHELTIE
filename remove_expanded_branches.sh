#!/bin/bash

ON_A_PROD_BRANCH=`git branch --list productivity_log_* | grep '\*'`

if [ ! -z "${ON_A_PROD_BRANCH}" ]; then
    echo "You are currently on a productivity_log branch. Change branches before running this cleanup script."
    exit
fi

BRANCH_LIST=`git branch --list productivity_log_*`

for BR in $BRANCH_LIST
do
    git branch -D $BR &> /dev/null
done
