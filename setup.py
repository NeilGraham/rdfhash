from setuptools import setup, find_packages
from os import path, getcwd

setup(
    name="rdfhash",
    version="0.1.0",
    author="Neil Graham",
    author_email="grahamneiln@gmail.com",
    packages=find_packages(
        where='.',
        include=['rdfhash*'],
        exclude=['test']
    ),
    scripts=["bin/rdfhash"],
    url="https://github.com/NeilGraham/rdfhash",
    license="LICENSE.txt",
    description="Command-line tool for hashing blank node triples into unique identifiers. (Default: sha256)",
    long_description=open(path.join(getcwd(), "README.md")).read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "pytest >= 7.1.2",
        "rdflib >= 6.1.1",
    ],
)