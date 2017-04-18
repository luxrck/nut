import os
from shutil import copy
from distutils.dir_util import copy_tree, remove_tree

def saveto(path, data):
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(data)


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def cp(s, t):
    if not os.path.exists(s): return
    if os.path.isdir(s): copy_tree(s, t)
    else: copy(s, t)

def rm(t):
    if not os.path.exists(t): return
    if os.path.isdir(t): remove_tree(t)
    else: os.remove(t)

def rms(t):
    if not os.path.exists(t): return
    if not os.path.isdir(t): return os.remove(t)
    for s in os.listdir(t): rm(os.path.join(t, s))

def ensure_file(p):
    if os.path.exists(p): return
    if not os.path.exists(os.path.dirname(p)):
        ensure_dir(os.path.dirname(p))
    touch(p)

def touch(p):
    saveto(p, "")

def read(p):
    if not os.path.exists(p): return ""
    return open(p).read()
