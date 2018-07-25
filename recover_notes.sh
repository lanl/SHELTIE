#!/bin/bash

REPO_PATH="$1"
if [ -z "REPO_PATH" ]; then
    exit 1
fi
cd "$REPO_PATH"

UNREACHABLE_COMMITS=`git fsck --unreachable --no-reflogs 2> /dev/null | grep "commit" | awk '{print $3}'`

echo "unreachable commits are:"
for COMM in $UNREACHABLE_COMMITS
do
    echo $COMM

    NOTE_HASH=`git show ${COMM} | grep "+++" | awk '{print $2}' | sed "s/b\///g"`
    PARTIAL_PARENT_HASH=`git show ${COMM} | grep "index " | awk '{print $2}' | sed "s/.*\.\.//g"`
    PARENT_HASH=`git log -n 1 --format=%H $COMM`

    RAW_MESSAGE=`git log -n 1 --format=%B $COMM`

    echo "   -- Note hash: ${NOTE_HASH}"
    echo "   -- Parent hash: ${PARENT_HASH}"
    echo "   -- Message was: ${RAW_MESSAGE}"

    # This copying doesn't work yet...
    #echo "Copying commit..."
    #git notes show ${NOTE_HASH} >> productivity_${PARENT_HASH}.md
    #git notes add -F productivity_${PARENT_HASH}.md -m ${RAW_MESSAGE}

done
