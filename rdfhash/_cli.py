import argparse
import sys
import logging

from rdfhash.main import hash_graph, reverse_hash_subjects
from rdfhash.logger import logger

def get_argparser():
    parser = argparse.ArgumentParser(
        description=(
            "Replace selected subjects with hash of their triples "
            "(`{predicate} {object}.\\n` sorted & joined)."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "--files",
        "-f",
        nargs="*",
        help="Files to hash"
    )
    parser.add_argument(
        "--endpoint",
        "-e",
        help="SPARQL endpoint"
    )
    parser.add_argument(
        "--ontology-files",
        "-o",
        help="Ontology files to base hash on"
    )
    parser.add_argument("--subjects", "-s", nargs="*", help="Subjects to hash")
    parser.add_argument(
        "--classes", "-c", nargs="*", help="Classes to hash. Advanced configuration can be defined on `owl:Class` instances using the namespace `hash: <http://rdfhash.com#>`."
    )
    parser.add_argument(
        "--threads", "-t", type=int, default=1, help="Number of threads to parallelize hashing over"
    )
    
def cli(args_list:list=None):
    parser = get_argparser()
    args = parser.parse_args(args_list)
    _args = vars(args)
    # F