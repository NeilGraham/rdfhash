import argparse
import sys
import logging

from .hash import rdfhash, reverse_hash
from .logger import logger
from .helper import hashlib_methods


def add_io_args(parser: argparse.ArgumentParser):
    """Adds 'input/output' arguments to given parser/subparser.
    Args: parser (argparse.ArgumentParser): parser/subparser
    """
    parser.add_argument(
        "-d", "--data", help="Input RDF string or file. (.ttl, .nt, .n3)"
    )

    parser.add_argument(
        "-f",
        "--format",
        help="Input format.",
        default=None,
        choices=["turtle", "n-triples", "trig", "n-quads", "n3", "rdf"],
    )

    parser.add_argument(
        "-a",
        "--accept",
        help="Output accept format.",
        default=["turtle"],
        nargs="+",
    )


def add_debug_args(parser: argparse.ArgumentParser):
    """Adds 'debug' arguments to given parser/subparser.
    Args: parser (argparse.ArgumentParser): parser/subparser
    """
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


def get_parser() -> argparse.ArgumentParser:
    """Return argument parser for command 'rdfhash'.
    Returns: argparse.ArgumentParser: _description_
    """
    parser = argparse.ArgumentParser(
        description=(
            "Replace selected subjects with hash of their triples "
            "(`{predicate} {object}.\\n` sorted + joined)."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparser = parser.add_subparsers(dest="command")

    # ____________________________
    #
    # Default arguments: 'rdfhash'
    # ____________________________

    add_io_args(parser)

    add_debug_args(parser)

    parser.add_argument(
        "-t",
        "--template",
        default="${method}:${value}",
        help="Template string for hash URI. 'method' corresponds to the hashing method. 'value' corresponds to the hash value.",
    )

    parser.add_argument(
        "-m",
        "--method",
        "--hash-method",
        help="Hash method.",
        default="sha256",
        choices=hashlib_methods.keys(),
    )

    parser.add_argument(
        "--sparql",
        "--sparql-select-subjects",
        default="SELECT DISTINCT ?s WHERE { ?s ?p ?o . FILTER (isBlank(?s)) }",
        help="SPARQL SELECT query returning subject URIs to replace with hash of"
        " their triples. Defaults to all blank node subjects.",
    )

    # ______________________________________
    #
    # Sub-command 'reverse' ('reverse_hash')
    # ______________________________________

    parser_reverse = subparser.add_parser(
        "reverse", help="Reverse hashed URIs to blank nodes."
    )

    add_io_args(parser_reverse)

    add_debug_args(parser_reverse)

    return parser


def run(args_list: list[str] = None):
    """
    Parse arguments and pass to function 'rdfhash'. Serialize results with
    respect to 'accept' argument.
    """
    # Parse arguments.
    if args_list == None:
        args_list = sys.argv[1:]
    parser = get_parser()
    args = parser.parse_args(["--help"] if len(args_list) == 0 else sys.argv[1:])

    if args.data == None:
        parser.print_usage()
        print("\nERROR: The following arguments are required: -d/--data")
        sys.exit(1)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.INFO)

    match args.command:
        case None:
            graph = rdfhash(
                args.data, args.format, args.method, args.template, args.sparql
            )
            print(graph.serialize(format=args.accept[0]))
            sys.exit(0)
        case "reverse":
            graph = reverse_hash(args.data, args.format)
            print(graph.serialize(format=args.accept[0]))
            sys.exit(0)
        case _:
            parser.print_usage()
            print(f"\nERROR: Command is not implemented: {args.command}")
            sys.exit(1)
