from setuptools import setup, find_packages
from os import path, getcwd

setup(
    name="rdfhash",
    version="0.3.1",
    author="Neil Graham",
    author_email="grahamneiln@gmail.com",
    url="https://github.com/NeilGraham/rdfhash",
    license_files="LICENSE.txt",
    description="Tool for replacing RDF subjects (Default: blank nodes) with hash of their triples (Default: sha256).",
    long_description=open(path.join(getcwd(), "README.md")).read()
    # Replace local links to 'docs/' to Github page 'docs/'.
    .replace(
        "](docs/",
        "](https://github.com/NeilGraham/rdfhash/blob/master/docs/",
    ),
    long_description_content_type="text/markdown",
    packages=["rdfhash"],
    package_dir={"rdfhash": "package"},
    entry_points={"console_scripts": ["rdfhash = rdfhash.__main__:run"]},
    python_requires=">=3.10",
    install_requires=[
        "pytest >= 7.1.2",
        "rdflib >= 6.1.1",
    ],
)
