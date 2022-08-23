from string import Template

from rdflib import Graph
from rdflib.term import URIRef, BNode

from .helper import hash_string, convert_data_to_graph, rdf_term_to_id, hashlib_methods
from .logger import logger


def rdfhash(
    data,
    format: str = None,
    method: str = "sha256",
    template: str = "${method}:${value}",
    sparql_select_subjects=(
        "SELECT DISTINCT ?s WHERE { ?s ?p ?o . FILTER (isBlank(?s)) }"
    ),
) -> Graph:
    """Hash RDF blank node subjects with sum of their triples.

    Subject hash result is calculated by sorting each triple by
    `{subject} {predicate}.` then joining with `\n`.

    Example:

        Data: `[ <p:name> "John"; <p:age> 24; <p:location> "US" ] .`

        Hash Input:
            `<p:name> "John"^^<http://www.w3.org/2001/XMLSchema#string>.\n`
            `<p:age> "24"^^<http://www.w3.org/2001/XMLSchema#decimal>.\n`
            `<p:location> "US"^^<http://www.w3.org/2001/XMLSchema#string>.\n`

        Hash Output: `<md5:840c3957b27ad45bbfaf3565a46b0d0b>`

    Args:
        data (_type_): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.
        method (str, optional): Hashing method to use. Defaults to "sha256".
        template (str, optional): Template string for hash URI.
            Defaults to "{method}:{value}".
        sparql_select_subject (str, optional): SPARQL SELECT query to return
            list of subjects which will have their triples hashed.

    Returns:
        Graph: Updated 'data' graph.
    """
    # Convert template string to 'Template' class.
    if type(template) != Template:
        template = Template(template)

    # Convert data provided to rdflib.Graph.
    graph: Graph = convert_data_to_graph(data, format)
    len_before = len(graph)

    # Use SPARQL query 'sparql_select_subject' to get list of subjects to hash.
    select_subjects = set([r[0] for r in graph.query(sparql_select_subjects)])

    logger.info(
        f"\n({len(select_subjects)}) Hashing subject triples:\n-- "
        + "\n-- ".join([s.n3() for s in select_subjects])
    )

    hashed_values = {}  # Dictionary of subjects and resolved hash values.

    for s in select_subjects:
        # Continue if subject is already replaced or N/A.
        if (s, None, None) not in graph:
            logger.debug("Subject was already replaced or is N/A: " + s.n3())
            continue

        hashed_values.update(hash_triples(graph, s, method, template, select_subjects))

    logger.info(
        f"\n({len(hashed_values)}) Hashed subjects:\n-- "
        + "\n-- ".join(f"{k.n3()} -> {v.n3()}" for k, v in hashed_values.items())
    )

    len_after = len(graph)
    if len_before == len_after:
        logger.info(f"(=) Graph size did not change: {len_before}")
    else:
        logger.info(
            f"(-{len_before-len_after}) Graph size reduced from {len_before} to {len_after}."
        )

    return graph


