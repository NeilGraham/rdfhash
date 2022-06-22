# RDF Hash

Command-line tool for converting blank nodes to sha256 (+ other hashing algorithm) values.

Predicates and objects of a blank node subject get hashed together to form a resolvable identifier. The blank node is then replaced with the newly generated hash.

By using this method, duplicate triples are avoided when pointing to blank nodes containing the exact same statements.

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
    <sha1:b4eba29a55992b0c2047c3b19c9018d94393641b> a <c:Person> .
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
@prefix sha256:    <sha256:> .

[
    rdf:type c:Product ;
    p:price [
        rdf:type    currency:USDollar ;
        p:amount    "500.00"^^xsd:decimal ;
    ] ;
] ;
.
```

### Resolved `sha256` Output

```text/turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

@prefix c:         <def:class:> .
@prefix currency:  <def:class:currency> .
@prefix p:         <def:property:> .
@prefix sha256:    <sha256:> .

sha256:30c839f1a34ac78df4858be36a7e2f05931cb37fda63f21400ead5ae1a2156ca
    rdf:type c:Product ;
    p:price sha256:80bdbaee649d7e8e1e075f08c14440dc17640b8745d78c0dc23e46498de28979 .

sha256:80bdbaee649d7e8e1e075f08c14440dc17640b8745d78c0dc23e46498de28979
    rdf:type currency:USDollar ;
    p:amount 500.00 .
```

- Nested blank nodes are always resolved first. The hash of nested blank nodes are then used to resolve the hash of a top-level blank node.

### Pointing to Hashed URIs

```text/turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

@prefix c:         <def:class:> .
@prefix p:         <def:property:> .
@prefix sha256:    <sha256:> .
@prefix :          <data:> .

:TimeEntry_2020-01-01
    a c:TimeEntry ;
    p:date "2020-01-01"^^xsd:date ;
    p:value sha256:30c839f1a34ac78df4858be36a7e2f05931cb37fda63f21400ead5ae1a2156ca ;
    .

:TimeEntry_2020-01-02
    a c:TimeEntry ;
    p:date "2020-01-02"^^xsd:date ;
    p:value sha256:30c839f1a34ac78df4858be36a7e2f05931cb37fda63f21400ead5ae1a2156ca ;
    .
```

- Both time entries above point to the same `c:Product` definition without duplicating any statements.

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
        a <def:class:Person> ;
        .
    ```

  - Updating statements on hashed subject:

    ```text/turtle
    # sha1 Result: c0f62a34306ecd165adb6a1af4ac1f608f94f5e6

    <sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f>
        a <def:class:Person> ;
        <def:property:age> "24"^^<http://www.w3.org/2001/XMLSchema#integer> ;
        .
    ```

    - Mismatch between original (`<sha1:2408f5f487b26247f9a82a6b9ea76f21b79bb12f>`) and actual (`<sha1:c0f62a34306ecd165adb6a1af4ac1f608f94f5e6>`)

- Cannot resolve circular dependencies between blank nodes.

    ```text/turtle
    _:b1 <property:connectedTo> _:b2 .
    _:b2 <property:connectedTo> _:b1 .
    ```
