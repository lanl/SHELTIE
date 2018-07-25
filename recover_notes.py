#!/usr/bin/env python2

import sys
import os.path
import subprocess
import cleansing

repo_path=sys.argv[1]
git_path=os.path.join(repo_path, '.git')
output = subprocess.check_output(["git", "--git-dir", git_path, "fsck"])
lines = output.split('\n')
for line in lines:
	if line:
		dangling, obj_type, obj_hash = line.split(' ')
		try:
			raw_log = subprocess.check_output(["git", "--git-dir", git_path, "show"]) 
			log_json = cleansing.parse_sublogs(raw_log)[0]
			commit_hash = log_json['log']['auto_generated']['git_info']['commit_hash']
			print(commit_hash)
		except Exception as e:
			print(e)
			continue
