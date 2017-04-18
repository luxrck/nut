import os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .fs import *


class Theme(object):
    def __init__(self, name, root):
        self.name = name
        self.root = os.path.join(os.path.abspath(root), "themes", name)
        if not os.path.exists(self.root):
            builtin_theme_root = os.path.join(os.path.dirname(__file__), "themes")
            cp(os.path.join(builtin_theme_root, name), self.root)
        self.env = Environment(loader=FileSystemLoader(os.path.join(self.root, "templates")))

    def get_template(self, name):
        try:
            return self.env.get_template(name)
        except TemplateNotFound:
            return None
