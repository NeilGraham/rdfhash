import hashlib
from os.path import isfile

from rdflib import Graph
from rdflib.term import URIRef, BNode

hash_methods = {
    "sha1": lambda s: hashlib.sha1(s.encode("utf-8")).hexdigest(),
    "sha256": lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest(),
}


def convert_data_to_graph(data, format: str = None) -> Graph:
    """Convert data provided to an rdflib.Graph.

    Args:
        data (_type_): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.

    Returns:
        Graph: rdflib.Graph.
    """
    type_data = type(data)

    if type_data == Graph:
        return data

    elif type_data == str:
        # If is a file, parse file and always let rdflib determine format.
        if isfile(data):
            return Graph().parse(data)
        # If not a file, assume it's a string of RDF triples.
        else:
            return Graph().parse(data=data, format=format)

    elif type_data == list:
        graph = Graph()
        # Concatenate graphs together for each item in list.
        for item in data:
            graph = graph + convert_data_to_graph(item, format)
        return graph


def rdf_hash(data, format: str = None, method: str = "sha256"):
    """Hash RDF blank node subjects with sum of their triples.

    Sum of triples is calculated by concatenating the predicate and object
    off of a single subject, sorting all concatenated values, and hashing
    the result.

    Args:
        data (_type_): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.
        method (str, optional): Hashing method to use. Defaults to "sha256".

    Returns:
        _type_: rdflib.Graph.
    """
    graph = convert_data_to_graph(data, format)

    # Check all subjects to see whether they are a blank node.
    for [s] in graph.query("select distinct ?s where { ?s ?p ?o }"):
        # Continue if not a blank node or if already replaced.
        if type(s) != BNode or ((s, None, None) not in graph):
            continue

        # Hash current blank node triples.
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
    for triple in triples:
        graph.remove(triple)  # Remove triple from graph.
        nested_hash = None

        # If encountered another blank node, recursively hash it.
        if type(triple[2]) == BNode:
            # If object in circular dependencies, throw error.
            if triple[2] in circ_deps:
                raise ValueError(
                    "Unable to resolve hash. "
                    f"Circular dependency detected: {subject} <--> {triple[2]}"
                )
            # Recursively hash object before resolving current subject.
            nested_hash = hash_triples(graph, triple[2], method, circ_deps)

        # Append predicate and object to list to be added later with hashed subject.
        triples_add.append((triple[1], nested_hash or triple[2]))
        # Add concatenated predicate and object to list of values to hash.
        hash_value_list.append(f"{triple[1].n3()} {(nested_hash or triple[2]).n3()}.")

    # Sort list of strings representing concatenated predicate + object.
    hash_value_list.sort()
    # Concatenate sorted list, hash with method, then add to a URIRef.
    hash_subject = URIRef(method + ":") + hash_methods[method](
        "\n".join(hash_value_list)
    )

    # Add triples to graph with hashed subject.
    for pred_obj in triples_add:
        graph.add((hash_subject, *pred_obj))

    # Replace instances of current subject in the object position.
    for triple in graph.triples((None, None, subject)):
        graph.remove(triple)
        graph.add((triple[0], triple[1], hash_subject))

    return hash_subject
