#!/usr/bin/env python2

from cleansing import parse_sublogs, build_graph, build_log_dict

import git
import networkx
import sys
import os.path
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import matplotlib
import subprocess
import pprint
from mpl_toolkits.axes_grid1 import make_axes_locatable

PRODUCTIVITY_NOTES_NAMESPACE = 'refs/notes/productivity'

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

def filter_out_commits_not_between_logged_commits(graph, logs):
	nodes = list(graph.nodes())
	for commit in nodes:
		if commit not in logs:
			after_log=False
			before_log =False
			for pred in graph.predecessors(commit):
				if pred in logs:
					after_log=True
					break
			if after_log:
				for succ in graph.successors(commit):
					if succ in logs:
						before_log=True
						break
			if not after_log and not before_log:
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
	return commit.authored_date

def time_by_branch_layout(graph, repo, logs):
	branches = {None : 0}

	xs = []
	for commit in graph.nodes:
		xs.append((commit, get_time(commit)))
	xs.sort(key=lambda (commit, time): time)	

	posns = {}
	for i in range(len(xs)):
		commit, x = xs[i]
		posns[commit] = (i, branches[get_branch(commit, branches)])

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
def colour_by_branch(graph, branches, logs, cmap=plt.get_cmap('jet')):
	colours = []
	for commit in graph.nodes:
		branch = get_branch(commit, branches)
		colours.append( cmap(1.0 * branches[branch] / len(branches)))
		#print(branch, 1.0 * branches[branch] / len(branches))
	return colours

def colour_by_log_val(graph, branches, logs, get_log_val, \
                      cmap='seismic', \
                      norm=colors.Normalize(vmin=1, vmax=7)):
	grey = colors.get_named_colors_mapping()['tab:gray']
	grey = colors.to_rgba(grey)
	cmap = plt.get_cmap(cmap)
	colours = []
	for commit in graph.nodes:
		try:
			log = logs[commit]
			#should be normalised between 0 and 1
			log_val = get_log_val(log) 
			colour = cmap(norm(log_val))
			colours.append(colour)
			#print(log_val, colour)
		except Exception as e:
			#print('log_val not found')
			#print(e)
			colours.append(grey)

	return colours, cmap, norm

def wrap_colour_by_log(get_log_val, cmap='coolwarm', norm=colors.Normalize()):
	return lambda graph, branches, logs: \
		colour_by_log_val(graph, branches, logs, get_log_val, cmap)

colour_by_frustration = \
	wrap_colour_by_log(lambda log: \
		log['log']['user_responses']['NASA-TLX']['frustration'])
#colour_by_kokkos = \
#	wrap_colour_by_log(lambda log: \
#		float(log['log']['user_responses']['tags']['Kokkos']), \
#	                   cmap='binary', \
#	                   norm=colors.BoundaryNorm(boundaries=[-0.2,-0.1,0.1,0.9,1.1,1.2]), \
#	                                            n_colors=256)

#from Stephen's analysis code
def get_delta_sloc(commit, repo_dir=sys.argv[1]):
	lines_changed = 0
	#print commit.diff(commit.parents[0])[0].diff
	diff = subprocess.check_output(["git", "--git-dir", os.path.join(repo_dir, ".git"),  'diff', commit.hexsha, commit.parents[0].hexsha])
	sloc = 0
	for line in diff.split('\n'):
			if not (line.startswith("-") or line.startswith("+")): continue
			if line.strip() == "+" or line.strip() == "-": continue
			if line.startswith('+++') or line.startswith('---'): continue
			sloc += 1
	return sloc	

def colour_by_delta_sloc(graph, branches, logs, cmap='coolwarm'):
	cmap = plt.get_cmap(cmap)
	colours = [get_delta_sloc(commit) for commit in graph.nodes]

	return colours, cmap, None

#build everything we need for ploting
repo_dir = sys.argv[1]
repo = git.Repo(repo_dir)
graph = build_graph(repo)
logs = build_log_dict(graph, repo_dir)
print('--- logs parsed ---')
#print(graph)

