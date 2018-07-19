#!/usr/bin/env python2

from test_json import test_json
from cleansing import parse_and_clean

import os.path
import subprocess
import sys
import json
import argparse
from git import Repo
import re
import pprint	

parser = argparse.ArgumentParser()
parser.add_argument("repo_dir", help="The repo that contains the productivity logs as notes")
args = parser.parse_args()

if(not os.path.isdir(os.path.join(args.repo_dir, ".git"))):
  print "Cannot find %s directory. Not a git repo." % os.path.join(args.repo_dir, ".git")
  sys.exit(1)

PRODUCTIVITY_NOTES_NAMESPACE="refs/notes/productivity"

repo = Repo(args.repo_dir)

commits = list(repo.iter_commits("sharrell"))

#git notes --ref refs/notes/productivity show
# git notes --ref refs/notes/productivity show eaa1b0f4a7ee65ab33d0ec0e28f6fdc04fd8fbe2
logs = []
for commit in commits:
  try:
    logs.append(subprocess.check_output(["git", "--git-dir", os.path.join(args.repo_dir, ".git"), "notes", "--ref", PRODUCTIVITY_NOTES_NAMESPACE, "show", commit.hexsha]))
  except:
      pass

log_list = []
for json_productivity_log in logs:
	sublogs = re.split(r'productivity log for commit [0-9a-f]* in branch \w*', json_productivity_log, re.MULTILINE)
		
	for sublog in sublogs:
		log_list.append(parse_and_clean(sublog))	
import pprint
pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(log_list)

for log in log_list:
    report = log['log']
    if len(report) == 0: 
        pp.pprint(log)
        continue
    if 'user_responses' not in report[0]: 
        pp.pprint(log)
        continue
    user_responses = report[0]['user_responses']
    if len(user_responses) == 1: continue
    time_categories = report[0]['user_responses'][1]['time_categories']
    #nasa_tlx = report['NASA-TLX']

    for category in time_categories:
        if 'refectoring' in category: break
    else:
        time_categories.append({'refactoring': [{u'time_spent': 0.0},{u'difficulty': 0}]})

    total_time = (time_categories[0]['planning'][0]['time_spent'] + 
            time_categories['coding']['time_spent'] + 
            time_categories['refactoring']['time_spent'] + 
            time_categories['debuging']['time_spent'] + 
            time_categories['optimising']['time_spent'])
    print total_time
