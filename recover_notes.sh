#!/bin/bash

NOTES_REF=refs/notes/productivity
LOG_PATH=.temp.log

REPO_PATH="$1"
if [ -z "REPO_PATH" ]; then
    exit 1
fi
cd "$REPO_PATH"

UNREACHABLE_COMMITS=$(git fsck --unreachable --no-reflogs 2> /dev/null | grep "commit" | awk '{print $3}')
BRANCHES=$(git branch)
BRANCHES=${BRANCHES/\*/}
#REACHABLE_COMMITS=$(git rev-parse $BRANCHES)
echo $UNREACHABLE_COMMITS
#$echo $REACHABLE_COMMITS

echo "unreachable commits are:"
for COMM in $UNREACHABLE_COMMITS #$REACHABLE_COMMITS
do
    echo $COMM

    ANNOTATED_COMMIT=`git show ${COMM} | grep "+++" | awk '{print $2}' | sed "s/b\///g"`
    
		#these are just COMM
		#PARTIAL_PARENT_HASH=`git show ${COMM} | grep "index " | awk '{print $2}' | sed "s/.*\.\.//g"`
    #PARENT_HASH=`git log -n 1 --format=%H $COMM`

    RAW_MESSAGE=$(git log -n 1 --format=%B $COMM)

    echo "   -- Annotated commit hash: ${ANNOTATED_COMMIT}"
		#echo "   -- Parent hash: ${PARENT_HASH}"
    echo "   -- Message was: ${RAW_MESSAGE}"

		if [ "$RAW_MESSAGE" = "Notes added by 'git notes add'" ]; then
			LOG=$(git show f57d98e7c6c303d73917a8a9036585edf4168198 | egrep "^\+" | grep -v "+++" | cut -c2-)
			echo ${LOG} >> ${LOG_PATH}
			git notes --ref ${NOTES_REF} add -f -F ${LOG_PATH} ${ANNOTATED_COMMIT}
			rm ${LOG_PATH}
		fi

    # This copying doesn't work yet...
    #echo "Copying commit..."
    #git notes show ${NOTE_HASH} >> productivity_${PARENT_HASH}.md
    #git notes add -F productivity_${PARENT_HASH}.md -m ${RAW_MESSAGE}

done
