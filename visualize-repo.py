#!/usr/bin/env python2

from cleansing import parse_and_clean

import git
import networkx
import sys
import matplotlib.pyplot as plt
import subprocess

def build_graph(repo):
	graph = networkx.DiGraph()

	def iter_parents(commit):
		#don't process commits twice
		if commit not in graph.nodes:
			
			graph.add_node(commit)
		
		for parent in commit.parents:
			#print(parent)
			
			#we shouldn't revist edges
			if (commit, parent) not in graph.edges:
				graph.add_edge(commit, parent)
				iter_parents(parent)

	for branch_head in repo.branches:
		iter_parents(branch_head.commit)
	return graph

def build_log_dict(repo_graph, repo_dir):
	logs_dict = {}
	for commit in repo_graph.nodes:
		#based on Stephen's work in analysis.py
		try:
			log = subprocess.check_output( \
				["git", \
				 "--git-dir",\
				 os.path.join(repo_dir, ".git"),\
				 "notes", \
				 "--ref", \
				 PRODUCTIVITY_NOTES_NAMESPACE, \
				 "show", \
				 commit.hexsha])
			logs_dict[commit] = log
		except:
				pass
	
	return logs_dict

repo_dir = sys.argv[1]
repo = git.Repo(repo_dir)
graph = build_graph(repo)
logs = build_log_dict(graph, repo_dir)

plt.subplot(121)
pos = networkx.kamada_kawai_layout(graph)
networkx.draw(graph, \
              pos, \
              node_size=10, \
							edge_width=1)
plt.show()
