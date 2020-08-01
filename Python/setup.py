# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_namespace_packages

# Set the setup values we will manage over time as variables
PACKAGE_NAME = "microsoft-bonsai-api"
SHORT_DESCRIPTION = ""
CLIENT_REQUIREMENT = [
    "msrest>=0.6.0",
    "azure-core<2.0.0,>=1.2.0",
    "msal==1.2.0",
    "msal_extensions==0.1.3",
]
TESTING_PLATFORM = "pytest"
TESTING_REQUIREMENT = ["pytest>=5.4.2"]
SEO_KEYWORDS = ["bonsai", "autonomous systems", "simulation"]

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
    keywords=SEO_KEYWORDS,
    name=PACKAGE_NAME,
    version=CLIENT_VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=find_namespace_packages(include=["microsoft_bonsai_api.*"]),
    install_requires=CLIENT_REQUIREMENT,
    test_suite=TESTING_PLATFORM,
    tests_require=TESTING_REQUIREMENT,
)
