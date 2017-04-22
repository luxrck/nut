import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

from .fs import *
from .processor import *
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
    Config(root)
    h = header()
    h.title = name
    filename = re.sub("[^\w\s]", "", name.lower()).strip()
    filename = filename.replace(" ", "-")
    filename = "{}-{}.md".format(h.date.strftime("%Y-%m-%d"), filename)
    open(os.path.join(root, "articles", filename), "w").write(serialize(h))


def serve(root="."):
    out = Config(root).output
    os.chdir(out)
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Start server on: 0.0.0.0:8000")
    httpd.serve_forever()
