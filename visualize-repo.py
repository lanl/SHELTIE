#!/usr/bin/env python2

from cleansing import parse_sublogs

import git
import networkx
import sys
import os.path
import matplotlib.pyplot as plt
import subprocess
import pprint

PRODUCTIVITY_NOTES_NAMESPACE = 'refs/notes/productivity'

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
			#print(log)
			
			#only hold onto the first sublog for now
			logs_dict[commit] = parse_sublogs(log)[0]
		except Exception as e:
			#print(e)
			pass
	
	return logs_dict

def filter_out_commits_without_logs(graph, logs):
	nodes = list(graph.nodes())
	for commit in nodes:
		if commit not in logs:
			in_edges = graph.in_edges(commit)
			out_edges = graph.out_edges(commit)
			if in_edges and out_edges:
				for pred, commit in in_edges:
					for commit, desc in out_edges:
						if (pred, desc) not in graph.edges:
							graph.add_edge(pred, desc)
			graph.remove_node(commit)

	return graph

def get_branch(commit, branches):
	try:
		log = logs[commit]
		#pprint.pprint(log)
		branch = log['log']['autogeneratated']['git_info']['branch']
		#print('commit %s on branch %s'.format(str(commit.hexsha), branch))

		#print(branch)

		#add branch if it hasn't already been found			
		if branch not in branches:
			branches[branch] = len(branches)
		
		return branch

	except Exception as e:
		#print(e)
		#print('error ^^')
		return None

def get_branch_lists(graph, branches=None):
	if not branches:
		branches = {}
	branch_lists = {}
	for commit in graph:
		branch = get_branch(commit, branches)
		if branch not in branch_lists:
			branch_lists[branch] = [commit]
		else:
			branch_lists[branch].append(commit)
	return branch_lists

def get_time(commit):
	print(commit)
	return commit.authored_date

def time_by_branch_layout(graph, repo, logs):
	branches = {None : 0}

	posns = {}
	for commit in graph.nodes:
		posns[commit] = (get_time(commit), branches[get_branch(commit, branches)])
	
	
	return posns, branches

def get_min_dist(commit, branch_distances):
	min_dist = float('inf')
	for branch_head in branch_distances:
		if commit in branch_distances[branch_head]:
			branch_dist = branch_distances[branch_head][commit]
			if branch_dist < min_dist:
				min_dist = branch_dist
	return min_dist

def dist_from_head_by_branch_layout(graph, repo, logs):
	branches = {None : 0}

	branch_distances = {}
	for branch_head in repo.branches:
		if branch_head.commit in graph.nodes:
			branch_distances[branch_head.commit] = \
				networkx.shortest_path_length(graph, source=branch_head.commit)
	#pprint.pprint(branch_distances)

	posns = {}
	for commit in graph.nodes:
		posns[commit] = (-get_min_dist(commit, branch_distances), \
		                 branches[get_branch(commit, branches)])
	
	return posns, branches

def dist_with_time_order_by_branch_layout(graph, repo, logs):
	dist_by_branch, branches = dist_from_head_by_branch_layout(graph, repo, logs)
	branch_lists = get_branch_lists(graph, branches=branches)

	branch_indicies = {}
	for branch in branch_lists:
		branch_lists[branch] = sorted(branch_lists[branch], key=get_time)
		branch_indicies[branch] = 0

	

	return dist_by_branch, branches

#written with reference to: [1]
#https://stackoverflow.com/questions/13517614/draw-different-color-for-nodes-in-networkx-based-on-their-node-value
def colour_by_branch(graph, branches):
	colours = []
	for commit in graph.nodes:
		branch = get_branch(commit, branches)
		colours.append( 1.0 * branches[branch] / len(branches))
		#print(branch, 1.0 * branches[branch] / len(branches))
	return colours

#build everything we need for ploting
repo_dir = sys.argv[1]
repo = git.Repo(repo_dir)
graph = build_graph(repo)
logs = build_log_dict(graph, repo_dir)
print('--- logs parsed ---')

graph = filter_out_commits_without_logs(graph, logs)

#posns, branches = dist_from_head_by_branch_layout(graph, repo, logs)
#posns, branches = time_by_branch_layout(graph, repo, logs)

#plotting done with reference to : [2]
#https://stackoverflow.com/questions/22992009/legend-in-python-networkx
layouts = [dist_from_head_by_branch_layout, 
           time_by_branch_layout,
           dist_with_time_order_by_branch_layout]
jet = plt.get_cmap('jet')
fig = plt.figure(1)

for i in range(len(layouts)):
	posns, branches = layouts[i](graph, repo, logs)
	colours = colour_by_branch(graph, branches)
	#posns = networkx.kamada_kawai_layout(graph)
	#print(posns)

	subplot = fig.add_subplot(1, len(layouts), 1 + i)
	for branch in branches:
		subplot.plot([0], [0],
		          color=jet(1.0 * branches[branch] / len(branches)),\
		          label=str(branch))
		#print(branch, 1.0 * branches[branch] / len(branches))
	#plot it (colouring with reference to [1])
	plt.subplot(subplot)
	networkx.draw_networkx(graph, \
								posns, \
								cmap=jet, \
								node_color=colours, \
								node_size=50, \
								edge_width=1, \
								arrows=False, \
	              with_labels=False, \
	              ax=subplot)	
	plt.axis('off')
	fig.set_facecolor('w')

	plt.legend(loc='upper center')
fig.tight_layout()
plt.show()
