import sys
import os

from .cmd import *

usage = """
nut usage:

init <blog>     initialize new blog site.
post <name>     new post.
build           generate static site.
serve           preview site.
"""

def main():
    if len(sys.argv) < 2:
        print(usage); return
    if sys.argv[1] == "build":
        build(".")
    elif sys.argv[1] == "serve":
        serve(".")
    elif sys.argv[1] == "post":
        if len(sys.argv) < 3:
            print(usage)
        else:
            new_article(sys.argv[2], '.')
    elif sys.argv[1] == "init":
        if len(sys.argv) < 3:
            project(".")
        else:
            project(sys.argv[2])



if __name__ == "__main__":
    sys.exit(main())
