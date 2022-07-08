import argparse
import sys
import logging


from package.logger import logger
from package.helper import hashlib_methods
from package import rdfhash


def parse_args(args: list[str]) -> argparse.Namespace:
    """Use argparse to parse list of arguments."""
    parser = argparse.ArgumentParser(
        description="Replace selected subjects with hash of their triples "
        "(`{predicate} {object}.\\n` sorted + joined).",
    )

    parser.add_argument("-d", "--data", required=True, help="Input data. (RDF)")

    parser.add_argument(
        "-f",
        "--format",
        help="Input format.",
        default=None,
        choices=["turtle", "n-triples", "trig", "n-quads", "n3", "rdf"],
    )

    parser.add_argument(
        "-m",
        "--method",
        help="Hash method.",
        default="sha256",
        choices=hashlib_methods.keys(),
    )

    parser.add_argument(
        "-a",
        "--accept",
        help="Accept format.",
        default=["turtle"],
        nargs="+",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Show 'info' level logs.",
        action="store_true",
    )

    parser.add_argument(
        "--debug",
        help="Show 'debug' level logs.",
        action="store_true",
    )

    parser.add_argument(
        "--sparql",
        "--sparql-select-subjects",
        default="SELECT DISTINCT ?s WHERE { ?s ?p ?o . FILTER (isBlank(?s)) }",
        help="SPARQL SELECT query returning subject URIs to replace with hash of"
        " their triples. Defaults to all blank node subjects.",
    )

    return parser.parse_args(args)


def run():
    """
    Parse arguments and pass to function 'rdfhash'. Serialize results with
    respect to 'accept' argument.
    """
    # Parse arguments.
    args = parse_args(sys.argv[1:])

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)

    graph = rdfhash(args.data, args.format, args.method, args.sparql)

    print(graph.serialize(format=args.accept[0]))


if __name__ == "__main__":
    run()
