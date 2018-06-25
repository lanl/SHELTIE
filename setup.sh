#!/bin/bash

<<<<<<< HEAD
#if we passed in the path to the logging repo
if [ ! -z "$1" ]; then
	LOGGING_REPO="$1"
	cd $LOGGING_REPO
fi
#otherwise this should have been run in
#the logging repo, so either way we're
#in it now

#so get the logging repo's absolute path
LOGGING_REPO=$PWD

#but either way the logging repo should
#be called logs, and just below the top
#level directory of the main repo
MAIN_REPO="$LOGGING_REPO"/..

echo "This will setup the logging repo in $LOGGING_REPO"
echo "with the main repo being in $MAIN_REPO."
echo "Is this okay? (y/n)"

while [ "$continue" != 'y' ] \
	 && [ "$continue" != 'n' ]; do
	read continue
done

if [ $continue = 'n' ]; then
	exit 1
fi

#NOTE: we assume both the logging and main directory exist
#      and that the main directory is already initialised

#switch over to main repo
#cd $MAIN_REPO

#switch back to the logging repo
#cd $LOGGING_REPO

if [ -d "$LOGGING_REPO"/.git ]; then
	
	while [ "$overwrite_history" != 'y' ] \
	   && [ "$overwrite_history" != 'n' ]; do
		echo "Git is already setup in the logging repo."
		echo "Would you like to overwrite the git history? (y/n)"
		echo "(Recommended ONLY for first-time settup)"
		read overwrite_history
	done

	if [ "$overwrite_history" = 'y' ]; then
		#get rid of the history
		rm -rf .git
		
		#recreate the repo with only its current contents
		git init
		git add .
		git commit -m 'initial commit'
	fi

else
	#create the repo
	git init
	git add .
	git commit -m 'initial commit'
fi

#copy over the log-side hook
cp $LOGGING_REPO/prepare-commit-msg-logging \
   $LOGGING_REPO/.git/hooks/prepare-commit-msg
#make sure the hook is executable
chmod +x $LOGGING_REPO/.git/hooks/prepare-commit-msg

#setup the main repo hooks
for hook in commit-msg post-commit post-checkout ; do
	#move over the main-repo-side hooks
	cp $LOGGING_REPO/$hook-main $MAIN_REPO/.git/hooks/$hook
	#make sure the hooks are executable
	chmod +x $MAIN_REPO/.git/hooks/$hook
=======
#NOTE: this should be run from the logging script repo
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
	#provide help info
	echo "Sets up the logging scripts in the main repo."
	echo "Intended to be run in the same directory as the logging scripts."
	echo "Usage: setup.sh [main-repo-path] [-h] [--help]"
	echo "main-repo-path [optional] - the path to the top level of"
	echo "                            the main repo; uses the level"
	echo "                            above the current directory"
	echo "                            by default"
	echo "-h --help - displays this help message"
elif [ -z "$1" ]; then
	#if we don't have a positional argument,
	#use the level above this by default
	MAIN_REPO=..
else
	#if we have a positional argument passed in,
	#interpert it as the path to the main repo
	MAIN_REPO=$1
fi

#setup the main repo hooks
for hook in commit-msg post-commit ; do
	hook_copy=$MAIN_REPO/.git/hooks/$hook

	#move over the main-repo-side hooks
	cp $hook $hook_copy 
	
	#make sure LOG variable line up in all the hooks
	sed -i "3iLOG=.commit.log" $hook_copy

	#make sure the hooks are executable
	chmod +x $hook_copy
>>>>>>> feature
done
