#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


setup(
    name="fritzing-stripboard",
    version="1.0.0",
    license="MIT",
    description="Generate Fritzing components that match your stripboard",
    long_description_content_type="text/markdown",
    long_description="%s"
    % (
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.md")
        )
    ),
    author="Adam Coddington",
    author_email="me@adamcoddington.net",
    url="https://github.com/coddingtonbear/fritzing-stripboard",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
    ],
    project_urls={
        "Changelog": "https://fritzing-stripboard.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/coddingtonbear/fritzing-stripboard/issues",
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyyaml>=6.0,<7.0",
        "pydantic>=1.10.7,<2.0",
    ],
    extras_require={},
    setup_requires=[
        "pytest-runner",
    ],
    entry_points={
        "console_scripts": [
            "fritzing-stripboard = fritzing_stripboard.cli:main",
        ]
    },
)
