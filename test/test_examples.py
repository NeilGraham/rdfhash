from os import getcwd, path, listdir
from pathlib import Path
from glob import glob

from rdflib import Graph
import pytest
import oxrdflib

from rdfhash import rdfhash, reverse_hash_subjects
from rdfhash.logger import logger
from rdfhash.utils.hash import (
    hash_types,
    hash_types_requiring_length,
    hash_types_resolvable,
)
from rdfhash.utils.graph import graph_types
from utils import compare_graphs, graph_diff

repo_dir = path.dirname(Path(__file__).parent.absolute())
ttl_files = (
    path.relpath(file) for file in glob(path.join(repo_dir, "examples", "*.ttl"))
)

resolvable_hash_methods = list(hash_types_resolvable.copy())
for i in range(0, len(resolvable_hash_methods)):
    if resolvable_hash_methods[i] in hash_types_requiring_length:
        resolvable_hash_methods[i] = resolvable_hash_methods[i] + ":64"


@pytest.mark.parametrize("file_path", ttl_files)
# @pytest.mark.parametrize("hash_method", resolvable_hash_methods)
@pytest.mark.parametrize("hash_method", ["sha256"])
@pytest.mark.parametrize("graph_type", list(graph_types.keys()))
# @pytest.mark.parametrize("graph_type", ["oxrdflib"])
def test__hash_examples(file_path, hash_method, graph_type, force_write=False):
    """Hash file and compare against hash file.

    Args:
        graph_type (str): Graph type to use.
        force_write (bool, optional): If True, forces writing hash
            result to file './examples/hashed'. Defaults to True.
    """

    success = False
    hash_file_path = path.join(
        path.dirname(file_path),
        "hashed",
        f"{path.splitext(path.basename(file_path))[0]}__{hash_method}.ttl",
    )

    # Generate hash of blank nodes in example file.
    graph, replaced_subjects = rdfhash(
        file_path, method=hash_method, graph_type=graph_type
    )

    graph_actual = (
        None
        if not path.isfile(hash_file_path)
        else Graph(store="Oxigraph").parse(hash_file_path)
    )
    graph_generated = Graph(store="Oxigraph").parse(
        data=graph.serialize(format="text/turtle"), format="text/turtle"
    )

    # If hash file does not exist, continue.
    if graph_actual == None:
        logger.warning(
            f"Cannot find hash file at path, writing to path: {hash_file_path}"
        )
        graph_generated.serialize(hash_file_path, format="text/turtle")
        return

    # Check to see that both graphs are the exact same.
    elif compare_graphs(graph_generated, graph_actual):
        logger.info(
            "Successfully verified hash against file: "
            f"'{file_path}' <-> '{hash_file_path}' ({hash_method})"
        )
        success = True

    # If the hash is not correct, append to 'failed' and continue.
    else:
        logger.error(
            "Mismatch between calculated hash and file: "
            f"'{file_path}' -> '{hash_file_path}' ({hash_method}) "
        )

    # Write output of function to file path if 'force_write' is True.
    if force_write:
        logger.warning(f"Forcing write to file path: {hash_file_path}")
        graph.serialize(hash_file_path, format="text/turtle")

    if not success:
        differences = graph_diff(graph_generated, graph_actual)
        diff_s = ""

        if len(differences["in_g1_not_g2"]) > 0:
            diff_s += "Test File Only:\n"
            for triple in differences["in_g1_not_g2"]:
                diff_s += differences["in_g1_not_g2"].serialize(format="turtle")
            diff_s += "\n\n"

        if len(differences["in_g2_not_g1"]) > 0:
            diff_s += "Reference File Only:\n"
            diff_s += differences["in_g2_not_g1"].serialize(format="turtle")
            diff_s += "\n\n"

        logger.error(diff_s)

        pytest.fail(f"Hash mismatch for file: {file_path} ({hash_method})\n\n{diff_s}")


# def test__reverse_example(file_path, template="{method}:{value}"):
#     graph_generated = reverse_hash_subjects(file_path, )
