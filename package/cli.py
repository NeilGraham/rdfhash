import argparse
import sys
import logging

from .main import hash_subjects, reverse_hash_subjects
from .logger import logger
from .utils.hash import hashlib_methods
from .utils.graph import mime, file_ext


def get_parser():
    """Return argument parser for command 'hash_subjects'.
    Returns: argparse.ArgumentParser: _description_
    """
    parser = argparse.ArgumentParser(
        description=(
            "Replace selected subjects with hash of their triples "
            "(`{predicate} {object}.\\n` sorted & joined)."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "data",
        nargs="+",
        help="Input RDF string or file path. Supported file formats are '.nt', '.nq', '.ttl', '.trig', '.n3', '.xml', '.rdf'.",
    )

    parser.add_argument(
        "-f",
        "--format",
        help="Input format. Supports 'turtle', 'ntriples', 'nquads', 'xml', 'n3'.",
        default="text/turtle",
    )

    parser.add_argument(
        "-g",
        "--graph",
        default="oxrdflib",
        help="Graph library to use. Supports 'oxrdflib', 'rdflib', 'oxigraph'.",
    )

    parser.add_argument(
        "-a",
        "--accept",
        default="text/turtle",
        help="Output accept format. Supports 'turtle', 'ntriples', 'nquads', 'xml', 'n3'.",
    )

    parser.add_argument(
        "-t",
        "--template",
        default="{method}:{value}",
        help="Hash URI template. '{method}' corresponds to the hashing method (eg. 'sha256'). '{value}' corresponds to the calculated hash value.",
    )

    parser.add_argument(
        "-m",
        "--method",
        "--hash-method",
        default="sha256",
        help="Hash method. Supports '" + "', '".join(hashlib_methods.keys()) + "'.",
    )

    parser.add_argument(
        "-s",
        "--sparql",
        "--sparql-select-subjects",
        default="SELECT DISTINCT ?s WHERE { ?s ?p ?o . FILTER (isBlank(?s)) }",
        help="SPARQL SELECT query returning subject URIs to replace with hash of"
        " their triples. Defaults to all blank node subjects.",
    )

    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Reverse hashed URIs to Blank Nodes. --template is used to identify hashed URI te",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show 'info' level logs.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show 'debug' level logs.",
    )

    return parser


def cli(args_list=None):
    """
    Parse arguments and pass to function 'hash_subjects'. Serialize results with
    respect to 'accept' argument.
    """
    # Parse arguments.
    if args_list == None:
        args_list = sys.argv[1:]
    parser = get_parser()
    args = parser.parse_args(["--help"] if len(args_list) == 0 else sys.argv[1:])

    if args.format in mime:
        args.format = mime[args.format]
    elif args.format in file_ext:
        args.format = file_ext[args.format]
    elif args.format not in mime.values():
        parser.print_usage()
        print(f"\nERROR: Unsupported format: {args.format}")
        sys.exit(1)

    if args.accept in mime:
        args.accept = mime[args.accept]
    elif args.accept in file_ext:
        args.accept = file_ext[args.accept]
    elif args.accept not in mime.values():
        parser.print_usage()
        print(f"\nERROR: Unsupported accept format: {args.accept}")
        sys.exit(1)

    if args.data == None:
        parser.print_usage()
        print("\nERROR: The following arguments are required: -d/--data")
        sys.exit(1)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)

    graph, hashed_values = hash_subjects(
        args.data, args.format, args.method, args.template, args.sparql, args.graph
    )

    if args.reverse:
        reverse_hash_subjects(graph, args.format, args.template, args.graph)

    print(graph.serialize(format=args.accept))
