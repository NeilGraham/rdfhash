# rdfhash: RDF Graph Compression Tool

`rdfhash` is a utility for RDF graph compression that works by hashing RDF subjects based on a checksum of their triples, effectively minimizing the size of RDF graphs by consolidating subjects that have identical definitions.

## Installation

You can install `rdfhash` using `pip`, a package manager for Python. Ensure [`python`](https://www.python.org/downloads/) and [`pip`](https://pip.pypa.io/en/stable/installation/#installation) are properly installed on your system, then run the following command:

```bash
pip install rdfhash
```

## Usage

### Command Line Interface (CLI)

#### **Basic Usage**

By default, all blank nodes in a `text/turtle` file or string are replaced by their hashed definition:

```bash
rdfhash '
@prefix hash: <http://rdfhash.com/ontology/> .

[ ] a hash:Attribute ;
    hash:unit hash:unit:Centimeters ;
    hash:value 5.38 .'
```

Output:

```yaml
@prefix hash: <http://rdfhash.com/ontology/> .

<sha256:960891b4b1856b4d2c24b977f75d497e4da9e6f147a292524ae51db5fd0e864e> 
    a hash:Attribute ;
    hash:unit <http://rdfhash.com/ontology/unit:Centimeters> ;
    hash:value 5.38 .
```

#### **Advanced Usage**

The `rdfhash` tool is highly customizable and can be tailored to fit the requirements of any organization:

```bash
rdfhash '
@prefix hash: <http://rdfhash.com/ontology/> .
@prefix md5: <http://rdfhash.com/instances/md5/> .

[ ] a hash:Contact ;
    hash:phone "487-538-2824" ;
    hash:email "johnsmith@example.com" ;
    hash:name [ 
        a hash:LegalName ;
        hash:firstName "John" ;
        hash:lastName "Smith" ;
    ] ;
    hash:address [ 
        a hash:Address ;
        hash:street "4567 Mountain Peak Way" ;
        hash:city "Denver" ;
        hash:state "CO" ;
        hash:zip "80202" ;
        hash:country "USA" ;
    ] ;
.' \
--method md5 \
--template 'http://rdfhash.com/instances/{method}/{value}' \
--sparql '
prefix hash: <http://rdfhash.com/ontology/>
select ?s where { 
    ?s a ?type . 
    VALUES ?type {
        hash:Contact
        hash:LegalName
        hash:Address
    }
}'
```
- `--method` specifies the hashing algorithm to use. The default is `sha256`.
- `--template` specifies the URI template to use for hashed subjects. The default is `{method}:{value}`.
- `--sparql` specifies the SPARQL query to use for selecting subjects to hash. The default is `SELECT ?s WHERE { ?s ?p ?o . FILTER(isBlank(?s))}` (Selecting all Blank Node subjects).
- Run `rdfhash --help` for more information on available parameters.

Output:

```yaml
@prefix hash: <http://rdfhash.com/ontology/> .
@prefix md5: <http://rdfhash.com/instances/md5/> .

md5:8fc18e400ff531e5cbe02fef751662ba 
    a hash:Contact ;
    hash:phone "487-538-2824" ;
    hash:email "johnsmith@example.com" ;
    hash:name md5:5fd42f2c072c80e3db760c3fc69b91b8 ;
    hash:address md5:9a3e3ce644e2c5271015d9665675a8e5 .

md5:5fd42f2c072c80e3db760c3fc69b91b8 
    a hash:LegalName ;
    hash:firstName "John" ;
    hash:lastName "Smith" .

md5:9a3e3ce644e2c5271015d9665675a8e5 
    a hash:Address ;
    hash:street "4567 Mountain Peak Way" ;
    hash:city "Denver" ;
    hash:state "CO" ;
    hash:zip "80202" ;
    hash:country "USA" .
```

### Import as a Python Module

```python
from rdfhash import hash_subjects

data = '''
@prefix hash: <http://rdfhash.com/ontology/> .
@prefix sha1: <http://rdfhash.com/instances/sha1/> .

<http://rdfhash.com/instances/Meaning-of-Life>
    a hash:Attribute ;
    hash:value 42 .
'''

graph, subjects_replaced = hash_subjects(
    data,
    method='sha1',
    template='http://rdfhash.com/instances/{method}/{value}',
    sparql_select_subjects='''
    prefix hash: <http://rdfhash.com/ontology/>
    SELECT ?s WHERE { ?s a hash:Attribute. }
    '''
)

print(graph.serialize(format='turtle'))
```

Output:

```yaml
@prefix hash: <http://rdfhash.com/ontology/> .
@prefix sha1: <http://rdfhash.com/instances/sha1/> .

sha1:4afe716d630b17d5a5d06f0901800e16f3e8c9a4
    a hash:Attribute ;
    hash:value 42 .
```

## Limitations

It's important to note where `rdfhash` is limited in its functionality. These limitations are expected to be addressed in future versions.

- The `rdfhash` tool does not yet fully support Named Graphs (e.g. `text/trig` or `application/n-quads`)
  - Users can still attempt to pass RDF data containing Named Graphs, although the expected output has not yet been tested.
- Circular dependencies between selected subjects are currently not allowed. (e.g. Inverse properties). A [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph) is required at the moment.
  - Best practice to follow is prioritizing broader-to-narrower relationships. (e.g. A person `Contact` points to `LegalName` and `Address` and not inversely. Multiple contacts can point to the same `LegalName` or `Address`.)
  - Future `rdfhash` versions will support ignoring specific properties used in a subject's hash, allowing the use of inverse properties.
- Currently, selected subjects are expected to be fully defined in the input graph.
  - Future `rdfhash` versions will support connections to a SPARQL endpoint to fetch full context for hashing.
