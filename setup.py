from setuptools import setup, find_packages
from os import path, getcwd

setup(
    name="rdfhash",
    version="0.2.3",
    author="Neil Graham",
    author_email="grahamneiln@gmail.com",
    url="https://github.com/NeilGraham/rdfhash",
    license_files="LICENSE.txt",
    description="Command-line tool for hashing RDF definitions into resolvable identifiers. (Default: sha256)",
    long_description=open(path.join(getcwd(), "README.md")).read(),
    long_description_content_type="text/markdown",
    packages=["rdfhash"],
    package_dir={"rdfhash": "package"},
    entry_points={"console_scripts": ["rdfhash = package.cli:run"]},
    python_requires=">=3.10",
    install_requires=[
        "pytest >= 7.1.2",
        "rdflib >= 6.1.1",
    ],
)
