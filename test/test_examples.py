from os import getcwd, path, listdir
from pathlib import Path

from rdflib import Graph
import pytest

from rdfhash import rdfhash
from rdfhash.logger import logger

hash_methods = ["sha256"]


def test__hash_examples(force_write=False):
    """Test hashing files in './examples'.

    Args:
        force_write (bool, optional): If True, forces writing hash
            result to file './examples/hashed'. Defaults to True.
    """
    # Get list of all items (files+directories) in './examples'.
    test_files = set(Path(v).name for v in listdir(path.join(getcwd(), "examples")))

    results = {"not_found": [], "successful": [], "failed": [], "wrote": []}

    # Iterate over each file in './examples'.
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
            graph = rdfhash(file_path, method=method)
            
            # Create hash file if 'write_output' is True.
            if force_write:
                logger.warning(f"Writing to file path: {hash_file_path}")
                graph.serialize(hash_file_path)
                results['wrote'].append(hash_file_path)
                continue

            # If hash file does not exist, add to results and continue.
            if not path.isfile(hash_file_path):
                logger.warning(f"Cannot find hash file at path: {hash_file_path}")
                results["not_found"].append(hash_file_path)

                continue

            graph_actual = Graph().parse(hash_file_path)

            # Check to see that both graphs are the exact same.
            if graph.isomorphic(graph_actual):
                logger.info(
                    "Successfully verified hash against file: "
                    f"'{file}' <-> '{hash_file_path}' ({method})"
                )
                results["successful"].append(file_path)

            # If the hash is not correct, append to 'failed' and continue.
            else:
                logger.error(
                    "Mismatch between calculated hash and file: "
                    f"'{file}' -> '{hash_file_path}' ({method}) "
                )
                results["failed"].append(file_path)

                continue

    # Log warning if any expected files were not found.
    if len(results["not_found"]) > 0:
        logger.warning(
            f"\n\n({len(results['not_found'])}) Could not find corresponding hash "
            "files:\n-- " + "\n-- ".join(results["not_found"])
        )

    # Fail test if any files failed.
    if len(results["failed"]) > 0:
        pytest.fail(
            f"\n\n({len(results['failed'])}) The following files failed the hash test: \n-- "
            + "\n-- ".join(results["failed"])
        )
    
    if len(results["successful"]) > 0:
        
        # Log final success message.
        logger.info(
            f"\n\n({len(results['successful'])}) Successfully verified hash methods "
            "against example files:\n-- " + "\n-- ".join(results["successful"])
        )
    else:
        
        # No files were verified.
        logger.info("No files were verified.")
        if len(results['wrote']) > 0:
            logger.info(
                f"\n\n({len(results['wrote'])}) The following files were written to: \n-- "
                + "\n-- ".join(results['wrote'])
            )
