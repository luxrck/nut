import os

import mistune

from .config import Config
from .theme import Theme
from .fs import *
from .processor import *


class Generator(object):
    def __init__(self, root):
        self.root = os.path.abspath(root)

        self.config = Config(self.root)
        self.theme = Theme(name = self.config.theme, root = self.root)

        self.articles = []
        self.categories = Category(name="all", rank=0, sub=[])
        self.tags = []
        self.pages = []
        self.index = ""
        self.about = ""

        self.reload()


    def select(category="all", tag=""):
        selected = self.articles
        if category:
            f = category if callable(category) else (lambda x: category in x.categories)
            selected = filter(f, selected)
        if tag:
            f = tag if callable(tag) else (lambda x: x == tag)
            selected = filter(f, selected)
        return selected


    def reload(self):
        tags = {}
        def load_articles(root, cats):
            for entry in os.listdir(root):
                location = os.path.join(root, entry)
                if os.path.isdir(location):
                    sub = Category(name=entry, rank=0, sub=[])
                    cats[-1].sub.append(sub)
                    load_articles(location, cats + [sub])
                    cats[-1].rank += sub.rank
                    continue

                if not entry.endswith(".md"): continue

                a = article(location)

                if a.header.categories:
                    for s in cats[-1].sub:
                        if s.name == a.header.categories[0]:
                            s.rank += 1; a.header.categories = [s]; break
                    else:
                        s = Category(name=a.header.categories[0], rank=1, sub=[])
                        cats[-1].sub.append(s)
                        a.header.categories = [s]
                a.header.categories = [c.name for c in cats + a.header.categories]

                self.articles.append(a)
                for t in a.header.tags:
                    tags.setdefault(t, 0); tags[t] += 1

                cats[-1].rank += 1

        articles_dir = os.path.join(self.root, "articles")
        ensure_dir(articles_dir)

        load_articles(articles_dir, [self.categories])

        tags = [Tag(name=i[0], rank=i[1]) for i in tags.items()]
        self.tags = sorted(sorted(tags, key=lambda t: t.name), key=lambda t: t.rank, reverse=True)

        self.articles.sort(key=lambda a: a.header.date, reverse=True)

        def csort(cat):
            cat.sub.sort(key=lambda c: c.rank, reverse=True)
            for s in cat.sub: csort(s)
        csort(self.categories)

        app = self.config.articles_per_page
        total_pages = len(self.articles) // app
        total_pages += (1 if len(self.articles) % app else 0)
        for p in range(1, total_pages+1):
            is_first = p == 1
            page = Page(name=p,
                        first=1,
                        last=total_pages,
                        is_first=is_first,
                        is_last=False,
                        articles=self.articles[p*app:(p+1)*app])
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
                    "config": self.config,
                    }
                for v in route[1]:
                    if route[2] == "tag": kw["tag"] = v
                    elif route[2] == "category": kw["category"] = v
                    elif route[2] == "article": kw["article"] = v
                    elif route[2] == "page": kw["page"] = v
                    output = os.path.join(root, route[0].format(getattr(v, "name") if hasattr(v, "name") else "").strip())
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
