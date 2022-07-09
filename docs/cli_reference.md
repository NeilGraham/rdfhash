# CLI Reference

## Main command: `rdfhash`

Replaces selected subjects with hash of their set of triples.

```
usage: rdfhash [-h] [-d DATA] [-f {turtle,n-triples,trig,n-quads,n3,rdf}]
            [-a ACCEPT [ACCEPT ...]] [-v] [--debug]
            [-m {md5,sha1,sha224,sha256,sha384,sha512,sha3_224,sha3_256,sha3_384,sha3_512,blake2b,blake2s}]
            [--sparql SPARQL]
            {reverse} ...

Replace selected subjects with hash of their triples (`{predicate} {object}.\n` sorted + joined).

positional arguments:
{reverse}
    reverse             Reverse hashed URIs to blank nodes.

options:
-h, --help            show this help message and exit
-d DATA, --data DATA  Input RDF string or file. (.ttl, .nt, .n3)
-f {turtle,n-triples,trig,n-quads,n3,rdf}, --format {turtle,n-triples,trig,n-quads,n3,rdf}
                        Input format.
-a ACCEPT [ACCEPT ...], --accept ACCEPT [ACCEPT ...]
                        Output accept format.
-v, --verbose         Show 'info' level logs.
--debug               Show 'debug' level logs.
-m {md5,sha1,sha224,sha256,sha384,sha512,sha3_224,sha3_256,sha3_384,sha3_512,blake2b,blake2s}, --method {md5,sha1,sha224,sha256,sha384,sha512,sha3_224,sha3_256,sha3_384,sha3_512,blake2b,blake2s}
                        Hash method.
--sparql SPARQL, --sparql-select-subjects SPARQL
                        SPARQL SELECT query returning subject URIs to replace
                        with hash of their triples. Defaults to all blank node
                        subjects.
```

### Example

```bash
rdfhash --data='[ a <def:class:Person> ] .' --method=md5
```

```
<sha256:377fc5177baae84d1d11c06f822a4f5db1a8ddf3219f3244c170fb2c5b64fc72> a <def:class:Person> .
```

---

## Subcommand: `reverse`

Reverses hashed URIs to blank nodes.

```
usage: rdfhash reverse [-h] [-d DATA] [-f {turtle,n-triples,trig,n-quads,n3,rdf}]
                       [-a ACCEPT [ACCEPT ...]] [-v] [--debug]

options:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  Input RDF string or file. (.ttl, .nt, .n3)
  -f {turtle,n-triples,trig,n-quads,n3,rdf}, --format {turtle,n-triples,trig,n-quads,n3,rdf}
                        Input format.
  -a ACCEPT [ACCEPT ...], --accept ACCEPT [ACCEPT ...]
                        Output accept format.
  -v, --verbose         Show 'info' level logs.
  --debug               Show 'debug' level logs.
```

### Example
  
```bash
rdfhash reverse --data='<md5:c839244d05b75ca2e36826d5dcc1969d> a <def:class:Person> .'
```

```
[] a <def:class:Person> .
```
