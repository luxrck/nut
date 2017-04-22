import re
import os
from datetime import datetime

import yaml
import mistune

from .config import config


class FormatError(Exception):
    pass


class ArticleRenderer(mistune.Renderer):
    pass


class Meta(dict):
    def __init__(self, **kw):
        for k,v in kw.items(): setattr(self, k, v)
    # def __str__(self):
    #     return (str(self.name) if self.name else "")
    def __getattr__(self, k):
        return self.get(k, None)
    def __setattr__(self, k, v):
        if hasattr(self, k): self.__dict__[k] = v
        self[k] = v


# name, rank
class Tag(Meta): pass
# name, first, last, is_first, is_last, articles
class Page(Meta): pass
# name, rank, sub
class Category(Meta): pass
class Header(Meta): pass
class Article(Meta):
    def summary(self):
        return Meta(name = self.name,
                    title = self.header.title,
                    date = self.header.date.strftime(config().datetime_format),
                    time = int(self.header.date.timestamp()),
                    categories = self.header.categories,
                    tags = self.header.tags)


def header(source=None, location=""):
    c = config()
    h = Header()
    h.title = ""
    h.date = datetime.now()
    h.categories = []
    h.tags = []
    if not source: return h
    processing = False
    while True:
        line = source.readline()
        if not line: break
        line = line.strip()
        if not processing:
            if not line: continue
            if line.startswith("#"): continue
            if line.startswith("---"): processing = True; continue
            raise FormatError("Article format incorrect: %s" % location)
        if line.startswith("---"): break
        try:
            prop, value = [i.strip() for i in line.split(":", 1)]
        except Exception as e:
            raise FormatError("Header property format error: %s" % location)
        if prop == "date":
            h.date = datetime.strptime(value, c.datetime_format)
        elif prop == "tags":
            h.tags = [i.strip() for i in filter(lambda x: x, value.split(","))]
        elif prop == "category": # special case for `category`
            if value:
                h.categories.append(value.split(',', 1).strip())
        else:
            setattr(h, prop, value)
    return h


def article(location):
    m = mistune.Markdown(renderer=ArticleRenderer())
    a = Article()
    source = open(location)
    matched = re.findall("(?:\d{4}-\d{2}-\d{2})?-?(.+)(?:\.md)", os.path.basename(location))
    # a.location = location
    a.name = matched[0] if matched else re.sub("\.md$", "", os.path.basename(location))
    a.header = header(source, location)
    a.text = source.read()
    a.html = m(a.text)
    return a


def serialize(m, t=""):
    if not t: t = m.__class__.__name__.lower()
    __render__ = globals().get("serialize_" + t)
    if not __render__: return ""
    return __render__(m)


def serialize_header(m):
    stream = ""
    stream += "---\n"
    stream += "title: {}\n".format(m.title)
    stream += "date: {}\n".format(m.date.strftime(config().datetime_format))
    stream += "category: {}\n".format(m.categories[-1] if m.categories else "")
    stream += "tags: {}\n".format(", ".join(m.tags).strip())
    stream += "---\n"
    return stream


def serialize_aricle(m):
    header = render_header(m.header)
    return header + m.text
