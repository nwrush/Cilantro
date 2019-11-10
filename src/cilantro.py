#!/bin/env python3

import argparse
import fnmatch
import json
import os
import os.path
import subprocess
import sys

import dependency_graph
import gcc
   

def main(*targets, def_file="build.json", **kwargs):
    try:
        definition = json.load(open(def_file, 'r'))
    except OSError as ex:
        print("Error while opening definition file: {}\nAre you sure the file exists?".format(def_file), file=sys.stderr)
        return

    defined_targets = {target["name"]: target for target in definition["targets"]}

    for target_name in targets:

        target = defined_targets.get(target_name, None)
        
        if target is None:
            print("Could not find target {}".format(target_name), file=sys.stderr)
            return

        # DFS ordering of buiild targets, with deepest targets listed first
        target_ordering = dependency_graph.get_depth_first_ordering(target, defined_targets, "name", "depends", reverse=True)

        for target in target_ordering:
            print(":" + target["name"])
            gcc.build_target(target)
            print()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="+")
    parser.add_argument("-f", "--file", dest="build_file", default="build.json")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(*args.targets, def_file=args.build_file)
