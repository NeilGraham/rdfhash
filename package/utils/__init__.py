import re

from .hash import hash_types


def validate_uri(
    uri,
    template="{method}:{value}",
    values={"method": set(list(hash_types)), "value": r"[a-f0-9]+"},
):
    def value_re(value):
        if type(value) == set:
            return "(" + "|".join(value) + ")"
        elif type(value) == str:
            return value

    # Convert 'template' to a regular expression.
    template_re = template
    for key in values.keys():
        template_re = template_re.replace("{" + key + "}", value_re(values[key]))

    # Validate URI.
    return re.match(template_re, uri) != None
