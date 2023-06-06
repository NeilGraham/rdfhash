from rdfhash.utils.hash import hash_string, hashlib_methods
from rdfhash.utils.graph import get_graph
from rdfhash.utils import validate_uri
from rdfhash.logger import logger


def hash_subjects(
    data,
    format=None,
    method="sha256",
    template="{method}:{value}",
    sparql_select_subjects=("SELECT DISTINCT ?s { ?s ?p ?o . FILTER (isBlank(?s)) }"),
    graph_type="oxrdflib",
    length=None,
):
    """Hash subjects by the sum of their triples.

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
        data (str|rdflib.Graph): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.
        method (str, optional): Hashing method to use. Defaults to "sha256".
        template (str, optional): Template string for hash URI.
            Defaults to "{method}:{value}".
        sparql_select_subject (str, optional): SPARQL SELECT query to return
            list of subjects which will have their triples hashed.
        graph_type (str, optional): Graph type to use. Defaults to "oxrdflib".
        length (int, optional): Length of hash result. Required for some hash methods,
            optional for all.

    Returns:
        rdflib.Graph: Updated 'data' graph.
    """

    # Convert data provided to rdflib.Graph.
    graph = get_graph(data, format, graph_type)
    len_before = len(graph)

    # Use SPARQL query 'sparql_select_subject' to get list of subjects to hash.
    select_subjects = set()
    for row in graph.query(sparql_select_subjects):
        for item in row:
            select_subjects.add(item)

    logger.info(
        f"\n({len(select_subjects)}) Hashing subject triples:\n-- "
        + "\n-- ".join([graph.term_to_string(s) for s in select_subjects])
    )

    hashed_values = {}  # Dictionary of subjects and resolved hash values.

    spec_length = None
    if ":" in method:
        method, spec_length = method.split(":")
        spec_length = int(spec_length)

    for s in select_subjects:
        if s in hashed_values:
            continue

        # Continue if subject is already replaced or N/A.
        if (s, None, None) not in graph:
            logger.warning(
                "Selected subject not found in graph: " + graph.term_to_string(s)
            )
            continue

        hashed_values.update(
            hash_subject(
                graph,
                s,
                method,
                template,
                select_subjects,
                length=length or spec_length,
            )
        )

    logger.info(
        f"\n({len(hashed_values)}) Hashed subjects:\n-- "
        + "\n-- ".join(
            f"{graph.term_to_string(k)} -> {graph.term_to_string(v)}"
            for k, v in hashed_values.items()
        )
    )

    len_after = len(graph)
    if len_before == len_after:
        logger.info(f"(=) Graph size did not change: {len_before}")
    else:
        logger.info(
            f"(-{len_before-len_after}) Graph size reduced from {len_before} to {len_after}."
        )

    return graph, hashed_values


def hash_subject(
    graph,
    subject,
    method="sha256",
    template="{method}:{value}",
    also_subjects=None,
    circ_deps=None,
    length=None,
):
    """Replaces subject in graph with hash of it's triples.

    If encounters a blank node in the object position, recursively hashes it.

    Updates 'graph' rdflib.Graph but does not return anything.

    Args:
        graph (rdflib.Graph): rdflib.Graph.
        subject (_type_): rdflib.term representing a subject.
        method (str, optional): Hashing method to use. Defaults to "sha256".
        template (str, optional): Template string for hash URI.
            Defaults to "{method}:{value}".
        also_subjects (set, optional) If encounters any of these terms in triples,
            recursively resolves them. Throws error if circular dependency found.
            Defaults to None.
        circ_deps (set, optional): Set of values which 'subject' cannot be.
            Defaults to None.
        length (int, optional): Length of hash result. Required for some hash methods,
            optional for all.

    Raises:
        ValueError: If blank node in predicate position of any triples.
        ValueError: If subject does not have triples associated with it.
        ValueError: If circular dependency is detected. Unable to resolve
            current hash.
    """
    hashed_values = {}  # Return dictionary.

    # if type(template) != Template:
    #     template = Template(template)

    if also_subjects == None:
        also_subjects = set()

    if circ_deps == None:
        circ_deps = set()

    # Add current subject to circular dependencies.
    circ_deps.add(subject)

    hash_input_list = []  # List of values to hash. (`${predicate} ${object}.`)
    triples_add = []  # List of triples to replace with hashed subject.

    # Get all triples containing subject.
    triples = [*graph.triples((subject, None, None))]

    # Return if no triples found on subject specified.
    if len(triples) == 0:
        logger.warning(
            "Could not find any triples for subject: " + graph.term_to_string(subject)
        )
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
                        f"detected: {graph.term_to_string(subject)} <--> {graph.term_to_string(term)}"
                    )

                # Recursive Call.
                # ---------------
                # Resolve hash value of nested triples first.
                hashed_values.update(
                    hash_subject(
                        graph, term, method, template, also_subjects, circ_deps, length
                    )
                )
                triple_new.append(hashed_values[term])
            else:
                triple_new.append(term)

        # Append predicate and object to list to be added later with hashed subject.
        triples_add.append(triple_new)

        # Append `{predicate} {object}.\n` to list of values to hash.
        hash_input_list.append(
            f"{graph.term_to_string(triple_new[0], True)} {graph.term_to_string(triple_new[1], True)}.\n"
        )

    # Sort and concatenate list, hash value, then add to graph.
    # ---------------------------------------------------------

    # Sort list of strings: `{predicate} {object}.\n`
    hash_input_list.sort()

    # Join list of strings to be hashed.
    hash_input = "".join(hash_input_list)

    logger.debug(f'({len(hash_input_list)}) Hashing triple set: """{hash_input}"""')

    # Concatenate sorted list, hash with method, then add to a URIRef.
    hash_dict = {"method": method, "value": hash_string(hash_input, method, length)}
    hash_subj = graph.NamedNode(template.format(**hash_dict))

    logger.debug(f"Result of hashed triples: {graph.term_to_string(hash_subj)}")

    # Add triples to graph with hashed subject.
    for pred_obj in triples_add:
        graph.add((hash_subj, *pred_obj))

    # Replace instances of current subject in the object position.
    for triple in graph.triples((None, None, subject)):
        graph.remove(triple)
        graph.add((triple[0], triple[1], hash_subj))

    # Add hashed subject to 'hashed_values' and return.
    hashed_values[subject] = hash_subj
    return hashed_values


def reverse_hash_subjects(
    data, format=None, template="{method}:{value}", graph_type="oxrdflib"
):
    """Convert hashed URIs to blank nodes.

    Args:
        data (_type_): Data representing RDF triples.
        format (str, optional): Format of data. Defaults to None.

    Returns:
        rdflib.Graph: Updated 'data' graph.
    """
    bnode_int = 0
    bnode_dict = {}

    graph = get_graph(data, format, graph_type)

    # Check every term in graph.
    for triple in graph.triples():
        new_triple = []  # Replaces 'triple'.
        updated = False  # Tracks whether 'new_triple' is different to 'triple'.

        for term in triple:
            if term in bnode_dict:
                updated = True
                new_triple.append(bnode_dict[term])
            # If term matches 'template' regex, replace with blank node.
            elif graph.is_uri(term) and validate_uri(
                graph.term_to_string(term)[1:-1], template
            ):
                updated = True
                bnode = graph.BlankNode(bnode_int)
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
