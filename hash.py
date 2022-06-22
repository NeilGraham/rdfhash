import hashlib

from rdflib import Graph
from rdflib.term import URIRef, BNode

hash_methods = {
    "sha1": lambda s: hashlib.sha1(s.encode("utf-8")).hexdigest(),
    "sha256": lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest(),
}


def rdf_hash(data, format="turtle", method="sha256"):
    """Hash RDF blank nodes with

    Args:
        data (_type_): _description_
        format (str, optional): _description_. Defaults to "turtle".
        method (str, optional): _description_. Defaults to "sha256".

    Returns:
        _type_: _description_
    """
    graph = Graph().parse(data=data, format=format)

    # Check all subjects to see whether they are a blank node.
    for [s] in graph.query("select distinct ?s where { ?s ?p ?o }"):
        # Continue if not a blank node or if already hashed.
        if type(s) != BNode or (s, None, None) not in graph:
            continue

        hash_triples(graph, s, method=method)

    return graph


def hash_triples(graph, subject, method="sha256", circ_deps=None):
    """Replaces subject in graph with hash of it's triples.

    Args:
        graph (_type_): _description_
        subject (_type_): _description_
        method (str, optional): _description_. Defaults to "sha256".
        circ_deps (_type_, optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_
    """
    # Initialize set of circular dependencies; Add subject.
    if circ_deps == None:
        circ_deps = set()
    circ_deps.add(subject)

    triples = [*graph.triples((subject, None, None))]
    value_list = []
    triples_add = []
    for triple in triples:
        if type(triple[2]) == BNode:
            # If subject in circular dependency set, throw error.
            if triple[2] in circ_deps:
                raise ValueError(
                    f"Circular dependency detected: {subject} <--> {triple[2]}"
                )
            nested_hash = hash_triples(graph, subject, method="sha256", circ_deps=None)
            triples_add.append((triple[1], nested_hash))
            value_list.append(f"{triple[1].n3()} {nested_hash.n3()}.")
            graph.remove(triple[0], triple[1], nested_hash)

        else:
            triples_add.append((triple[1], triple[2]))
            value_list.append(f"{triple[1].n3()} {triple[2].n3()}.")
            graph.remove(triple)

    value_list.sort()
    hash_subject = URIRef(method + ":") + hash_methods[method]("\n".join(value_list))
    for triple in triples_add:
        graph.add([hash_subject, triple[0], triple[1]])

    # Replace instances of subject in the object position.
    for triple in graph.triples((None, None, subject)):
        graph.remove(triple)
        graph.add((triple[0], triple[1], hash_subject))

    return hash_subject
