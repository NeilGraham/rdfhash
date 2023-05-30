from rdflib import Graph, Literal, XSD, BNode
import oxrdflib


def normalize_graph(g, create_new=False):
    """
    Normalize a rdflib.Graph by converting all string literals to the xsd:string datatype.
    """
    if create_new:
        new_g = Graph(store="Oxigraph")
    else:
        new_g = g
    for s, p, o in g:
        if isinstance(o, Literal) and o.datatype is None and isinstance(o.value, str):
            o = Literal(o.value, datatype=XSD.string)
        new_g.add((s, p, o))
    return new_g


def compare_graphs(g1, g2):
    """
    Compare two graphs, normalizing strings to xsd:string before comparison.
    """
    return normalize_graph(g1).isomorphic(normalize_graph(g2))


def graph_differences(g1, g2, compare_bnodes=False):
    """
    Find and return the differences between two graphs.

    Returns a dictionary with two keys: 'in_g1_not_g2' and 'in_g2_not_g1'. Each key
    corresponds to a list of triples that are present in one graph but not the other.
    """
    normalized_g1 = normalize_graph(g1)
    normalized_g2 = normalize_graph(g2)

    def triples_without_bnodes(graph):
        """
        Generate triples from the graph, skipping those with blank nodes.
        """
        for triple in graph:
            if any(isinstance(node, BNode) for node in triple):
                if compare_bnodes:
                    raise NotImplementedError(
                        "Comparison of blank nodes is not implemented"
                    )
                else:
                    continue
            yield triple

    triples_in_g1_not_g2 = list(
        set(triples_without_bnodes(normalized_g1))
        - set(triples_without_bnodes(normalized_g2))
    )
    triples_in_g2_not_g1 = list(
        set(triples_without_bnodes(normalized_g2))
        - set(triples_without_bnodes(normalized_g1))
    )

    g1_diff = Graph(store="Oxigraph")
    g2_diff = Graph(store="Oxigraph")
    for triple in triples_in_g1_not_g2:
        g1_diff.add(triple)
    for triple in triples_in_g2_not_g1:
        g2_diff.add(triple)

    return {"in_g1_not_g2": g1_diff, "in_g2_not_g1": g2_diff}
