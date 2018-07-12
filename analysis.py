#!/usr/bin/env python2

from test_json import test_json

import os.path
import subprocess
import sys
import json
import argparse
from git import Repo
import re

def peek(l):
	if l:
		return l[-1]
	else:
		return None, None

def clean_term(term):
	term_parts = term.split(':')
	key, value = term_parts[0], ':'.join(term_parts[1:])

	#make sure subterms within term are comma separated
	if re.search(r'\{.*\}\s*\{.*\}', value):
		value = re.sub(r'\}\s*\{', '},{', value)

	#enclose lists
	if re.search(r'\{.*\}\s*,\s*\{.*\}', value) \
	   and not re.match(r'\s*\[.*\]', value):
		value = '[{}]'.format(value)
		#print('list enclosed: {}'.format(value))

	#remove trailing comma in list
	elif re.search(r',\s*\]', value):
		match = re.search(r',\s*]', value).group(0)
		#try not to make the value string any shorter
		substitute = ' ' * (len(match) - 1) + ']'
		value = re.sub(r',\s*]', substitute, value)
		#print('trailing comma removed: {}'.format(value))		

	#quote non-numberic values which aren't already quoted
	elif not re.match(r'\s*".*"', value):	
		try:
			float(value)
		except:
			value = '"{}"'.format(value)
			#print('non-numerical literal quoted: {}'.format(value))
	
	#if we're doing this right, value should be parsable
	try:
		json.loads(value)
	except:
		#print(value)
		raise ValueError('value not parsable')

	return '{}:{}'.format(key, value)

closure_pairs = {'{':'}'}
                 #'[':']'}
                 #'"':'"'}
def clean_json(old_log): 
	#convert the log string to a list
	new_log = old_log
	#keep track of the difference between the lengths of the two logs
	list_offset = 0
	#create an empty stack
	stack = []
	for i in range(len(old_log)):
		c = old_log[i]
		new_i = i + list_offset
		top_new_i, top_c = peek(stack)

		#if c finishes the last closure pairing
		if top_c in closure_pairs \
		   and closure_pairs[top_c] == c:
			stack.pop()
			
			#extract json term without enclosing {}
			term = new_log[top_new_i + 1 : new_i]
				
			try:
				json.loads('{' + term + '}')
			except:
				#print('{' + term + '}', list_offset, term_offset)
				
				#clean terms that won't load
				new_term = clean_term(term)
				new_log = new_log.replace(term, new_term)
			
				#update offsets
				d_len = len(new_term) - len(term)
				term_offset += d_len #update the offset for the top element on the stack
				list_offset += d_len
				new_i = i + list_offset

		#otherwise, if c starts a closure pairing
		elif c in closure_pairs:
			#push c onto the stack
			stack.append((new_i, c))

			#reset the term offset
			term_offset = 0
	
	#print(stack)
	return ''.join(new_log)

def add_top_level(log):
	#TODO: check whether or not log already has a top level
	#in the general case
	if re.match(r'\s*\{\s*"log"\s*:', log):
		return log
	else:
		#print('added top level')
		return '{"log":' + log + '}'

parser = argparse.ArgumentParser()
parser.add_argument("repo_dir", help="The repo that contains the productivity logs as notes")
args = parser.parse_args()

if(not os.path.isdir(os.path.join(args.repo_dir, ".git"))):
  print "Cannot find %s directory. Not a git repo." % os.path.join(args.repo_dir, ".git")
  sys.exit(1)

PRODUCTIVITY_NOTES_NAMESPACE="refs/notes/productivity"

repo = Repo(args.repo_dir)

commits = list(repo.iter_commits("master"))
#list(repo.iter_commits("kokkos_advance_b"))

#git notes --ref refs/notes/productivity show
#for commit in commits[:5]:
#  try:
#    print subprocess.check_output(["git", "--git-dir", os.path.join(args.repo_dir, ".git"), "notes", "--ref", PRODUCTIVITY_NOTES_NAMESPACE, "show", commit.hexsha])
#  except:
#      pass


for json_productivity_log in test_json:
	json_productivity_log = json_productivity_log.replace("\n", "")

	try:
		print json.loads(json_productivity_log)
	except ValueError:
		# Fix bad commit logs  
		json_productivity_log = add_top_level(json_productivity_log)
		json_productivity_log = clean_json(json_productivity_log)
		#print(json_productivity_log[1124:207529])
		print(json.loads(json_productivity_log))
