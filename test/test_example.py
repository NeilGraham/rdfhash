from rdflib import Graph

from hash import rdf_hash


def test_product_example_sha256():
    ttl = """
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    @prefix c:         <def:class:> .
    @prefix currency:  <def:class:currency> .
    @prefix p:         <def:property:> .
    @prefix sha256:    <sha256:> .

    [
        rdf:type c:Product ;
        p:price [
            rdf:type    currency:USDollar ;
            p:amount    "500.00"^^xsd:decimal ;
        ] ;
    ] ;
    .
    """
    graph = rdf_hash(ttl)

    graph_compare = Graph().parse(
        data="""
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        @prefix c:         <def:class:> .
        @prefix currency:  <def:class:currency> .
        @prefix p:         <def:property:> .
        @prefix sha256:    <sha256:> .

        sha256:d780d9c620a96223fb7f20bcc948140d6af0ade6a2343e00f42ae47b0a96f3f6 
            a c:Product ;
            p:price sha256:35608b4b549ba41256ca9e89c3f7882b31dd17ab23e617a1b4f56069912e98d2 .

        sha256:35608b4b549ba41256ca9e89c3f7882b31dd17ab23e617a1b4f56069912e98d2 
            a currency:USDollar ;
            p:amount 500.00 .
        """,
        format="ttl"
    )
    
    assert graph.isomorphic(graph_compare) == True
