import logging

from rdflib import Graph
from rdflib.term import URIRef, BNode

from helper import hash_string, convert_data_to_graph


def rdf_hash(data, format: str = None, method: str = "sha256") -> Graph:
    """Hash RDF blank node subjects with sum of their triples.

    Sum of triples is calculated by concatenating the predicate and object
    off of a single subject, sorting all concatenated values, and hashing
    the result.

    Args:
        data (_type_): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.
        method (str, optional): Hashing method to use. Defaults to "sha256".

    Returns:
        Graph: rdflib.Graph.
    """
    graph = convert_data_to_graph(data, format)

    # Check all subjects to see whether they are a blank node.
    for [s] in graph.query("select distinct ?s where { ?s ?p ?o }"):
        # Continue if not a blank node or if already replaced.
        if type(s) != BNode or ((s, None, None) not in graph):
            continue

        hash_triples(graph, s, method)

    return graph


def hash_triples(graph: Graph, subject, method="sha256", circ_deps: set = None):
    """Replaces subject in graph with hash of it's triples.

    If encounters a blank node in the object position, recursively hashes it.

    Args:
        graph (Graph): rdflib.Graph.
        subject (_type_): rdflib.term representing a subject.
        method (str, optional): Hashing method to use. Defaults to "sha256".
        circ_deps (set, optional): Set of . Defaults to None.

    Raises:
        ValueError: If blank node in predicate position of any triples.
        ValueError: If subject does not have triples associated with it.
        ValueError: If circular dependency is detected. Unable to resolve
            current hash.
    """
    # Initialize set of circular dependencies.
    if circ_deps == None:
        circ_deps = set()
    # Add current subject to circular dependencies.
    circ_deps.add(subject)

    hash_value_list = []  # List of values to hash. (`${predicate} ${object}.`)
    triples_add = []  # List of triples to replace with hashed subject.

    # Get all triples containing subject.
    triples = [*graph.triples((subject, None, None))]

    # Throw error if subject
    if len(triples) == 0:
        raise ValueError(f"Could not find triples on subject: {subject.n3()}")

    for triple in triples:
        graph.remove(triple)  # Remove triple from graph.
        nested_hash = None

        # If blank node in predicate position, throw error.
        if type(triple[1]) == BNode:
            raise ValueError(
                f"Blank node cannot be in predicate position: "
                + " ".join(part.n3() for part in triple)
            )

        # If encountered another blank node, recursively hash it.
        if type(triple[2]) == BNode:
            # If object in circular dependencies, throw error.
            if triple[2] in circ_deps:
                raise ValueError(
                    "Unable to resolve hash. Circular dependency "
                    f"detected: {subject.n3()} <--> {triple[2].n3()}"
                )
            # Recursive call; Resolve hash value of nested triples first.
            nested_hash = hash_triples(graph, triple[2], method, circ_deps)

        # Append predicate and object to list to be added later with hashed subject.
        triples_add.append((triple[1], nested_hash or triple[2]))
        # Add concatenated predicate and object to list of values to hash.
        hash_value_list.append(f"{triple[1].n3()} {(nested_hash or triple[2]).n3()}.")

    # Sort list of strings representing concatenated predicate + object.
    hash_value_list.sort()
    # Join list of strings with '\n'.
    hash_value = "\n".join(hash_value_list)

    logging.debug(f"Hashing triple set ({len(hash_value_list)}): '{hash_value}'")

    # Concatenate sorted list, hash with method, then add to a URIRef.
    hash_subject = URIRef(method + ":") + hash_string(hash_value, method)

    logging.debug(f"Result of hashed triples: {hash_subject.n3()}")

    # Add triples to graph with hashed subject.
    for pred_obj in triples_add:
        graph.add((hash_subject, *pred_obj))

    # Replace instances of current subject in the object position.
    for triple in graph.triples((None, None, subject)):
        graph.remove(triple)
        graph.add((triple[0], triple[1], hash_subject))

    return hash_subject
