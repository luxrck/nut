import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

from .fs import *
from .model import *
from .config import Config
from .theme import Theme
from .generator import Generator


def project(root):
    structures = ["assets", "articles", "themes"]
    for d in structures:
        os.makedirs(os.path.join(root, d), exist_ok=True)

    Config(root).save()

    ensure_file(os.path.join(root, "index.md"))
    ensure_file(os.path.join(root, "about.md"))
    # return Generator(root)


def build(root="."):
    return Generator(root).generate()


def new_article(name, root="."):
    h = ArticleHeader()
    h.title = name
    filename = name.lower().replace(" ", "-")
    filename = "{}-{}.md".format(h.date.strftime("%Y-%m-%d"), filename)
    open(os.path.join(root, "articles", filename), "w").write(h.serialize())


def serve(root="."):
    out = Config(root).output
    os.chdir(out)
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Start server on: 0.0.0.0:8000")
    httpd.serve_forever()
