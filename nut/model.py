import re
import os
from datetime import datetime

import mistune

from .renderer import ArticleRenderer


class FormatError(Exception):
    pass


class Page(object):
    def __init__(self, name, articles, is_last=False):
        self.name = name
        self.articles = articles
        self.is_first = name == 1
        self.is_last = is_last
    def __str__(self):
        return str(self.name)


class Tag(object):
    def __init__(self, name):
        self.name = name
        self.articles = set()
    def __str__(self):
        return str(self.name)
    def add(self, a):
        self.articles.add(a)
    def pop(self, a):
        self.articles.pop(a)


class ArticleHeader(object):
    title = ""
    category = ""
    tags = []
    date = datetime.now()

    def __init__(self, source=None):
        if source:
            self.parse(source)

    def parse(self, source):
        processing = False
        while True:
            line = source.readline()
            if not line: break
            line = line.strip()
            if not processing and not line.startswith("---"): continue
            if not processing: processing = True; continue
            if line.startswith("---"): break
            try:
                prop, value = [i.strip() for i in line.split(":", 1)]
            except Exception as e:
                raise FormatError("Header property format error.")
            if prop == "date":
                self.date = datetime.strptime(value, "%Y-%m-%d %H:%M")
            elif prop == "tags":
                self.tags = [i.strip() for i in filter(lambda x: x, value.split(","))]
            else:
                setattr(self, prop, value)

    def serialize(self):
        stream = ""
        stream += "---\n"
        stream += "title: {}\n".format(self.title)
        stream += "date: {}\n".format(self.date.strftime("%Y-%m-%d %H:%M"))
        stream += "category: {}\n".format(self.category)
        stream += "tags: {}\n".format(" ".join(self.tags))
        stream += "---\n"
        return stream


class Article(object):
    def __init__(self, path):
        source = open(path)
        matched = re.findall("(?:\d{4}-\d{2}-\d{2})?-?(\w[\_\-\w]+\w)", os.path.basename(path))
        self.name = matched[0] if matched else re.sub("\.md$", "", os.path.basename(path))
        self.header = ArticleHeader(source)
        self.text = source.read()
        m = mistune.Markdown(renderer=ArticleRenderer())
        self.html = m(self.text)
    def __str__(self):
        return self.name