def hash_triples(
    graph: Graph,
    subject: URIRef or BNode,
    method="sha256",
    template: str = "${method}:${value}",
    also_subjects: set = None,
    circ_deps: set = None,
):
    """Replaces subject in graph with hash of it's triples.

    If encounters a blank node in the object position, recursively hashes it.

    Args:
        graph (Graph): rdflib.Graph.
        subject (_type_): rdflib.term representing a subject.
        method (str, optional): Hashing method to use. Defaults to "sha256".
        template (str, optional): Template string for hash URI.
            Defaults to "{method}:{value}".
        also_subjects (set, optional) If encounters any of these terms in triples,
            recursively resolves them. Defaults to None.
        circ_deps (set, optional): Set of values which 'subject' cannot be.
            Defaults to None.

    Raises:
        ValueError: If blank node in predicate position of any triples.
        ValueError: If subject does not have triples associated with it.
        ValueError: If circular dependency is detected. Unable to resolve
            current hash.
    """
    hashed_values = {}  # Return dictionary.

    if type(template) != Template:
        template = Template(template)

    if also_subjects == None:
        also_subjects = set()

    if circ_deps == None:
        circ_deps = set()

    # Add current subject to circular dependencies.
    circ_deps.add(subject)

    hash_value_list = []  # List of values to hash. (`${predicate} ${object}.`)
    triples_add = []  # List of triples to replace with hashed subject.

    # Get all triples containing subject.
    triples = [*graph.triples((subject, None, None))]

    # Return if no triples found on subject specified.
    if len(triples) == 0:
        logger.warning("Could not find any triples for subject: " + subject.n3())
        return hashed_values

    # Generate list of `${predicate} ${object}.` for each triple on subject.
    # ----------------------------------------------------------------------

    for triple in triples:
        graph.remove(triple)  # Remove triple from graph.

        triple_new = []

        # Iterate over 'predicate' (1) and 'object' (2).
        for i in range(1, 3):
            term = triple[i]
            if term in also_subjects:
                # If object in circular dependencies, throw error.
                if term in circ_deps:
                    raise ValueError(
                        "Unable to resolve hash. Circular dependency "
                        f"detected: {subject.n3()} <--> {term.n3()}"
                    )

                # Recursive Call.
                # ---------------
                # Resolve hash value of nested triples first.
                hashed_values.update(
                    hash_triples(
                        graph, term, method, template, also_subjects, circ_deps
                    )
                )
                triple_new.append(hashed_values[term])
            else:
                triple_new.append(term)

        # Append predicate and object to list to be added later with hashed subject.
        triples_add.append(triple_new)

        # Append `{predicate} {object}.\n` to list of values to hash.
        hash_value_list.append(
            f"{rdf_term_to_id(triple_new[0])} {rdf_term_to_id(triple_new[1])}.\n"
        )

    # Sort and concatenate list, hash value, then add to graph.
    # ---------------------------------------------------------

    # Sort list of strings: `{predicate} {object}.\n`
    hash_value_list.sort()

    # Join list of strings to be hashed.
    hash_value = "".join(hash_value_list)

    logger.debug(f'({len(hash_value_list)}) Hashing triple set: """{hash_value}"""')

    # Concatenate sorted list, hash with method, then add to a URIRef.
    hash_dict = {"method": method, "value": hash_string(hash_value, method)}
    hash_subject = URIRef(template.substitute(**hash_dict))

    logger.debug(f"Result of hashed triples: {hash_subject.n3()}")

    # Add triples to graph with hashed subject.
    for pred_obj in triples_add:
        graph.add((hash_subject, *pred_obj))

    # Replace instances of current subject in the object position.
    for triple in graph.triples((None, None, subject)):
        graph.remove(triple)
        graph.add((triple[0], triple[1], hash_subject))

    # Add hashed subject to 'hashed_values' and return.
    hashed_values[subject] = hash_subject
    return hashed_values


def reverse_hash(data, format: str = None) -> Graph:
    """Convert hashed URIs to blank nodes.

    Args:
        data (_type_): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.

    Returns:
        Graph: Updated 'data' graph.
    """
    bnode_int = 0
    bnode_dict = {}

    # Convert data provided to rdflib.Graph.
    graph: Graph = convert_data_to_graph(data, format)

    # Check every term in graph.
    for triple in graph:
        new_triple = []  # Replaces 'triple'.
        updated = False  # Tracks whether 'new_triple' is different to 'triple'.

        for term in triple:
            # Skip update if starts with 'http' (most common case).
            # No hash method is expected to start with this string.
            if term.startswith("http"):
                new_triple.append(term)
            # If URI is already replaced, use replacement.
            elif term in bnode_dict:
                updated = True
                new_triple.append(bnode_dict[term])
            # Check to see if term starts with any of the possible hash methods.
            elif any(
                term.startswith(hash_string + ":")
                for hash_string in hashlib_methods.keys()
            ):
                updated = True
                bnode = BNode(bnode_int)
                bnode_int += 1
                bnode_dict[term] = bnode
                new_triple.append(bnode)
            # If does not start with hash method, do not update.
            else:
                new_triple.append(term)

        # If 'new_triple' is different to 'triple', replace with new.
        if updated:
            graph.remove(triple)
            graph.add(new_triple)

    return graph
