#!/bin/bash
NOTES_REF=refs/notes/productivity

NOTES_LIST=`git notes --ref $NOTES_REF list`

ORIG_IFS=$IFS
NEWLINE_IFS=$'\n'

CUR_BRANCH=`git branch | grep "\*" | awk '{print $2}'`
if [ "$CUR_BRANCH" == "(HEAD" ]; then
    CUR_BRANCH=`git log --format=%h -n 1`
    echo " Not on a branch currently. Head is detached at: $CUR_BRANCH"
else
    echo " Expanding notes into branches. Currently on branch $CUR_BRANCH"
fi

IFS=$NEWLINE_IFS

for NOTE in $NOTES_LIST
do
    COMMIT_HASH=`echo $NOTE | awk '{print $2}'`
    NOTE_HASH=`echo $NOTE | awk '{print $1}'`
    echo "Commit: $COMMIT_HASH -- Note: $NOTE_HASH"

    BR_NAME=productivity_log_${COMMIT_HASH}
    LOG_NAME=productivity_log_${NOTE_HASH}

    # Create branch for producitivty log
    git branch $BR_NAME ${COMMIT_HASH} &> /dev/null
    git checkout $BR_NAME &> /dev/null

    # Create a text file with the note in it
    touch $LOG_NAME
    git notes --ref $NOTES_REF show ${COMMIT_HASH} >> $LOG_NAME
    git add $LOG_NAME &> /dev/null
    git commit --no-verify $LOG_NAME -m "Expanded productivity log from note $NOTE_HASH to $LOG_NAME" &> /dev/null
done

git checkout $CUR_BRANCH &> /dev/null

IFS=$ORIG_IFS
