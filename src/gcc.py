# Nikko Rush
# 11/9/2019

import access
import fnmatch
import os
import os.path
import shutil
import subprocess
import sys


@access.private
def file_newer(time, fname):
    try:
        return os.stat(fname).st_mtime > time
    except OSError:
        return True


@access.private
def source_newer(source, target):
    try:
        return os.stat(source).st_mtime > os.stat(target).st_mtime
    except OSError:
        return True


@access.private
def any_file_newer(target, *fnames):
    try:
        return any(file_newer(os.stat(target).st_mtime, fname) for fname in fnames)
    except OSError:
        return True


@access.private
def load_files(folder, data):
    files = list()

    match_pattern = data.get("include", "*")
    reject_pattern = data.get("exclude", "")

    for entry in os.scandir(folder):
        if entry.is_file():
            if fnmatch.fnmatch(entry.name, match_pattern) and not fnmatch.fnmatch(entry.name, reject_pattern):
                files.append(entry.path)
        elif entry.is_dir() and (data.get("recursive", True) or entry.name in folder):
            if entry.name in folder:
                files.extend(load_files(entry.path, folder[entry.name]))
            else:
                files.extend(load_files(entry.path, data))
    
    return files


@access.private
def build_objects(target):
    sources = target["sources"]
    include_dirs = target["include"]    
    output_dir = target["output_dir"]
    
    folders = target["sources"]
    
    files = list()

    for folder, data in target["sources"].items():
        files.extend(load_files(folder, data))

    include_args = ["-I{}".format(dir_name) for dir_name in include_dirs]

    for fname in files:
        output_path = os.path.splitext(os.path.join(output_dir, fname))[0] + ".o"

        if not target.get("force", False) and not source_newer(fname, output_path):
            continue
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        command = ["gcc", *target.get("args", list()), "-c", "-o", output_path, *include_args, fname]
        print(" ".join(command))
        subprocess.run(command)


@access.private
def build_so(target):
    sources = target["sources"]
    include_dirs = target.get("include", list())
    libraries = target.get("libraries", list())
    library_dirs = target.get("lib_path", list())
    
    files = list()
    
    for folder, data in target["sources"].items():
        files.extend(load_files(folder, data))

    include_args = ["-I{}".format(dir_name) for dir_name in include_dirs]
    library_args = ["-l{}".format(lib_name) for lib_name in libraries]
    library_paths = ["-L{}".formata(dir_name) for dir_name in library_dirs]

    output = target["output_name"] if "output_name" in target else target["name"]

    if not target.get("force_name", False):
        if output[:3] != "lib":
            output = "lib" + output
        if output[-3:] != ".so":
            output += ".so"

    output_path = os.path.join(target["output_dir"], output)

    if not any_file_newer(output_path, *files):
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    command = ["gcc", *target.get("args", list()), "-shared", "-fPIC", "-o", output_path, *include_args, *library_paths, *files, *library_args]
    print(" ".join(command))
    subprocess.run(command)


@access.private
def clean(target):
    files = target.get("files", list())

    for fname in files:
        try:
            if os.path.isdir(fname):
                shutil.rmtree(fname, ignore_errors=True)
            else:
                os.remove(fname)
        except:
            pass


@access.private
def exec(target):
    sources = target["sources"]
    include_dirs = target.get("include", list())
    libraries = target.get("libraries", list())
    library_dirs = target.get("lib_path", list())

    files = list()

    for folder, data in sources.items():
        files.extend(load_files(folder, data))


    include_args = ["-I{}".format(dir_name) for dir_name in include_dirs]
    library_args = ["-l{}".format(lib_name) for lib_name in libraries]
    library_paths = ["-L{}".format(dir_name) for dir_name in library_dirs]
    output = target["output_name"] if "output_name" in target else target["name"]

    output_path = os.path.join(target["output_dir"], output)

    if not any_file_newer(output_path, *files):
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    command = ["gcc", *target.get("args", list()), "-o", output_path, *include_args, *library_paths, *files, *library_args]
    print(" ".join(command))
    subprocess.run(command)


@access.private
def run(target):
    target_env = os.environ.copy()
    
    target_env.update(target.get("env", dict()))

    additional_path = target.get("path", "")
    
    target_env["PATH"] = additional_path + ":" + target_env.get("PATH", "")

    command = target["command"]
    command = target["command"] if isinstance(command, list) else command.split(" ")
    print(" ".join(command))
    subprocess.run(target["command"], cwd=target.get("cwd", None), env=target_env)

    
function_mappings = {
    "objects": build_objects,
    "shared_lib": build_so,
    "exec": exec,
    "run": run
}

name_mappings = {
    "clean": clean
}


def build_target(target):
    func = function_mappings.get(target.get("type", ""), None) or name_mappings.get(target["name"], None)
    if func is None:
        print("Could not find handler for target: {}".format(target["type"]), file=sys.stderr)

    return func(target)
