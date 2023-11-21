from rdfhash.utils.hash import hash_string, hashlib_methods
from rdfhash.utils.graph import get_graph, Graph
from rdfhash.utils import validate_uri
from rdfhash.logger import logger

import rdflib

def hash_graph(rdfdb:Graph, onto_rdfdb:Graph=None, classes:list[str]=[], blank_nodes=True, format=None, hash_function="sha256"):
    
    if onto_rdfdb is None:
        onto_rdfdb = rdfdb
    
    # Set of all subjects to hash
    _s = set()
    
    # Find all blank nodes in graph
    # _____________________________
    if blank_nodes:
        # Iterate over all subjects, determine if blank node, and hash if so.
        for s in rdfdb.subjects():
            if isinstance(s, rdflib.BNode):
                # Hash blank node
                # ______________
                # Hash all triples
                _s.add(rdfdb.triples((s, None, None)))
    
    # Find all instances associated with specified classes
    # ____________________________________________________
    class_subjects = {}
    for _c in classes:
        class_subjects[_c] = list(rdfdb.subjects(rdflib.RDF.type, rdflib.URIRef(_c)))
        _s.add(class_subjects[_c])
    
    # Accumulate triples for hash digest, validate that predicates and objects do not reference blank nodes that have
    for _subject in _s:
        rdfdb.triples((_subject, None, None))
        