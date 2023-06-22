import difflib

from rdflib import Graph, Literal, XSD, BNode
import oxrdflib
from termcolor import colored

from rdfhash.utils.graph import get_graph, __Graph__
from rdfhash.main import hash_subjects


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

def diff_strings(a, b):
    for i, s in enumerate(difflib.ndiff(a, b)):
        if s[0] == " ":
            continue
        elif s[0] == "-":
            print(colored(f"Line {i+1}, char {s[2:].find(s[-1])+1}: {s}", "red"))
        elif s[0] == "+":
            print(colored(f"Line {i+1}, char {s[2:].find(s[-1])+1}: {s}", "green"))


def graph_diff(f1, f2):
    g1: __Graph__ = get_graph(graph_type="oxigraph")
    g1.parse_file(f1)

    g2: __Graph__ = get_graph(graph_type="oxigraph")
    g2.parse_file(f2)
    subjects1 = set(g1.subjects())
    subjects2 = set(g2.subjects())
    
    def hash_bnodes(g):
        g_hashed = get_graph(graph_type="oxigraph")

        blank_nodes_s1 = set([node for node in subjects1 if g.is_bnode(node)])
        blank_nodes_s1 += set(
            [g.subjects(None, node) for node in g.objects() if g.is_bnode(node)]
        )
        for node in blank_nodes_s1:
            g_hashed.add(g.triples((node, None, None)))
            hash_subjects(g_hashed)
        
        return g_hashed
    
    g1_bnodes = hash_bnodes(g1)
    for triple in g1_bnodes.triples():
        g1.add(triple)
    g2_bnodes = hash_bnodes(g2)
    for triple in g2_bnodes.triples():
        g2.add(triple)

    # Compare subjects
    for subject in subjects1.union(subjects2):
        if subject in subjects1 and subject in subjects2:
            # For subjects that are similar, display differences in sorted set of triples
            triples1 = sorted(list(g1.triples((subject, None, None))))
            triples2 = sorted(list(g2.triples((subject, None, None))))
            print(f"Subject: {subject}")
            diff_strings(triples1, triples2)
        elif subject in subjects1:
            # For subjects that are different, display them above and below the similar subjects diff
            triples1 = sorted(list(g1.triples((subject, None, None))))
            print(
                colored(
                    f"Subject: {subject} only in g1 with triples:\n{triples1}",
                    "red",
                )
            )
        else:
            triples2 = sorted(list(g2.triples((subject, None, None))))
            print(
                colored(
                    f"Subject: {subject} only in g2 with triples:\n{triples2}",
                    "green",
                )
            )



def graph_differences(g1, g2, compare_bnodes=False):
    """
    Find and return the differences between two graphs.

    Returns a dictionary with two keys: 'in_g1_not_g2' and 'in_g2_not_g1'. Each key
    corresponds to a list of triples that are present in one graph but not the other.
    """
    normalized_g1 = normalize_graph(g1)
    normalized_g2 = normalize_graph(g2)

    def triples_without_bnodes(graph, compare_bnodes=False):
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
            yield triple[0]

    triples_in_g1_not_g2 = list(
        set(triples_without_bnodes(normalized_g1))
        - set(triples_without_bnodes(normalized_g2))
    )
    triples_in_g2_not_g1 = list(
        set(triples_without_bnodes(normalized_g2))
        - set(triples_without_bnodes(normalized_g1))
    )

    g1_diff = {}
    g2_diff = {}
    # g1_diff = Graph(store="Oxigraph")
    # g2_diff = Graph(store="Oxigraph")
    for triple in triples_in_g1_not_g2:
        g1_diff.add(triple)
    for triple in triples_in_g2_not_g1:
        g2_diff.add(triple)

    return {"in_g1_not_g2": g1_diff, "in_g2_not_g1": g2_diff}
