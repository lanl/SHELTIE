#!/usr/bin/env python2

from test_json import test_json

import os.path
import subprocess
import sys
import json
import argparse
from git import Repo

def peek(l):
	if l:
		return l[-1]
	else:
		return None, None

def listify(log_str):
	print('starting sanitation work')
	#convert the log string to a list
	log_list =list(log_str)
	list_offset = 0
	#create an empty stack
	stack = []
	for str_i in range(len(log_str)):
		list_i = list_offset + str_i
		c = log_str[str_i]
		if c == ':':
			#push a ':' onto the stack
			stack.append((list_i, ':'))
		elif c == ',':
			#peek the stack
			last_list_i, last_c = peek(stack)

			#if we pushed a ':' last...
			if last_c == ':':
				#...put a '[' after it in the list
				log_list.insert(last_list_i + 1 ,'[')
				#update the offset
				list_offset += 1				
				list_i += 1

				#then push a '[' onto the stack
				stack.append((last_list_i + 1, '['))

			#push a ',' onto the stack
			stack.append((list_i, ','))
			
		elif c == '}':
			#peek the stack
			last_list_i, last_c = peek(stack)

			#if we pushed a '[' last...
			if last_c == '[':
				#...put a ']' before the current '}' in the list
				log_list.insert(list_i, ']')
				#update the offset
				list_offset += 1

				#then pop the '[' from the list
				stack.pop()
			
			#peek the stack
			last_list_i, last_c = peek(stack)
			
			#we should have a ':' on the top of the stack now
			if last_c == ':':
				#so if we do, pop it off
				stack.pop()
			else:
				#and we want to know if that's not the case
				print(''.join(log_list[last_list_i - 20 : last_list_i + 20]))
			
			#now push a '}' unto the stack
			stack.append((list_i, '}'))
		
		elif c == '{':
			#peek stack
			last_list_i, last_c = peek(stack)

			#a '{' shouldn't come immediately after a '}'
			#so if we pushed one last...
			if last_c == '}':
				#...then we need to add a ',' after it
				log_list.insert(last_list_i + 1, ',')
				#update the offset
				list_offset += 1
			
				#and the we should pop it
				stack.pop()
	
				#now we need to proceed as if we just found a ','
				#so hold onto the index of the ',' we just inserted
				list_i = last_list_i + 1
				
				#peek the stack
				last_list_i, last_c = peek(stack)

				#if we pushed a ':' last...
				if last_c == ':':
					#...put a '[' after it in the list
					log_list.insert(last_list_i + 1 ,'[')
					#update the offset
					list_offset += 1				
					list_i += 1

					#then push a '[' onto the stack
					stack.append((last_list_i + 1, '['))
			#also, we just push ','s as buffers between '}' and '{'
			#so if we pushed one last...
			elif last_c == ',':
				#...we should pop it
				stack.pop()
			 
	return ''.join(log_list)

def add_top_level(log_str):
	log_list = list(log_str)
	list_offset = 0
	
	return '{"log":' + ''.join(log_list) + '}'

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


test_json = test_json.replace("\n", "")

#print test_json

json_productivity_log = test_json

try:
  print json.loads(json_productivity_log)
except ValueError:
  # Fix bad commit logs  
  #json_productivity_log = json_productivity_log.replace('"user_responses":', '"user_responses":[')
  #json_productivity_log = json_productivity_log.replace('"time_categories":', '"time_categories":[')
	json_productivity_log = add_top_level(json_productivity_log)
	json_productivity_log = listify(json_productivity_log)
	print(json_productivity_log[760:770])
	print(json.loads(json_productivity_log))
