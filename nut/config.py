import os
import yaml
from .fs import *

class Config(object):
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.file = os.path.join(self.root, "config.yml")
        ensure_file(self.file)
        self.default()
        self.reload()

    def default(self):
        self.theme = "default"
        self.summary = ""
        self.output = "docs"
        self.articles_per_page = 10

    def reload(self):
        data = yaml.load(open(self.file).read())
        if not data: return
        for k, v in data.items():
            if hasattr(self, k): setattr(self, k, v)

    def save(self):
        data = {
            "theme": self.theme,
            "summary": self.summary,
            "output": self.output,
            "articles_per_page": self.articles_per_page
            }
        with open(self.file, "w") as stream:
            yaml.dump(data, stream, default_flow_style=False)
