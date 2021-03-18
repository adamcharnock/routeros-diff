def find_expression(key, value, settings, *args):
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
            settings=settings,
        )
    else:
        return Expression(
            section_path="",
            command="find",
            find_expression=None,
            args=ArgList([Arg(key, value)]),
            settings=settings,
        )


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
