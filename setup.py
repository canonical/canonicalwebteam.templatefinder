#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.templatefinder",
    version="1.0.0",
    author="Canonical Webteam",
    url="https://github.com/canonical-webteam/templatefinder",
    packages=find_packages(),
    description=(
        "A module which attempts to load the corresponding templates directly"
        " from URLs, without the need to write a view for each URL."
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "Flask>=1.0",
        "mistune==0.8.4",
        "python-frontmatter>=0.4.5",
        "bleach>=3.1",
    ],
    tests_require=["Flask-Testing>=0.7.1"],
)
