from setuptools import setup, find_packages
from os import path, getcwd

setup(
    name="rdfhash",
    version="0.3.3",
    author="Neil Graham",
    author_email="grahamneiln@gmail.com",
    url="https://github.com/NeilGraham/rdfhash",
    license_files="LICENSE.txt",
    description="De-duplicate RDF triples w/ a SPARQL query. Subjects taken from SELECT are replaced by the hash of their triples '{predicate} {object}.\n' pairs sorted.",
    long_description=open(path.join(getcwd(), "README.md")).read()
    # Replace local links to 'docs/' to Github page 'docs/'.
    .replace(
        "](docs/",
        "](https://github.com/NeilGraham/rdfhash/blob/master/docs/",
    ),
    long_description_content_type="text/markdown",
    packages=["rdfhash"],
    package_dir={"rdfhash": "package"},
    entry_points={"console_scripts": ["rdfhash = rdfhash.cli:cli"]},
    python_requires=">=3.6",
    install_requires=[
        "pytest >= 7.1.2",
        "rdflib >= 6.1.1",
    ],
)
