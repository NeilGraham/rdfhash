import hashlib

hashlib_methods = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha3_224": hashlib.sha3_224,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_384,
    "sha3_512": hashlib.sha3_512,
    # "shake_128": hashlib.shake_128,
    # "shake_256": hashlib.shake_256,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}


def hash_string(s, method="sha256", hashlib_options={}):
    """Hash a Python string with a given

    Args:
        s (str): _description_
        method (str, optional): _description_. Defaults to "sha256".

    Raises:
        ValueError: _description_

    Returns:
        str: Hexadecimal string representation of hash.
    """
    if method in hashlib_methods:
        return hashlib_methods[method](s.encode("utf-8"), **hashlib_options).hexdigest()
    else:
        raise ValueError(f"Invalid hashing method: {method}")
