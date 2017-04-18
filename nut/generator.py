import os

import mistune

from . import config, theme
from .model import *
from .renderer import *
from .fs import *


class Generator(object):
    def __init__(self, root):
        self.root = os.path.abspath(root)

        self.config = config.Config(self.root)
        self.theme = theme.Theme(name = self.config.theme, root = self.root)

        self.reload()


    def reload(self):
        self.articles = []
        self.categories = {}
        self.tags = {}
        self.pages = []
        self.index = ""
        self.about = ""

        articles_dir = os.path.join(self.root, "articles")
        ensure_dir(articles_dir)
        for entry in os.listdir(articles_dir):
            if not entry.endswith(".md"): continue
            a = Article(os.path.join(self.root, "articles", entry))

            self.articles.append(a)
            self.categories.setdefault(a.header.category, [])
            self.categories[a.header.category].append(a)

            for t in a.header.tags:
                self.tags.setdefault(t, [])
                self.tags[t].append(a)

        sort = lambda v: v.sort(key=lambda a: a.header.date, reverse=True)
        dsort = lambda d: [sort(v) for v in d.values()]
        sort(self.articles)
        dsort(self.categories)
        dsort(self.tags)

        app = self.config.articles_per_page
        total_pages = len(self.articles) // app
        total_pages += (1 if len(self.articles) % app else 0)
        for p in range(1, total_pages+1):
            page = Page(p, self.articles[p*app:(p+1)*app])
            self.pages.append(page)
        if self.pages: self.pages[-1].is_last = True

        m = mistune.Markdown(renderer=ArticleRenderer())
        self.index = m(read(os.path.join(self.root, "index.md")))
        self.about = m(read(os.path.join(self.root, "about.md")))


    def generate(self, root=None):
        t = lambda tmpl: self.theme.get_template(tmpl)
        r = lambda v, t: t.render(**v)

        if not root: root = self.config.output
        root = os.path.abspath(root)

        rms(root)

        def gen(root, routes):
            for route in routes:
                tmpl = self.theme.get_template(route[2])
                if not tmpl: continue
                kw = {
                    "tags": self.tags,
                    "categories": self.categories,
                    "articles": self.articles,
                    "pages": self.pages,
                    "this": self,
                    }
                for v in route[1]:
                    if route[2] == "tag": kw["tag"] = v
                    elif route[2] == "category": kw["category"] = v
                    elif route[2] == "article": kw["article"] = v
                    elif route[2] == "page": kw["page"] = v
                    output = os.path.join(root, route[0].format(str(v)).strip())
                    output = output + ("index.html" if output[-1] == "/" else "")
                    saveto(output, r(kw, tmpl))

        gen(root, [
            ("t/{}/",       self.tags,      "tag"      ),
            ("c/{}/",       self.categories,"category" ),
            ("p/{}/",       self.articles,  "article"  ),
            ("page/{}/",    self.pages,     "page"     ),
            ("archive/",    [self],         "archive"  ),
            ("about/",      [self],         "about"    ),
            ("index.html",  [self],         "index"    ),
            ])

        cp(os.path.join(self.root, "assets"), os.path.join(root, "assets"))
        cp(os.path.join(self.theme.root, "assets"), os.path.join(root, "assets"))
