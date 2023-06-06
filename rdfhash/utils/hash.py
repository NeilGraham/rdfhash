import hashlib
import uuid


hashlib_methods = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha3-224": hashlib.sha3_224,
    "sha3-256": hashlib.sha3_256,
    "sha3-384": hashlib.sha3_384,
    "sha3-512": hashlib.sha3_512,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}

uuid_methods = {
    "uuid1": uuid.uuid1,
    "uuid3": uuid.uuid3,
    "uuid4": uuid.uuid4,
}

manual_methods = {
    "uuid5": lambda v: uuid.uuid5(uuid.NAMESPACE_OID, v).hex,
    "shake-128": lambda v, length: hashlib.shake_128(v).hexdigest(length),
    "shake-256": lambda v, length: hashlib.shake_256(v).hexdigest(length),
}

# ----------------------------------------------------------------------------- #


hash_types_requiring_length = {
    "shake-128",
    "shake-256",
}

hash_types_requiring_string = {
    "uuid5",
}

hash_types_resolvable = {
    *list(hashlib_methods.keys()),
    "uuid5",
    "shake-128",
    "shake-256",
}

hash_type_functions = {
    "hashlib": lambda method, val_list: hashlib_methods[method](*val_list).hexdigest(),
    "uuid": lambda method, val_list: uuid_methods[method](*val_list).hex,
    "manual": lambda method, val_list: manual_methods[method](*val_list),
}

hash_types = {
    **{k: hash_type_functions["hashlib"] for k in hashlib_methods.keys()},
    **{k: hash_type_functions["uuid"] for k in uuid_methods.keys()},
    **{k: hash_type_functions["manual"] for k in manual_methods.keys()},
}


# ----------------------------------------------------------------------------- #


def hash_string(s, method="sha256", length=None):
    """Hash a Python string with a given

    Args:
        s (str): String to hash.
        method (str, optional): Hash method to use. Defaults to "sha256".
        length (int, optional): Length of hash result.

    Raises:
        ValueError: String is not able to be encoded to 'UTF-8'
        ValueError: Hash method specified is not in 'hash_types'

    Returns:
        str: Hexadecimal string representation of hash.
    """
    # Validate that s is encoded as UTF-8.
    try:
        if method not in hash_types_requiring_string:
            s = s.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("String must be encoded as UTF-8.")

    # Throw error if method not found in 'hash_types'
    if method not in hash_types:
        raise ValueError(f"Invalid hash method: {method}")

    # Set up method values
    method_vals = [s]
    if method in hash_types_requiring_length:
        method_vals.append(length)

    # Calculate hash
    result = hash_types[method](method, method_vals)

    # If length specified, truncate result (unless already truncated in hash method)
    if length:
        if method in hash_types_requiring_length:
            return result
        result = result[:length]

    return result
