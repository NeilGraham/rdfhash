# RDF Hash

Command-line tool for converting blank nodes to sha256 values (+ other hashing algorithms).

Predicates and objects of a blank node subject get hashed together to form a resolvable identifier. The blank node is then replaced with the hash of it's sorted triples.

SPARQL query used to query for blank node subjects can be changed to select any subject to hash.

## Setup

### Dependencies

- Python: [3.10](https://www.python.org/downloads/)

### Getting Started

- Install `pip` packages

    ```bash
    python3.10 -m pip install -r requirements.txt
    ```

- Test script

    ```bash
    cd rdf-hash
    rdfhash --data="[ a <def:class:Person> ] ." --method=sha1
    ```

    ```bash
    <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f> a <def:class:Person> .
    ```

---

## Example

### Blank Node Input

```text/turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

@prefix c:         <def:class:> .
@prefix currency:  <def:class:currency> .
@prefix p:         <def:property:> .

_:xbox_series_x
    rdf:type c:Product ;
    p:name "Microsoft - Xbox Series X 1TB Console - Black" ;
    p:url <https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p> ;
    p:available false ;
    p:price [
        rdf:type <def:class:currency:USDollar> ;
        p:amount "499.99"^^xsd:decimal ;
    ] .

_:ps5
    rdf:type c:Product ;
    p:name "Sony - PlayStation 5 Console" ;
    p:url <https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p> ;
    p:available false ;
    p:price [
        rdf:type currency:USDollar ;
        p:amount "499.99"^^xsd:decimal ;
    ] .
```

### Resolved `sha256` Output

```text/turtle
@prefix c: <def:class:> .
@prefix currency: <def:class:currency> .
@prefix d: <data:> .
@prefix p: <def:property:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<sha256:128054dcfddf6b42608cd5303a2360b7ee685c684d2e42c259798bf69827a5a4> a <def:class:currency:USDollar> ;
    p:amount 499.99 .

<sha256:a0c79d7c20e8aef506d6aa8129bd7c25f05600afd5f3715ce0b7ed5f1e5d8b45> a c:Product ;
    p:available false ;
    p:name "Microsoft - Xbox Series X 1TB Console - Black" ;
    p:price <sha256:128054dcfddf6b42608cd5303a2360b7ee685c684d2e42c259798bf69827a5a4> ;
    p:url <https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p> .

<sha256:fcc539213e619877dc193f76f86c6fb4826f78210de348d97cdf2eefb4031dd7> a currency:USDollar ;
    p:amount 499.99 .

<sha256:20a273b984eadd9667b9955e2797ef38da1e06852a8caaa93672b26fb3ac4100> a c:Product ;
    p:available false ;
    p:name "Sony - PlayStation 5 Console" ;
    p:price <sha256:fcc539213e619877dc193f76f86c6fb4826f78210de348d97cdf2eefb4031dd7> ;
    p:url <https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p> .
```

- Nested blank nodes are always resolved first. The hash of nested blank nodes are then used to resolve the hash of a top-level blank node.
- The nested definition for `c:Price` is referenced 2 times but defined only once.

---

## Use Cases

- High frequency web-scraping.

    ```text/turtle
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    @prefix c:         <def:class:> .
    @prefix currency:  <def:class:currency> .
    @prefix p:         <def:property:> .

    @prefix d: <data:> .

    d:TimeEntry_2020-11-12 a c:TimeEntry ;
        p:date "2020-11-12"^^xsd:date,
            "2020-11-12"^^xsd:date ;
        p:value <sha256:20a273b984eadd9667b9955e2797ef38da1e06852a8caaa93672b26fb3ac4100>,
            <sha256:a0c79d7c20e8aef506d6aa8129bd7c25f05600afd5f3715ce0b7ed5f1e5d8b45> .

    d:TimeEntry_2022-06-01 a c:TimeEntry ;
        p:date "2022-06-01"^^xsd:date ;
        p:value <sha256:20a273b984eadd9667b9955e2797ef38da1e06852a8caaa93672b26fb3ac4100> .
    ```

  - If a product page doesn't change over time, you can reference already defined triples.

---

## Limitations

- Named graphs are currently not supported.
- All blank node statements are expected to be static (all or nothing). Updating statements on a hashed subject will result in a hash mismatch.
  - Blank node statement:

    ```text/turtle
    [ a <def:class:Person> ] .
    ```

  - Hashed subject:

    ```text/turtle
    <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f> 
        a <def:class:Person> .
    ```

  - Updating statements on hashed subject:

    ```text/turtle
    # sha1 Result: c0f62a34306ecd165adb6a1af4ac1f608f94f5e6

    <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f>
        a <def:class:Person> ;
        <def:property:age> "24"^^<http://www.w3.org/2001/XMLSchema#integer> .
    ```

    - Mismatch between original (`<sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f>`) and actual (`<sha1:c0f62a34306ecd165adb6a1af4ac1f608f94f5e6>`)

- Cannot resolve circular dependencies between blank nodes.

    ```text/turtle
    _:b1 <def:property:connectedTo> _:b2 .
    _:b2 <def:property:connectedTo> _:b1 .
    ```

- Blank nodes cannot be in the predicate position.

    ```text/turtle
    <s:0> _:b1 <o:0> .
    ```
