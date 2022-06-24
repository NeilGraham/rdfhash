from os import getcwd, path, listdir
import logging
from pathlib import Path

from rdflib import Graph
import pytest

from hash import rdf_hash

hash_methods = ["sha256", "md5"]


def test__hash_examples(write_output=False):
    # Get list of all items (files+directories) in './examples'.
    test_files = set(Path(v).name for v in listdir(path.join(getcwd(), "examples")))

    results = {"not_found": [], "successful": [], "failed": []}

    for file in test_files:
        file_path = path.join(getcwd(), "examples", file)

        # If is not a file, skip.
        if not path.isfile(file_path):
            continue

        # Iterate over hash methods defined above.
        for method in hash_methods:
            hash_file_path = path.join(
                getcwd(),
                "examples",
                "hashed",
                f"{path.splitext(file)[0]}__{method}.ttl",
            )

            # Generate hash of blank nodes in example file.
            graph = rdf_hash(file_path, method=method)

            # If hash file does not exist, add to results and continue.
            if not path.isfile(hash_file_path):
                logging.warning(f"Cannot find hash file at path: {hash_file_path}")
                results["not_found"].append(hash_file_path)

                # Create hash file if 'write_output' is True.
                if write_output:
                    logging.warning(f"Writing to file path: {hash_file_path}")
                    graph.serialize(hash_file_path)

                continue

            graph_actual = Graph().parse(hash_file_path)

            # Check to see that both graphs are the exact same.
            if graph.isomorphic(graph_actual):
                logging.info(
                    f"Verified hash method against example file: '{file}' ({method})"
                )
                results["successful"].append(file_path)

            # If the hash is not correct, append to 'failed' and continue.
            else:
                logging.error(
                    f"Hash method failed against example file: '{file}' ({method})"
                )
                results["failed"].append(file_path)

                continue

    # Log warning if any expected files were not found.
    if len(results["not_found"]) > 0:
        logging.warning(
            f"({len(results['not_found'])}) Could not find corresponding hash files."
        )

    # Fail test if any files failed.
    if len(results["failed"]) > 0:
        pytest.fail(
            f"({len(results['failed'])}) The following files failed the hash test: \n"
            + "\n-- ".join(results["failed"])
        )

    # Log final success message.
    logging.info(
        f"({len(results['successful'])}) Successfully verified hash methods against all example files."
    )
