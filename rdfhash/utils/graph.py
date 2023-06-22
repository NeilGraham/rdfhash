import os.path
import io

import oxrdflib
import rdflib
import pyoxigraph

from rdfhash.utils.hash import hash_string

mime = {
    "trig": "application/trig",
    "nq": "application/n-quads",
    "nquads": "application/n-quads",
    "ntriples": "application/n-triples",
    "nt": "application/n-triples",
    "turtle": "text/turtle",
    "ttl": "text/turtle",
    "rdf": "application/rdf+xml",
    "xml": "application/rdf+xml",
    "n3": "text/n3",
}

file_ext = {
    "nt": "application/n-triples",
    "nq": "application/n-quads",
    "ttl": "text/turtle",
    "trig": "application/trig",
    "n3": "text/n3",
    "xml": "application/rdf+xml",
    "rdf": "application/rdf+xml",
    "n3": "text/n3",
}

# _____________________________________________________________________________ #


class __Graph__:
    """Interoperable graph class, based on rdflib.ConjunctiveGraph.

    Raises:
        TypeError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_

    Returns:
        _type_: _description_
    """

    graph = None

    library_class = rdflib
    graph_class = rdflib.ConjunctiveGraph

    NamedNode = rdflib.URIRef
    BlankNode = rdflib.BNode
    Literal = rdflib.Literal
    Variable = rdflib.Variable

    xsd_langstring = rdflib.URIRef(
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
    )

    xsd_string = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#string")
    
    xsd_boolean = rdflib.URIRef("http://www.w3.org/2001/XMLSchema#boolean")

    default_format = mime["trig"]

    supports_named_graphs = True

    def __init__(self, data=None, format=None, max_path=2048):
        """Initialize graph object

        Args:
            data (_type_, optional): _description_. Defaults to None.
            format (_type_, optional): _description_. Defaults to None.
            max_path (int, optional): Check if 'data' is a file path if length
                is less than 'max_path'. Specify -1 to always check. Defaults to 2048.
        """
        if self.graph == None:
            self.graph = self.graph_class()

        if data:
            type_data = type(data)

            if type_data == self.graph_class:
                self.graph = data
                return

            elif type_data == str:
                data = [data]

            elif type_data != list:
                raise ValueError(
                    "Argument 'data' must be string or list of strings. Got "
                    + str(type_data)
                )

            # Parse all files into graph.
            for item in data:
                if (max_path == -1 or len(item) < max_path) and os.path.isfile(item):
                    self.parse_file(item, format)
                else:
                    self.parse(item, format)

    def __len__(self):
        return len(self.graph)

    def __contains__(self, item):
        return item in self.graph

    def _parse(self, data, format):
        self.graph.parse(data=data, format=format)

    def _parse_file(self, file_path, format=None):
        self.graph.parse(file_path, format=format)

    def parse(self, data, format=None):
        self._parse(data=data, format=format or self.default_format)
        return self

    def parse_file(self, file_path, format=None):
        if format == None:
            ext = os.path.splitext(file_path)[1][1:]
            if ext not in file_ext:
                raise ValueError("File specified not recognized as a valid RDF file. ")
            self._parse_file(file_path, format=file_ext[ext])
        else:
            self._parse_file(file_path, format=format)
        return self

    def serialize(self, path=None, format=None):
        if path:
            self.graph.serialize(destination=path, format=format or self.default_format)
            return True
        else:
            return self.graph.serialize(format=format or self.default_format)

    def query(self, query):
        res = self.graph.query(query)
        return res

    def subjects(self, predicate=None, object=None):
        return self.graph.subjects(predicate, object)

    def predicates(self, subject=None, object=None):
        return self.graph.predicates(subject, object)

    def objects(self, subject=None, predicate=None):
        return self.graph.objects(subject, predicate)

    def triples(self, triple=None):
        if triple == None:
            return self.graph.triples((None, None, None))
        return self.graph.triples(triple)

    def quads(self, quad=None):
        if quad == None:
            return self.graph.quads((None, None, None, None))
        return self.graph.quads(quad)

    def is_bnode(self, term):
        return type(term) == self.BlankNode

    def is_uri(self, term):
        return type(term) == self.NamedNode

    def is_literal(self, term):
        return type(term) == self.Literal

    def is_variable(self, term):
        return type(term) == self.Variable

    def is_term(self, term, allow_variable=False):
        return any(
            [
                self.is_uri(term),
                self.is_literal(term),
                self.is_bnode(term),
                self.is_variable(term) if allow_variable else False,
            ]
        )

    def term_to_string(self, term, expand_literals=False):
        if expand_literals and type(term) == self.Literal:
            value, datatype, language = term.value, term.datatype, term.language
            if datatype == None:
                if language:
                    datatype = self.xsd_langstring
                else:
                    datatype = self.xsd_string
            if term.language:
                return f'"{value}"^^{datatype.n3()}@{language}'

            return f'"{value}"^^{datatype.n3()}'
        return term.n3()

    def hash_triples(self, triples, method="sha256", triple_format="{p} {o}\n"):
        sorted_triples = sorted(
            triple_format.format(s=s, p=p, o=o) for s, p, o in triples
        )
        joined_triples = "".join(sorted_triples)
        return hash_string(joined_triples, method=method)

    def add(self, triples):
        self.graph.add(triples)
        return self

    def remove(self, triples):
        self.graph.remove(triples)
        return self

    """Available methods:
    __init__
    __len__
    __contains__
    _parse
    _parse_file
    parse
    parse_file
    serialize
    query
    subjects
    predicates
    objects
    quads
    triples
    is_bnode
    is_uri
    is_literal
    term_to_string
    hash_triples
    add
    remove
    """


