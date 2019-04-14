# SHELTIE

![logo](./docs/logo.png)

Simple Hooks Enabling Logging Techniques through an Interactive Experience (SHELTIE)

SHELTIE is comprised of a series of git hooks for collecting productivity
measures as a part of a workflow using git (a version control system). Setup
scripts for configuring a given project for logging are also included, as are
post-processing scripts for consolidating, visualizing, and analyzing the data
collected.

## Overview:

This repo contains a few scripts designed to enable productivity
logging on a git repo. Most are git hooks, which will be automatically
executed by git after a commit is made.

## Dependencies:
  
- `bash` (or similar shell): to execute hooks scripts
- `git`: this repo extends git's functionality
- `git notes`: for storing logs (should come by default with newer versions of git)

## Setup:

- run setup.sh, optionally passing in the path to the main repo setup.sh <main
   repo path> [by default, <main repo path> is one level above where setup.sh
   is stored]

## Usage:

###  Basic Usage 

Once a repo is configured for logging, (see Setup), just commit like normal!
After you finalize your commit message, you will be asked if you would like to
create a commit log. If you answer yes, you will be prompted to answer a few
quick questions about the work you just committed. After answering, your commit
will proceed like normal. Behind the scenes, though, your answers, plus a few
pieces of metadata which are gathered automatically will be stored 
as a git note on your commit.

### Viewing Logs 

You can view the log entries for a given commit using the command git notes
--ref refs/notes/productivity show <commit hash> ommiting <commit hash> will
show the log for the current HEAD.

To see a list of all the log entries, simply run list_notes.sh

### Editing Logs 

Similarly, if you ever need to make changes to your logs, (for instance, if you
entered a value wrong, or there was sensitive information in your commit message)
you can edit the log file for a specific commit using the command
git notes --ref refs/notes/productivity edit <commit hash>
as above, omitting <commit hash> will allow you to edit the log for the
current HEAD.

### Customisation:

You can change the specific areas you will be asked about by editing
the lists at the top of commit-msg, and then rerunning setup.sh to get
the new version of that script into the hooks folder.

## Copyright

© (or copyright) 2019. Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for
Los Alamos National Laboratory (LANL), which is operated by Triad National
Security, LLC for the U.S. Department of Energy/National Nuclear Security
Administration. All rights in the program are reserved by Triad National
Security, LLC, and the U.S. Department of Energy/National Nuclear Security
Administration. The Government is granted for itself and others acting on its
behalf a nonexclusive, paid-up, irrevocable worldwide license in this material
to reproduce, prepare derivative works, distribute copies to the public,
   perform publicly and display publicly, and to permit others to do so.

This is open source software; you can redistribute it and/or modify it under
the terms of the BSD-3 License. If software is modified to produce derivative
works, such modified software should be clearly marked, so as not to confuse it
with the version available from LANL.
