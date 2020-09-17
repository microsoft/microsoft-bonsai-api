# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_namespace_packages

# Grab the README to use as the long description
if sys.version_info[0] < 3:
    with open("README.md", "r") as fh:
        LONG_DESCRIPTION = fh.read()
else:
    with open("README.md", "r", encoding="utf-8") as fh:
        LONG_DESCRIPTION = fh.read()

# Grab the version.py file to set the version
version = {}
with open("./microsoft_bonsai_api/version.py") as fp:
    exec(fp.read(), version)
CLIENT_VERSION = version["__version__"]

setup(
    author="Microsoft Project Bonsai",
    author_email="bonsaiq@microsoft.com",
    url="https://docs.microsoft.com/bonsai",
    keywords=["bonsai", "autonomous systems", "simulation"],
    name="microsoft-bonsai-api",
    version=CLIENT_VERSION,
    description="API library for the Microsoft Bonsai Platform",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=find_namespace_packages(include=["microsoft_bonsai_api.*"]),
    install_requires=[
        "msrest>=0.6.0",
        "azure-core<2.0.0,>=1.2.0",
        "msal>=1.2.0,<=1.4.3",
        "msal_extensions>=0.1.3,<=0.2.2",
    ],
    test_suite="pytest",
    tests_require=["pytest>=5.4.2"],
)