# __   __   __   __   __   __   __   __   __   __   __   __   __   __   __   __ #


class RdfLibGraph(__Graph__):
    """
    __Graph__ defines interoperable graph class and is based on rdflib.Graph.
    No need to define methods here.
    """


# __   __   __   __   __   __   __   __   __   __   __   __   __   __   __   __ #


class OxRdfLibGraph(RdfLibGraph):
    library_class = oxrdflib
    graph_class = oxrdflib.Graph

    NamedNode = rdflib.URIRef
    BlankNode = rdflib.BNode
    Literal = rdflib.Literal
    Variable = rdflib.Variable

    default_format = mime["trig"]

    supports_named_graphs = True
    """Inheriting methods from RdfLibGraph"""

    def __init__(self, data=None, format=None, max_path=2048):
        self.graph = rdflib.ConjunctiveGraph(store="Oxigraph")
        super().__init__(data, format, max_path)


# __   __   __   __   __   __   __   __   __   __   __   __   __   __   __   __ #


class OxiGraph(__Graph__):
    graph_class = pyoxigraph.Store

    default_format = mime["trig"]

    BlankNode = pyoxigraph.BlankNode
    NamedNode = pyoxigraph.NamedNode
    Literal = pyoxigraph.Literal
    Variable = pyoxigraph.Variable

    Quad = pyoxigraph.Quad

    xsd_string = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#string")
    xsd_boolean = pyoxigraph.NamedNode("http://www.w3.org/2001/XMLSchema#boolean")

    supports_named_graphs = True

    def __contains__(self, item):
        iter = self.quads(item)
        try:
            next(iter)
            return True
        except StopIteration:
            return False

    def _parse(self, data, format):
        input = io.StringIO(data)
        self.graph.load(input, format)
        return self

    def _parse_file(self, path, format):
        self.graph.load(path, format)
        return self

    def serialize(self, path=None, format=None):
        if format == None:
            format = self.default_format
        if path:
            self.graph.dump(path, mime_type=format)
            return True
        else:
            with io.BytesIO() as buffer:
                self.graph.dump(buffer, mime_type=format)
                buffer.seek(0)
                res = buffer.read()
            return res.decode("utf-8")

    def subjects(self, predicate=None, object=None, graph=None):
        return self.graph.quads_for_pattern(None, predicate, object, graph)

    def predicates(self, subject=None, object=None, graph=None):
        return self.graph.quads_for_pattern(subject, None, object, graph)

    def objects(self, subject=None, predicate=None, graph=None):
        return self.graph.quads_for_pattern(subject, predicate, None, graph)

    def quads(self, quad):
        return self.graph.quads_for_pattern(*quad)

    def triples(self, triple=None):
        if triple == None:
            triple = (None, None, None)
        return self.quads(triple)

    def term_to_string(self, term, expand_literals=False):
        if expand_literals and type(term) == self.Literal:
            value, datatype, language = term.value, term.datatype, term.language
            if datatype == self.xsd_boolean:
                value = str(value.capitalize())
            if language:
                return f'"{value}"^^{datatype}@{language}'
            return f'"{value}"^^{datatype}'
        return str(term)

    def add(self, quad):
        return self.graph.add(self.Quad(*quad))

    def remove(self, quad):
        return self.graph.remove(self.Quad(*quad))


# _____________________________________________________________________________ #

graph_types = {
    "rdflib": RdfLibGraph,
    "oxrdflib": OxRdfLibGraph,
    "oxigraph": OxiGraph,
}

graph_classes = {
    rdflib.Graph: RdfLibGraph,
    oxrdflib.Graph: OxRdfLibGraph,
    pyoxigraph.Store: OxiGraph,
}


def get_graph(data=None, format="trig", graph_type="oxrdflib", max_path=2048):
    type_data = type(data)

    if issubclass(type_data, __Graph__):
        return data
    elif type_data in graph_classes:
        return graph_classes[type_data](data, format)
    elif graph_type in graph_types:
        return graph_types[graph_type](data, format, max_path)
    else:
        raise ValueError(
            "Argument 'graph_type' must be one of: "
            + ", ".join(graph_types.keys())
            + ". Got: "
            + str(graph_type)
        )
