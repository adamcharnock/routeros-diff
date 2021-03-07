from routeros_diff.constants import NATURAL_KEYS


def find_expression(key, value, *args):
    """Create an expression which can be used as a value for Expression.find_expression"""
    from routeros_diff.arguments import ArgList, Arg
    from routeros_diff.expressions import Expression

    if key == "comment-id":
        # Match an ID in the comment
        return Expression(
            section_path="",
            command="find",
            find_expression=None,
            args=ArgList([Arg("where", None), Arg("comment", f"ID:{value}", "~")]),
        )
    else:
        return Expression(
            section_path="",
            command="find",
            find_expression=None,
            args=ArgList([Arg(key, value)]),
        )


def get_natural_key(section_path: str) -> str:
    """Get the natural key for a given section path

    Will default to 'name' if no entry is found in NATURAL_KEYS
    """
    return NATURAL_KEYS.get(section_path, "name")


def quote(s: str):
    """Quote a value for use in a RouterOS expression"""
    if not s:
        return '""'

    assert (
        '"' not in s
    ), """Found value containing a double quote ("). We cannot quote this. Remove the char from the string"""
    specials = ["\\", " ", "$", "(", ")", "[", "]", "{", "}", ";", "=", "`", "~", "/"]

    if any(c in s for c in specials):
        return f'"{s}"'
    else:
        return s
