import os
import yaml
from .fs import *


def external_link(website, username):
    symtb = {
        "github": "https://github.com/{}",
        "steam": "https://https://steamcommunity.com/id/{}",
        "twitter": "https://twitter.com/{}",
        }
    if not website in symtb: return ""
    return symtb[website].format(username)


class Config(object):
    __instance__ = None
    def __new__(cls, *args, **kw):
        if not Config.__instance__:
            self = Config.__instance__ = object.__new__(cls)
            Config.__init__(self, *args, **kw)
        return Config.__instance__

    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.file = os.path.join(self.root, "config.yml")
        ensure_file(self.file)
        self.default()
        self.reload()

    def default(self):
        self.theme = "default"
        self.summary = ""
        self.home = "Homepage"
        self.output = "site"
        self.datetime_format = "%Y-%m-%d %H:%M %Z%z"
        self.externals = {}
        self.external_links = {}
        self.articles_per_page = 10
        self.ga = {}

    def reload(self):
        data = yaml.load(open(self.file).read())
        if not data: return
        for k, v in data.items():
            if hasattr(self, k): setattr(self, k, v)
        for k, v in self.externals.items():
            self.external_links[k] = external_link(k, v)

    def save(self):
        data = {
            "theme": self.theme,
            "summary": self.summary,
            "home": self.home,
            "output": self.output,
            "datetime_format": self.datetime_format,
            "articles_per_page": self.articles_per_page,
            "externals": self.externals,
            "ga": self.ga,
            }
        with open(self.file, "w") as stream:
            yaml.dump(data, stream, default_flow_style=False)


def config():
    return Config.__instance__