graph = filter_out_commits_without_logs(graph, logs)
#graph = filter_out_commits_not_between_logged_commits(graph, logs)
posns, branches = dist_with_time_order_by_branch_layout(graph, repo, logs)
#posns, branches = dist_from_head_by_branch_layout(graph, repo, logs)
#posns, branches = time_by_branch_layout(graph, repo, logs)

#plotting done with reference to : [2]
#https://stackoverflow.com/questions/22992009/legend-in-python-networkx
#layouts = [dist_from_head_by_branch_layout, 
          # time_by_branch_layout,
          # dist_with_time_order_by_branch_layout]
layouts = [time_by_branch_layout]
#layouts = [#networkx.shell_layout,
           #networkx.spring_layout
           #networkx.spectral_layout
          #]
colourings = [colour_by_frustration
              #colour_by_branch,
              #colour_by_kokkos,
              #colour_by_delta_sloc
             ]
jet = plt.get_cmap('jet')
fig = plt.figure(1)

for i in range(len(layouts)):
	for j in range(len(colourings)):
		posns, branches = layouts[i](graph, repo, logs)
		colours, cmap, norm = colourings[j](graph, branches, logs)
		#colours = colour_by_branch(graph, branches)
		#posns = networkx.kamada_kawai_layout(graph)
		#posns = layouts[i](graph)
		#print(posns)

		subplot = fig.add_subplot(1, \
		                          len(layouts) * len(colourings), \
		                          1 + j*len(layouts) + i)
		#print(subplot)
		b_list = ['' for b in branches]
		for branch in branches:
			b_list[branches[branch]] = branch

		#for branch in b_list:
		#	label = str(branch)
		#	if label == 'sharrell':
		#		label = 'Working Branch'
		#	subplot.plot([0], [0],
		#						marker='o', \
		#						color=jet(1.0 * branches[branch] / len(branches)),\
		#						label=label)
		#	#print(branch, 1.0 * branches[branch] / len(branches))
		##plot it (colouring with reference to [1])
		plt.subplot(subplot)
		
		#pprint.pprint(posns)
		#pprint.pprint(colours)
		networkx.draw_networkx(graph, \
													 posns, \
													 #cmap=jet, \
													 node_color=colours, \
													 node_size=50, \
													 edge_width=1, \
													 arrows=False, \
													 with_labels=False, \
													 ax=subplot)


		#based on: [3]
		#https://stackoverflow.com/questions/26739248/how-to-add-a-simple-colorbar-to-a-network-graph-plot-in-python	
		scalar_map = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
		scalar_map._A = []
		cbar = plt.colorbar(scalar_map, orientation='vertical', ticks=[1, 4, 7])	
		
		cbar.set_label('Frustration', rotation=270, labelpad=16)	
	
		#based on: [4]
		#https://matplotlib.org/gallery/ticks_and_spines/colorbar_tick_labelling_demo.html
		cbar.ax.set_yticklabels(['Very Low', 'About Average', 'Very High'], rotation=270, verticalalignment='center')
	
		#based on: [5]
		#https://3diagramsperpage.wordpress.com/2014/05/25/arrowheads-for-axis-in-matplotlib/
		xmin, xmax = subplot.get_xlim() 
		ymin, ymax = subplot.get_ylim()

		dps = fig.dpi_scale_trans.inverted()
		bbox = subplot.get_window_extent().transformed(dps)
		width, height = bbox.width, bbox.height
	
		hw = 1./20.*(ymax-ymin) 
		hl = 1./20.*(xmax-xmin)
		lw = 1. # axis line width
		ohg = 0.3 # arrow overhang

		subplot.arrow(xmin, ymin, xmax-xmin, 0., fc='k', ec='k', lw = lw, 
						 head_width=hw, head_length=hl, overhang = ohg, 
						 length_includes_head= True, clip_on = False) 
		
		subplot.set_title('Frustration Reported by Commit')
		subplot.set_xlabel('Time')
		subplot.set_xticks([])
		subplot.set_yticks([])
		subplot.set_frame_on(False)
			
		#plt.axis('off')

		#plt.legend(loc='upper center')
fig.set_facecolor('w')
fig.tight_layout()
plt.show()
