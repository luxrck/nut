#!/usr/bin/env python
import nut
from setuptools import setup


setup(name='nut',
      version=nut.__version__,
      description='A static site generator.',
      author='lux.r.ck',
      author_email='lux.r.ck@gmail.com',
      packages=['nut'],
      entry_points={
        "console_scripts": "nut = nut.__main__:main"
        },
      install_requires=[
        "mistune",
        "Jinja2",
        "PyYAML"
        ],
      include_package_data=True,
      license="MIT License",
      zip_safe=False,
     )
