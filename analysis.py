#!/usr/bin/env python2

from test_json import test_json
from cleansing import parse_sublogs, build_graph

import os.path
import subprocess
import sys
import json
import argparse
from git import Repo
import re
import pprint
import git
import matplotlib
import binascii

parser = argparse.ArgumentParser()
parser.add_argument("repo_dir", help="The repo that contains the productivity logs as notes")
args = parser.parse_args()

if(not os.path.isdir(os.path.join(args.repo_dir, ".git"))):
  print "Cannot find %s directory. Not a git repo." % os.path.join(args.repo_dir, ".git")
  sys.exit(1)

PRODUCTIVITY_NOTES_NAMESPACE="refs/notes/productivity"

repo = Repo(args.repo_dir)

#commits = list(repo.iter_commits("sharrell"))
commits = list(build_graph(repo).nodes)

#git notes --ref refs/notes/productivity show
# git notes --ref refs/notes/productivity show eaa1b0f4a7ee65ab33d0ec0e28f6fdc04fd8fbe2
logs = []
for commit in commits:
  try:
    logs.append([commit.hexsha, subprocess.check_output(["git", "--git-dir", os.path.join(args.repo_dir, ".git"), "notes", "--ref", PRODUCTIVITY_NOTES_NAMESPACE, "show", commit.hexsha])])
  except:
		pass
log_list = []
for hexsha, log in logs:	
	try:
		for sublog in parse_sublogs(log):
			log_list.append([hexsha, sublog])	
	except:
		print(hexsha)

import pprint
pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(log_list)
lines_per_commit = []
total_time_per_commit = []

for log in log_list:
    report = log[1]['log']
    if not 'user_responses' in report: continue
    if len(report) == 0: continue
    user_responses = report['user_responses']


    if len(user_responses) == 1: continue
    time_categories = report['user_responses']['time_categories']
    #nasa_tlx = report['NASA-TLX']

    for category in time_categories:
        if 'refectoring' in category: break
    else:
        time_categories['refactoring'] = {u'time_spent': 0.0, u'difficulty': 0}
    #pp.pprint(log)
    total_time = (time_categories['planning']['time_spent'] + 
            time_categories['coding']['time_spent'] + 
            time_categories['refactoring']['time_spent'] + 
            time_categories['debugging']['time_spent'] + 
            time_categories['optimising']['time_spent'])
    total_time_per_commit.append(total_time)
    commit = git.Commit(repo, binascii.unhexlify(log[0]))
    lines_changed = 0
    print commit.diff(commit.parents[0])[0].diff
    diff = subprocess.check_output(["git", "--git-dir", os.path.join(args.repo_dir, ".git"),  'diff', commit.hexsha, commit.parents[0].hexsha])
    sloc = 0
    for line in diff.split('\n'):
        if not (line.startswith("-") or line.startswith("+")): continue
        if line.strip() == "+" or line.strip() == "-": continue
        if line.startswith('+++') or line.startswith('---'): continue
        sloc += 1

    total_time_per_commit = sloc

