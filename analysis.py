#!/usr/bin/env python

test_json = """{"user_responses":
                 {"description":"readme"},
                 {"time_categories":
                   {"planning":
                     {"time_spent":1.000000},                        {"difficulty":1}
                   },
                   {"coding":
                    {"time_spent":1.000000},                        {"difficulty":1}
                   },
                   {"refactoring":
                     {"time_spent":1.000000},                        {"difficulty":1}
                   },
                   {"debugging":
                     {"time_spent":1.000000},                        {"difficulty":1}
                   },
                   {"optimising":
                     {"time_spent":1.000000},                        {"difficulty":1}
                   }
                 }       
        {"tags":
                {"MPI":true},
                {"OpenMP":true},
                {"Cuda":true},
                {"Kokkos":false},
                {"domain specific work":false}
        },
        {"NASA-TLX":
                {"mental_demand":1},            {"temporal_demand":1},          {"performance":1},              {"effort":1},
        {"frustration":1}       }}
{"status":""}
{"files":

}
{"git_info":
        {"commit_hash":0895d2f3be84aefa259aa0255a6b36384f195fe7},
        {"branch":master}
}
"""

import os.path
import subprocess
import sys
import json
import argparse
from git import Repo

parser = argparse.ArgumentParser()
parser.add_argument("repo_dir", help="The repo that contains the productivity logs as notes")
args = parser.parse_args()

if(not os.path.isdir(os.path.join(args.repo_dir, ".git"))):
  print "Cannot find %s directory. Not a git repo." % os.path.join(args.repo_dir, ".git")
  sys.exit(1)

PRODUCTIVITY_NTOES_NAMESPACE="refs/notes/productivity"

repo = Repo(args.repo_dir)

commits = list(repo.iter_commits("kokkos_advance_b"))

#git notes --ref refs/notes/productivity show
for commit in commits:
  try:
    print subprocess.check_output(["git", "--git-dir", os.path.join(args.repo_dir, ".git"), "notes", "--ref", PRODUCTIVITY_NTOES_NAMESPACE, "show", commit.hexsha])
  except:
      pass


#test_json = test_json.replace("\n", "")

#print test_json

#json_productivity_log = test_json

#try:
#  print json.loads(json_productivity_log)
#except ValueError:
#  # Fix bad commit logs  
#  json_productivity_log = json_productivity_log.replace('"user_responses":', '"user_responses":[')
#  json_productivity_log = json_productivity_log.replace('"time_categories":', '"time_categories":[')







