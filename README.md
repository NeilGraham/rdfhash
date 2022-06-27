# RDF Hash

Command-line tool for hashing blank node triples into unique identifiers ( `sha256`, `md5`, `blake2b`, etc. ).

Predicates and objects on a blank node subject are sorted then hashed together to form a unique identifier. The blank node subject is then replaced with the hash of it's sorted triples.

## Setup

### Dependencies

- Python: [3.10](https://www.python.org/downloads/)

### Getting Started

- Install `pip` packages

    ```bash
    python3.10 -m pip install rdfhash
    ```

- Test script

    ```bash
    rdfhash --data="[ a <def:class:Person> ] ." --method=sha1
    ```

    ```bash
    <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f> a <def:class:Person> .
    ```

---

## Web-Scraper Example

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
        rdf:type currency:USDollar ;
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

### `md5` Output

```text/turtle
<md5:f5d6f1a4fe970099ea56f4ac626ad4a8>
    rdf:type c:Product ;
    p:available false ;
    p:name "Microsoft - Xbox Series X 1TB Console - Black" ;
    p:price <md5:fdd61ec7cdbc7241f0289339678dd008> ;
    p:url <https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p> .

<md5:64eee8e358fd1b6340385f4588e5536b>
    rdf:type c:Product ;
    p:available false ;
    p:name "Sony - PlayStation 5 Console" ;
    p:price <md5:fdd61ec7cdbc7241f0289339678dd008> ;
    p:url <https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p> .

<md5:fdd61ec7cdbc7241f0289339678dd008>
    rdf:type currency:USDollar ;
    p:amount 499.99 .
```

- Default hashing method is `sha256`. You can change this by passing the `--method` flag.
- Nested blank nodes are always resolved first. The hash of nested blank nodes are then used to resolve the hash of a top-level blank node.
- The nested definition for `c:Price` is referenced 2 times but defined only once.

### Simple time-entry data

```text/turtle
@prefix d:  <data:> .

d:TimeEntry__ps5__2020_11_12
    a c:TimeEntry ;
    p:date "2020-11-12"^^xsd:date ;
    p:value <md5:64eee8e358fd1b6340385f4588e5536b> .

d:TimeEntry__xbox_series_x__2020_10_12
    a c:TimeEntry ;
    p:date "2020-10-12"^^xsd:date ;
    p:value <md5:f5d6f1a4fe970099ea56f4ac626ad4a8> .

d:TimeEntry__ps5__2022_06_01
    a c:TimeEntry ;
    p:date "2022-06-01"^^xsd:date ;
    p:value <md5:64eee8e358fd1b6340385f4588e5536b> .
```

- If a webscraper encounters the exact same definition, output RDF will be identical. Only triples added are references to the existing triples.

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

- Mixing hashing methods.

    ```text/turtle
    _:error_multiple_hash_methods
        <p:0> <md5:64eee8e358fd1b6340385f4588e5536b> ;
        <p:1> <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f> .
    ```

    - Using multiple hashing methods will result in 
