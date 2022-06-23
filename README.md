# RDF Hash

Command-line tool for converting blank nodes to sha256 values (+ other hashing algorithms).

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
@prefix sha256:    <sha256:> .

[
    rdf:type c:Product ;
    p:price [
        rdf:type    currency:USDollar ;
        p:amount    "500.00"^^xsd:decimal ;
    ] ;
] .
```

### Resolved `sha256` Output

```text/turtle
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
    p:value sha256:d780d9c620a96223fb7f20bcc948140d6af0ade6a2343e00f42ae47b0a96f3f6 ;
    .

:TimeEntry_2020-01-02
    a c:TimeEntry ;
    p:date "2020-01-02"^^xsd:date ;
    p:value sha256:d780d9c620a96223fb7f20bcc948140d6af0ade6a2343e00f42ae47b0a96f3f6 ;
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
    _:b1 <def:property:connectedTo> _:b2 .
    _:b2 <def:property:connectedTo> _:b1 .
    ```

- Blank nodes cannot be in the predicate position.

    ```text/turtle
    <s:0> _:b1 <o:0> .
    ```
