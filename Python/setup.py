from setuptools import setup, find_packages

NAME = "microsoft-bonsai-api"
REQUIRES = ["msrest>=0.6.0", "azure-core<2.0.0,>=1.2.0"]

version = {}
with open("./microsoft_bonsai_api/version.py") as fp:
    exec(fp.read(), version)

# TODO: Update
setup(
    name=NAME,
    version=version["__version__"],
    description="",
    author_email="",
    url="",
    keywords=[""],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="",
)
