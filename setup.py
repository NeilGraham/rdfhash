from setuptools import setup, find_packages
from os import path, getcwd

setup(
    name="rdfhash",
    version="0.4.6",
    author="Neil Graham",
    author_email="grahamneiln@gmail.com",
    url="https://github.com/NeilGraham/rdfhash",
    license_files="LICENSE.txt",
    description="De-duplicate RDF triples w/ a SPARQL query. Subjects taken from SELECT are replaced by the hash of their triples '{predicate} {object}.\n' pairs sorted.",
    long_description=open(path.join(getcwd(), "README.md")).read()
    # Replace relative links with absolute links to GitHub for PyPi
    .replace(
        "](docs/",
        "](https://github.com/NeilGraham/rdfhash/blob/master/docs/",
    ),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={"console_scripts": ["rdfhash = rdfhash.cli:cli"]},
    python_requires=">=3.7",
    install_requires=[
        "pytest >= 7.1.2",
        "rdflib >= 6.1.1",
        "oxrdflib >= 0.3.4",
        "pyoxigraph >= 0.3.16",
    ],
)
