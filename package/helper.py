import hashlib
from os.path import isfile

from rdflib import Graph
from rdflib.term import URIRef, Literal, BNode, Variable


hashlib_methods = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha3_224": hashlib.sha3_224,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_384,
    "sha3_512": hashlib.sha3_512,
    # "shake_128": hashlib.shake_128,
    # "shake_256": hashlib.shake_256,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}


def hash_string(s: str, method="sha256", hashlib_options={}) -> str:
    """Hash a Python string with a given

    Args:
        s (str): _description_
        method (str, optional): _description_. Defaults to "sha256".

    Raises:
        ValueError: _description_

    Returns:
        str: Hexadecimal string representation of hash.
    """
    if method in hashlib_methods:
        return hashlib_methods[method](s.encode("utf-8"), **hashlib_options).hexdigest()
    else:
        raise ValueError(f"Invalid hashing method: {method}")


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


def rdf_term_to_id(term: URIRef or Literal or BNode or Variable) -> str:
    """Convert rdflib.term to a resolvable identifier. This is useful for hashing.

    Args:
        term (URIRef or Literal or BNode or Variable): rdflib.term.

    Returns:
        str: String identifier for rdflib.term.
    """
    type_t = type(term)

    if type_t == URIRef:
        return term.n3()
    elif type_t == Literal:
        return (
            # If is an 'xsd:string', manually form id.
            f'"{term.value}"^^<http://www.w3.org/2001/XMLSchema#string>'
            if term.datatype == None
            # Else use '.n3()' to form id.
            else term.n3()
        )
    else:
        raise ValueError(
            "RDF Term type cannot be converted to a resolvable identifier: "
            + str(type_t)
        )
