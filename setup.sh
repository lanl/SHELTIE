#!/bin/bash

LOGS_REF=refs/notes/productivity

#cd into the directory where this script is stored
cd "${BASH_SOURCE%/*}" || exit

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
	#provide help info
	echo "Sets up the logging scripts in the specified repo."
	echo "Intended to be run in the same directory as the logging scripts."
	echo "Usage: setup.sh [main-repo-path] [-h] [--help]"
	echo "main-repo-path [optional] - the path to the top level of the main repo;"
	echo "                            uses the level above the current directory"
	echo "                            by default"
	echo "-h --help - displays this help message"
	exit 0
elif [ -z "$1" ]; then
	#if we don't have a positional argument,
	#use the level above this by default
	MAIN_REPO=..
else
	#if we have a positional argument passed in,
	#interpert it as the path to the main repo
	MAIN_REPO=$1
fi

echo "Starting setup"
#setup the main repo hooks
for hook in commit-msg post-commit ; do
	echo "Starting setup for $hook"	

	hook_copy=$MAIN_REPO/.git/hooks/$hook

	#move over the main-repo-side hooks
	cp $hook $hook_copy
	printf "\t$hook copied to $hook_copy\n" 
	
	#make sure LOG variable line up in all the hooks
	#sed -i "3iLOG=.commit.log" $hook_copy

	#make sure the hooks are executable
	chmod +x $hook_copy
	printf "\t$hook_copy is now executable\n"
	
	#let the user know that the hook was configured properly
	echo "Setup complete for $hook"
done

#remove any depricated hooks
for hook in $MAIN_REPO/.git/hooks/{pre-push} ; do
  if [ -f "$hook" ]; then
    rm "$hook"
    echo "removed depricated hook $hook"
  fi
done

echo "Setup complete for all hooks"

#switch into main repo
cd $MAIN_REPO

#clear the existing notes merge strategy
git config --unset-all notes.mergeStrategy
#set the merge strategy for notes
git config --add notes.mergeStrategy "union"

#make sure that the logs will be properly conncatenated during a rebase
#by adding LOGS_REF to notes.rewriteRef, if it isn't already in it
REWRITE_REF=$(git config --get notes.rewriteRef)

if [ -z "$REWRITE_REF" ] ; then
	#if rewriteRef not set, just set it to LOGS_REF
	git config --unset-all notes.rewriteRef
	git config --add notes.rewriteRef "$LOGS_REF"
else
	#otherwise, make sure LOGS_REF isn't already in REWRITE_REF
	REWRITE_REF_LIST=${REWRITE_REF//,/ }

	logs_ref_found=false
	for ref in $REWRITE_REF_LIST ; do
		
		if [[ "$LOGS_REF" = "$ref" ]]; then
			logs_ref_found=true
		fi

	done

	#if LOGS_REF isn't already in there, add it
	if ! $logs_ref_found ; then
		git config --unset-all notes.rewriteRef
		git config --add notes.rewriteRef "$REWRITE_REF,$LOGS_REF"
	fi
fi

for remote in $(git remote) ; do
	#get git to fetch logs along with everything else
	FETCH_CONFIG=$(git config --get remote."$remote".fetch) 
	if [[ $FETCH_CONFIG = *+refs/notes/productivity:refs/remotes/"$remote"/notes/productivity* ]] ; then
		echo "remote $remote already fetching logs"
	else
		git config --add remote."$remote".fetch +refs/notes/productivity:refs/remotes/"$remote"/notes/productivity
		echo "remote $remote configured to fetch logs"
	fi
	
	#get git to push logs along with everything else
	PUSH_CONFIG=$(git config --get remote."$remote".push) 
	if [[ $PUSH_CONFIG = *refs/notes/productivity:refs/notes/productivity* ]] ; then
		echo "remote $remote already pushing logs"
	else
		git config --add remote."$remote".push refs/notes/productivity:refs/notes/productivity
		echo "remote $remote configured to push logs"
	fi
done

#REWRITE_REF_CONFIG=$(git config --get 

echo "setup complete"
