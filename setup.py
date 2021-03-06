# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ""

setup(
    long_description=readme,
    name="routeros-diff",
    version="0.1.0",
    description="Tools for parsing & diffing RouterOS configuration files. Can produce config file patches.",
    python_requires="==3.*,>=3.8.0",
    project_urls={"repository": "https://github.com/gardunha/routeros-diff"},
    author="Adam Charnock",
    author_email="adam.charnock@gardunha.net",
    license="MIT",
    packages=["routeros_diff"],
    package_dir={"": "."},
    package_data={},
    install_requires=["python-dateutil==2.*,>=2.8.1"],
)
