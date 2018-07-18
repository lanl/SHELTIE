#!/usr/bin/env python2

from test_json import test_json

import os.path
import subprocess
import sys
import json
import argparse
from git import Repo
import re
import pprint

def peek(l):
	if l:
		return l[-1]
	else:
		return None, None

#options for should_clean
def is_not_parsable(term, stack):
	try:
		json.loads(term)
		return False
	except ValueError:
		return True

def is_at_top_level(term, stack):
	return len(stack) == 1

def is_inside_top_level_list(term, stack):
	top_i, top_c = peek(stack)
	return top_c == '[' and len(stack) == 1

def is_non_file_list(term, stack):
	term_parts = term[1:-1].split(':')
	key, value = term_parts[0], ':'.join(term_parts[1:])

	#print('checking value: {}'.format(value))
	
	return key != '"files"' \
	   and re.match(r'\s*\[.*\]', value)
	
#options for clean_json
def merge_terms(term, stack):
	term_parts = term.split(':')
	key, value = term_parts[0], ':'.join(term_parts[1:])
	
	term = ' {}:{} '.format(key, value)
	#print('merged term: {}'.format(term))
	return term

def list_to_dict(term, stack):
	term_parts = term.split(':')
	key, value = term_parts[0], ':'.join(term_parts[1:])
	
	#print('orig term: {}'.format(term))
	value = clean_json(value[1:-1], \
	                   closure_pairs={'{':'}'}, \
	                   clean_term=merge_terms, \
	                   should_clean=is_at_top_level)
	value = '{' + value + '}'

	#print('wrapped list: {}'.format(value))

	return '{' + '{}:{}'.format(key, value) + '}'

def clean_json_term(term, stack):
	term_parts = term.split(':')
	key, value = term_parts[0], ':'.join(term_parts[1:])

	#print(term)
	#make sure subterms within term are comma separated
	if re.search(r'\{.*\}\s*\{.*\}', value):
		value = re.sub(r'\}\s*\{', '},{', value)
		#print('added commas: {}'.format(value))
		
	#enclose lists
	if re.search(r'\{.*\}\s*,\s*\{.*\}', value) \
	   and not re.match(r'\s*\[.*\]', value):
		value = '[{}]'.format(value)
		#print('list enclosed: {}'.format(value))

	#remove trailing comma in list
	elif re.search(r',\s*\]', value):
		match = re.search(r',\s*\]', value).group(0)
		#try not to make the value string any shorter
		substitute = ' ' * (len(match) - 1) + ']'
		value = re.sub(r',\s*\]', substitute, value)
		#print('trailing comma removed: {}'.format(value))		

	#remove trailing comma before end of value
	elif re.search(r',\s*$', value):
		match = re.search(r',\s*$', value).group(0)
		#try not to make the value string any shorter
		substitute = ' ' * len(match)
		value = re.sub(r',\s*$', substitute, value)
		#print('trailing comma removed: {}'.format(value))		
		

	#quote non-numberic values which aren't already quoted
	elif not re.match(r'\s*".*"', value):	
		try:
			float(value)
		except:
			value = '"{}"'.format(value)
			#print('non-numerical literal quoted: {}'.format(value))

	term = '{}:{}'.format(key, value)
	term = '{' + term + '}'	

	#if we're doing this right, value should be parsable
	try:
		json.loads(term)
	except:
		print(term)
		raise ValueError('value not parsable')

	return term

def clean_json(old_log, \
	             closure_pairs={'{':'}'}, \
	             should_clean=is_not_parsable, \
	             clean_term=clean_json_term): 
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
			
			#extract json term
			term = new_log[top_new_i : new_i + 1]
					
			if should_clean(term, stack):
				
				#clean terms that won't load
				new_term = clean_term(term[1:-1], stack)
				new_log = new_log.replace(term, new_term)
			
				#update offsets
				d_len = len(new_term) - len(term)
				term_offset += d_len #update the offset for the top element on the stack
				list_offset += d_len
				new_i = i + list_offset
			
			stack.pop()

		#otherwise, if c starts a closure pairing
		elif c in closure_pairs:
			#push c onto the stack
			stack.append((new_i, c))

			#reset the term offset
			term_offset = 0
	
	##print(stack)
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
		sublog = sublog.replace("\n", "")
		sublog = sublog.replace("\t", " ")
		try:
			temp = clean_json(sublog, should_clean=is_non_file_list, clean_term=list_to_dict)
			log_list.append(json.loads(temp))
		except ValueError:
			# Fix bad commit logs  
			#sublog += '}' * 2
			sublog = add_top_level(sublog)
			sublog = clean_json(sublog)
			sublog = clean_json(sublog, should_clean=is_non_file_list, clean_term=list_to_dict)
			print('Log parsed')
			try:	
				log_list.append(json.loads(sublog))
			except ValueError:
				#print(sublog)
				#print(sublog[65800:65900])
				#print(sublog[65888])
				log_list.append(json.loads(sublog))

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
