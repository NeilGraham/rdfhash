# RDF Hash

Command-line tool for hashing RDF definitions into resolvable identifiers ( `sha256`, `md5`, `blake2b`, etc. ).

Selected subjects (Default: blank node subjects) are replaced with hash of their triples.

Set of triples on a given subject are sorted by `{predicate} {object}.\n`, then hashed together. The hash result replaces the subject URI (Ex: `<md5:fdd61ec7cdbc7241f0289339678dd008>`).

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
    <sha1:f0392681a6a701d9672925133bf1207f4be9e412> a <def:class:Person> .
    ```

### Command-Line Interface

```
rdfhash [-h] -d DATA [-f {turtle,n-triples,trig,n-quads,n3,rdf}]
        [-m {md5,sha1,sha224,sha256,sha384,sha512,sha3_224,sha3_256,sha3_384,sha3_512,blake2b,blake2s}]
        [-a ACCEPT [ACCEPT ...]] [-v] [--debug] [--sparql SPARQL]

Replace selected subjects with hash of their triples (`{predicate} {object}.\n` sorted + joined).

options:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  Input data. (RDF)
  -f {turtle,n-triples,trig,n-quads,n3,rdf}, --format {turtle,n-triples,trig,n-quads,n3,rdf}
                        Input format.
  -m {md5,sha1,sha224,sha256,sha384,sha512,sha3_224,sha3_256,sha3_384,sha3_512,blake2b,blake2s}, --method {md5,sha1,sha224,sha256,sha384,sha512,sha3_224,sha3_256,sha3_384,sha3_512,blake2b,blake2s}
                        Hash method.
  -a ACCEPT [ACCEPT ...], --accept ACCEPT [ACCEPT ...]
                        Accept format.
  -v, --verbose         Show 'info' level logs.
  --debug               Show 'debug' level logs.
  --sparql SPARQL, --sparql-select-subjects SPARQL
                        SPARQL SELECT query returning subject URIs to replace with hash of their triples. Defaults to all
                        blank node subjects.
```

---

## Example

Test the tool out on the directory `./examples`.

    ```bash
    rdfhash --data ./examples/product_0.ttl
    ```

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
<md5:e2edf345944d2d2360ca0af3a2e263e5>
    a c:Product ;
    p:available false ;
    p:name "Microsoft - Xbox Series X 1TB Console - Black" ;
    p:price <md5:230919236fbe71a692d10c9a693fdd2b> ;
    p:url <https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p> .

<md5:64c8f3c04879effcad67df5e62c00245>
    a c:Product ;
    p:available false ;
    p:name "Sony - PlayStation 5 Console" ;
    p:price <md5:230919236fbe71a692d10c9a693fdd2b> ;
    p:url <https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p> .

<md5:230919236fbe71a692d10c9a693fdd2b>
    a currency:USDollar ;
    p:amount 499.99 .
```

- The nested definition for `499.99` USD is referenced 2 times and defined only once.

### Simple time-entry data

```text/turtle
@prefix d:  <data:> .

d:TimeEntry__ps5__2020_11_12
    a c:TimeEntry ;
    p:date "2020-11-12"^^xsd:date ;
    p:value <md5:64c8f3c04879effcad67df5e62c00245> .

d:TimeEntry__xbox_series_x__2020_10_12
    a c:TimeEntry ;
    p:date "2020-10-12"^^xsd:date ;
    p:value <md5:e2edf345944d2d2360ca0af3a2e263e5> .

d:TimeEntry__ps5__2022_06_01
    a c:TimeEntry ;
    p:date "2022-06-01"^^xsd:date ;
    p:value <md5:64c8f3c04879effcad67df5e62c00245> .
```

- If a webscraper encounters the exact same definition, output RDF will be identical. Only triples added are references to the existing triples.

---

## Limitations

- Named graphs are currently not supported.
- Cannot update triples on hashed subjects.
  - Updating statements on a hashed subject will result in a hash mismatch.
  - Blank node statement input:

    ```text/turtle
    [ a <def:class:Person> ] .
    ```

  - Hashed subject output:

    ```text/turtle
    <sha1:f0392681a6a701d9672925133bf1207f4be9e412>
        a <def:class:Person> .
    ```

  - Updating statements on hashed subject:

    ```text/turtle
    # Actual sha1 Result: 0c0140462cb569cb700fe5d01bf5efb3185cdb4d

    <sha1:f0392681a6a701d9672925133bf1207f4be9e412>
        a <def:class:Person> ;
        <def:property:age> "24"^^<http://www.w3.org/2001/XMLSchema#integer> .
    ```

    - Mismatch between original hash and actual hash result.
      - Original: `<sha1:f0392681a6a701d9672925133bf1207f4be9e412>`
      - Actual: `<sha1:0c0140462cb569cb700fe5d01bf5efb3185cdb4d>`

- Cannot resolve circular dependencies between selected subjects.

    ```text/turtle
    _:b1 <def:property:connectedTo> _:b2 .
    _:b2 <def:property:connectedTo> _:b1 .
    ```

- Using multiple hashing methods is not recommended.

    ```text/turtle
    _:error_multiple_hash_methods
        <p:0> <md5:64eee8e358fd1b6340385f4588e5536b> ;
        <p:1> <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f> .
    ```

    - Using multiple hashing methods can result in duplicate hashed statements. 
    - Sticking with 1 hashing method allows for the smallest possible graph size.
