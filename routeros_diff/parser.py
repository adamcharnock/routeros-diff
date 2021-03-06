import re
import shlex
from copy import copy
from dataclasses import dataclass, replace
from datetime import datetime
from ipaddress import ip_address
from typing import List, Tuple, Optional, Dict, Union

import dateutil.parser


@dataclass
class AbstractArgValue:
    value: Union[str, "Expression"]

    def __eq__(self, other):
        other_value = other.value if isinstance(other, AbstractArgValue) else str(other)
        return id(self) == id(other) or self.value == other_value

    def __hash__(self):
        return hash(self.value)

    def __lt__(self, other):
        other_value = other.value if isinstance(other, AbstractArgValue) else str(other)
        return str(self.value) < other_value

    def __gt__(self, other):
        other_value = other.value if isinstance(other, AbstractArgValue) else str(other)
        return str(self.value) > other_value

    def __contains__(self, item):
        return item in self.value

    def __str__(self):
        return str(self.value)


@dataclass(eq=False)
class ArgValue(AbstractArgValue):
    value: str

    def quote(self) -> str:
        return quote(self.value)


@dataclass(eq=False)
class ExpressionArgValue(AbstractArgValue):
    value: "Expression"

    def quote(self) -> str:
        return f"[ {self.value} ]"


@dataclass(init=False)
class Arg:
    """A single key=value pair as part of a RouterOS expression

    For example:

        router-id=100.127.0.1

    In the above, router-id is the key, and 100.127.0.1 is the value.

    Positional args have a value of None. For example, in this expression:

        set core router-id=100.127.0.1

    The first argument would have a key of `core` and value of `None`.
    """

    key: str
    value: Union[ArgValue, ExpressionArgValue, None]
    comparator: str = "="

    def __init__(
        self,
        key: str,
        value: Union[str, "Expression", AbstractArgValue, None] = None,
        comparator: str = "=",
    ):
        self.key = key
        self.comparator = comparator
        if isinstance(value, str):
            self.value = ArgValue(value)
        elif isinstance(value, Expression):
            self.value = ExpressionArgValue(value)
        elif value is None:
            self.value = None
        elif isinstance(value, AbstractArgValue):
            self.value = value
        else:
            raise ValueError(f"Invalid arg value: {value}")

    def __str__(self):
        """Render this argument as a string"""
        if self.value is None:
            # Positional argument, so just render the key
            return self.key
        else:
            # Standard key/value pair
            return f"{self.key}{self.comparator}{self.value.quote()}"

    @staticmethod
    def parse(s: str):
        """Parse an argument string

        Can be either key/value, or positional
        """
        if "=" in s:
            key, value = s.split("=", maxsplit=1)
        else:
            key = s
            value = None

        assert (
            key != "["
        ), "Something went wrong, failed to detect find expression correctly"
        return Arg(key=key, value=value)

    @property
    def is_positional(self):
        return not self.value

    @property
    def is_key_value(self):
        return not self.is_positional


class ArgList(list):
    def __str__(self):
        return " ".join([str(a) for a in self])

    def __getitem__(self, item):
        if isinstance(item, str):
            for arg in self:
                if arg.key == item:
                    return arg.value
            raise KeyError(item)
        else:
            return super().__getitem__(item)

    def __contains__(self, key):
        return key in self.keys()

    def __delitem__(self, key):
        if isinstance(key, str):
            for i, arg in enumerate(self):
                if arg.key == key:
                    del self[i]
        else:
            return super().__delitem__(key)

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def keys(self) -> List[str]:
        return [arg.key for arg in self]

    def diff(self, old: "ArgList") -> "ArgList":
        added = []
        removed = []
        modified = []
        old_keys = old.keys()
        new_keys = self.keys()
        diffed_arg_list = ArgList()

        if self[0].is_positional != old[0].is_positional:
            raise CannotDiff(
                f"Diffing arguments in different formats. One has a positional starting argument "
                f"and the other does not:\n"
                f"    Old: {old}\n"
                f"    New: {self}\n"
            )

        if self[0].is_positional:
            if self[0].key != old[0].key:
                raise CannotDiff(
                    f"Diffing arguments in different formats. Initial positional arguments "
                    f"do not match, so they are explicitly trying to modify different things:\n"
                    f"    Old: {old}\n"
                    f"    New: {self}\n"
                )
            else:
                # Make sure we keep the positional arg
                diffed_arg_list.append(Arg(key=self[0].key, value=None))

        for k in old_keys:
            if k not in new_keys:
                if k == "disabled" and old[k] == "yes":
                    # disabled=yes has been removed, so let's enable it
                    diffed_arg_list.append(Arg("disabled", "no"))
                else:
                    removed.append(k)

        for k in new_keys:
            if k not in old_keys:
                added.append(k)

        for k in set(old_keys).intersection(new_keys):
            if self[k] != old[k]:
                modified.append(k)

        for k in old_keys:
            if k in removed:
                diffed_arg_list.append(Arg(key=f"{k}", value=""))
        for k in new_keys:
            if k in added or k in modified:
                diffed_arg_list.append(Arg(key=k, value=self[k]))

        return diffed_arg_list

    def sort(self):
        positional = [a for a in self if a.is_positional]
        key_value = [a for a in self if a.is_key_value]
        key_value = sorted(key_value, key=str)
        return ArgList(positional + key_value)


@dataclass
class Expression:
    section_path: str
    command: str
    find_command: Optional["Expression"]
    args: ArgList

    def __post_init__(self):
        assert "=" not in self.command, (
            f"Not a valid command: {self.command}. "
            f"It looks like you have parsed an expression which does not start with a command."
        )

    def __str__(self):
        if self.find_command:
            find_command_ = f"[ {self.find_command} ]"
        else:
            find_command_ = ""

        return " ".join([x for x in (self.command, find_command_, str(self.args)) if x])

    @staticmethod
    def parse(s: str, section_path: str):
        """Eg: add area=core network=100.127.0.0/24"""
        # Simple matching for find expressions
        assert s.count("[") <= 1, f"Too many sub commands, cannot parse: {s}"
        find_command_ = re.search(r"\[\s*(find.*?)\]", s)
        if find_command_:
            find_command_ = find_command_.group(1).strip()
            s = re.sub(r"\[.*?\]", "", s)
            find_command_ = Expression.parse(find_command_, section_path)
        else:
            find_command_ = None

        try:
            command, *args = shlex.split(s)
        except ValueError:
            raise ValueError(f"Error parsing line: {s}")

        args = [Arg.parse(arg) for arg in args]
        return Expression(
            command=command,
            find_command=find_command_,
            args=ArgList(args),
            section_path=section_path,
        )

    def diff(self, old: "Expression") -> List["Expression"]:
        new_natural_key, new_natural_id = self.natural_key_and_id
        old_natural_key, old_natural_id = old.natural_key_and_id

        error_details = f"\n" f"    Old: {old}\n" f"    New: {self}\n"

        if self.section_path != old.section_path:
            raise CannotDiff(f"Section paths do not match.{error_details}")

        if new_natural_key != old_natural_key:
            raise CannotDiff(
                f"Cannot diff expressions with mismatched natural Keys.{error_details}"
            )

        if not new_natural_id:
            raise CannotDiff(
                f"Cannot diff expressions which lack natural ID.{error_details}"
            )

        if new_natural_id != old_natural_id:
            raise CannotDiff(
                f"Cannot diff expressions with mismatched natural IDs.{error_details}"
            )

        try:
            diffed_args = self.args.diff(old.args)
        except CannotDiff:
            return [
                old.as_delete(),
                self.as_create(),
            ]

        # No need to include the natural key
        if new_natural_key and new_natural_key in diffed_args:
            del diffed_args[new_natural_key]

        if not new_natural_key:
            # Positional ID
            # Eg: set telnet address=10.0.0.0/8 disabled=no
            return [
                Expression(
                    section_path=self.section_path,
                    command="set",
                    args=diffed_args,
                    find_command=None,
                )
            ]
        else:
            return [
                Expression(
                    section_path=self.section_path,
                    command="set",
                    args=diffed_args,
                    find_command=find_command(new_natural_key, new_natural_id),
                )
            ]

    @property
    def natural_key_and_id(self) -> Tuple[Optional[str], Optional[str]]:
        """Returns (key, id)"""

        def _get():
            # ID is in comment
            if "comment" in self.args:
                # Format: "blah blah [ ID:12345 ]"
                matches = re.search(
                    r"\[\s?ID:([a-zA-Z0-9-_]+)\s?\]", self.args["comment"].value
                )
                if matches:
                    # Use the special key 'comment-id'
                    return "comment-id", matches.group(1)

            natural_key = get_natural_key(self.section_path)
            # ID is in args
            try:
                return natural_key, self.args[natural_key]
            except KeyError:
                pass

            # ID is in find expression
            try:
                if self.find_command:
                    return natural_key, self.find_command.args[natural_key]
            except KeyError:
                pass

            # ID is positional arg
            if self.args[0].is_positional:
                return None, self.args[0].key

            return None, None

        def _post_process(natural_key, natural_id):
            if self.section_path == "/ip address" and natural_key == "address":
                # Normalise addresses to contain the /32 prefix as this is required
                # from find expressions to work
                if "/" not in natural_id and ip_address(natural_id).version == 4:
                    natural_id = f"{natural_id}/32"
            return natural_key, natural_id

        return _post_process(*_get())

    @property
    def has_kw_args(self):
        return any(not a.is_positional for a in self.args)

    @property
    def finds_by_default(self):
        return self.find_command and self.find_command.args[0].key == "default"

    def as_delete(self):
        if self.section_path in NO_DELETIONS:
            return None
        natural_key, natural_id = self.natural_key_and_id
        if natural_id:
            if natural_key:
                # Find by key: "remove [ find key=value ]"
                return Expression(
                    section_path=self.section_path,
                    command="remove",
                    find_command=find_command(natural_key, natural_id),
                    args=ArgList(),
                )
            else:
                # Find by positional name: "remove value"
                if natural_id == "default":
                    # We generally cannot remove default things
                    return None
                return Expression(
                    section_path=self.section_path,
                    command="remove",
                    find_command=None,
                    args=ArgList([Arg(natural_id, None)]),
                )

        if natural_key:
            raise NotImplementedError()

        # Delete by value
        return Expression(
            section_path=self.section_path,
            command="remove",
            find_command=Expression(
                section_path="", command="find", find_command=None, args=self.args,
            ),
            args=ArgList(),
        )

    def as_create(self):
        if self.section_path == "/interface ethernet":
            return None
        return Expression(
            section_path=self.section_path,
            command="set"
            if self.is_single_object_expression or self.args[0].is_positional
            else "add",
            find_command=None,
            args=self.args,
        )

    @property
    def is_single_object_expression(self):
        return (
            self.command == "set"
            and self.args
            and self.args[0].is_key_value
            and not self.find_command
        )

    def with_ordered_args(self):
        return replace(self, args=self.args.sort())


@dataclass
class Section:
    path: str
    expressions: List[Expression]

    def __str__(self):
        s = f"{self.path}\n"
        for expression in self.expressions:
            s += f"{expression}\n"
        return s

    @staticmethod
    def parse(s: str):
        """
        Example input:

            /routing ospf network
            add area=core network=10.100.0.0/24
            add area=towers network=100.126.0.0/29
        """

        s = s.strip()
        assert s.startswith("/"), "Was not passed a section block"

        # Remove escaped new lines where a key=value pair has been split by a new line
        s = re.sub(r"= *\\\n *", "=", s)
        # Remove escaped new lines
        s = re.sub(r" *\\\n *", " ", s)
        s = s.rstrip("\\")

        lines = s.split("\n")
        # Remove blank lines and comments
        lines = [l.strip() for l in lines if l.strip() and not l.startswith("#")]

        path = lines[0]
        expressions = [Expression.parse(l, section_path=path) for l in lines[1:]]

        return Section(path=path, expressions=[e for e in expressions if e])

    @property
    def uses_natural_ids(self):
        return not any(i is None for i in self.natural_ids)

    @property
    def modifies_default_only(self):
        return self.expressions and all(i.finds_by_default for i in self.expressions)

    @property
    def has_any_default_entry(self):
        return self.expressions and any(i.finds_by_default for i in self.expressions)

    @property
    def is_single_object_section(self):
        """Such as `/system identity`"""
        return self.expressions and all(
            i.is_single_object_expression for i in self.expressions
        )

    @property
    def expression_order_is_important(self):
        # Note: Probably other cases here. Catch them as they come up
        return self.path.startswith("/ip firewall")

    def expression_index_for_natural_key(self, natural_key, natural_id):
        for i, expression in enumerate(self.expressions):
            if expression.natural_key_and_id == (natural_key, natural_id):
                return i

        raise KeyError()

    def diff(self, old: "Section") -> "Section":
        if self.path != old.path:
            raise CannotDiff(f"Section paths do not match")
        if self.is_single_object_section or old.is_single_object_section:
            diff = self._diff_single_object(old)
        elif self.modifies_default_only and old.modifies_default_only:
            diff = self._diff_default_only(old)
        elif self.modifies_default_only and not old.expressions:
            # The new one sets values on the default entry, but the entry
            # isn't mentioned in the old section (probably because it has
            # entirely default values)
            return self
        elif old.modifies_default_only:
            if not self.has_any_default_entry:
                # Old config modifies default entry, and the new config
                # makes no mention of it. We cannot delete default entries,
                # so just ignore it. We ignore it by removing it and starting
                # the diff process again
                diff = self.diff(Section(old.path, []))
            else:
                raise CannotDiff(
                    "Cannot handle section which contain a mix of default setting and non-default setting"
                )
        elif old.uses_natural_ids and self.uses_natural_ids:
            diff = self._diff_by_id(old)
        else:
            diff = self._diff_by_value(old)

        if self.expression_order_is_important and diff.expressions:
            # Order is important here, and we have changes
            if self.uses_natural_ids and old.uses_natural_ids:
                # We can ID each record, so apply the correct ordering
                sort_expressions = []
                for diff_expression in diff.expressions:
                    natural_key, natural_id = diff_expression.natural_key_and_id
                    new_expression_index = self.expression_index_for_natural_key(
                        natural_key, natural_id
                    )
                    next_expression = self.expressions[new_expression_index + 1]
                    new_expression = self.expressions[new_expression_index]

                    # Update with place-before value
                    new_expression.args.append(
                        Arg(
                            key="place-before",
                            value=find_command(*next_expression.natural_key_and_id),
                        )
                    )
            else:
                # Cannot be smart, so do a full wipe and recreate
                wipe_expression = Expression(
                    section_path=self.path,
                    command="remove",
                    find_command=Expression("", "find", None, ArgList()),
                    args=ArgList(),
                )
                diff = replace(self, expressions=[wipe_expression] + self.expressions)

        return diff

    def _diff_single_object(self, old: "Section") -> "Section":
        diffed = self._diff_by_value(old)
        single_object_expressions = []
        for expression in diffed.expressions:
            if expression.command == "remove":
                pass
            else:
                single_object_expressions.append(expression)

        return replace(diffed, expressions=single_object_expressions)

    def _diff_default_only(self, old: "Section") -> "Section":
        if len(old.expressions) > 1:
            raise CannotDiff(
                "Section can only contain one expression if using [ find default=x ]"
            )
        if len(self.expressions) > 1:
            raise CannotDiff(
                "Section can only contain one expression if using [ find default=x ]"
            )

        args_diff = self.expressions[0].args.diff(old.expressions[0].args)
        return Section(
            path=self.path,
            expressions=[replace(self.expressions[0], args=args_diff)]
            if args_diff
            else [],
        )

    def _diff_by_id(self, old: "Section") -> "Section":
        all_natural_ids = sorted(set(self.natural_ids) | set(old.natural_ids))
        new_expression: Optional[Expression]
        old_expression: Optional[Expression]

        remove = []
        modify = []
        create = []

        for natural_id in all_natural_ids:
            try:
                new_expression = self[natural_id]
            except KeyError:
                new_expression = None

            try:
                old_expression = old[natural_id]
            except KeyError:
                old_expression = None

            if old_expression and not new_expression:
                # Deletion
                remove.append(old_expression.as_delete())

            elif new_expression and not old_expression:
                # Creation
                create.append(new_expression.as_create())

            else:
                # Modify
                modify.extend(new_expression.diff(old_expression))

        # No point modifying if nothing needs changing
        modify = [e for e in modify if e.has_kw_args]

        expressions = remove + modify + create
        return Section(path=self.path, expressions=[e for e in expressions if e])

    def _diff_by_value(self, old: "Section") -> "Section":
        remove = []
        create = []

        old_expressions = {str(e.with_ordered_args()): e for e in old.expressions}
        new_expressions = {str(e.with_ordered_args()): e for e in self.expressions}

        for old_expression_str, old_expression in old_expressions.items():
            if (
                old_expression_str not in new_expressions
                and old_expression.args.get("disabled") != "yes"
            ):
                remove.append(old_expression.as_delete())

        for new_expression_str, new_expression in new_expressions.items():
            if new_expression_str not in old_expressions:
                create.append(new_expression.as_create())

        expressions = remove + create
        return Section(path=self.path, expressions=[e for e in expressions if e])

    @property
    def natural_ids(self) -> List[str]:
        return [e.natural_key_and_id[1] for e in self.expressions]

    def __getitem__(self, natural_id):
        for expression in self.expressions:
            natural_id_ = expression.natural_key_and_id[-1]
            if natural_id == natural_id_:
                return expression
        raise KeyError(natural_id)

    def with_only_removals(self):
        return replace(
            self, expressions=[e for e in self.expressions if e.command == "remove"]
        )

    def without_any_removals(self):
        return replace(
            self, expressions=[e for e in self.expressions if e.command != "remove"]
        )


@dataclass
class RouterOSConfig:
    timestamp: Optional[datetime]
    router_os_version: Optional[Tuple[int, int, int]]
    sections: List[Section]

    def __str__(self):
        return "\n".join(str(s) for s in self.sections if s.expressions)

    @staticmethod
    def parse(s: str):
        """Takes an entire routeros config dump"""
        s = s.strip().replace("\r\n", "\n")
        first_line: str
        first_line, *_ = s.split("\n", maxsplit=1)
        if first_line.startswith("#") and " by RouterOS " in first_line:
            first_line = first_line.strip("#").strip()
            timestamp, *_ = first_line.split(" by ")
            timestamp = dateutil.parser.parse(timestamp)
            router_os_version = re.search("(\d\.[\d\.]+\d)", first_line).group(1)
            router_os_version = tuple([int(x) for x in router_os_version.split(".")])
        else:
            timestamp = None
            router_os_version = None

        # Split on lines that start with a slash
        sections = ("\n" + s).split("\n/")
        # Add the slash back, and skip off the first comment
        sections = ["/" + s for s in sections[1:]]

        # Note that this dict will maintain it's ordering in modern python
        parsed_sections: Dict[str, Section] = {}
        for section in sections:
            # Parse the section
            parsed_section = Section.parse(section)
            if parsed_section.path not in parsed_sections:
                # Not seen this section, so store it as normal
                parsed_sections[parsed_section.path] = parsed_section
            else:
                # This is a duplicate section, so append its expressions to the existing section
                parsed_sections[parsed_section.path].expressions.extend(
                    parsed_section.expressions
                )

        return RouterOSConfig(
            timestamp=timestamp,
            router_os_version=router_os_version,
            sections=list(parsed_sections.values()),
        )

    def keys(self):
        return [section.path for section in self.sections]

    def __getitem__(self, path):
        for section in self.sections:
            if section.path == path:
                return section
        raise KeyError(path)

    def __contains__(self, path):
        return path in self.keys()

    def diff(self, old: "RouterOSConfig"):
        new_sections = self.keys()
        old_sections = old.keys()
        diffed_sections = []

        if len(new_sections) != len(set(new_sections)):
            raise CannotDiff("Duplicate section names present in new config")

        if len(old_sections) != len(set(old_sections)):
            raise CannotDiff("Duplicate section names present in old config")

        section_paths = copy(new_sections)
        for section_path in old_sections:
            if section_path not in new_sections:
                section_paths.append(section_path)

        for section_path in section_paths:
            if section_path in new_sections:
                new_section = self[section_path]
            else:
                new_section = Section(path=section_path, expressions=[])

            if section_path in old_sections:
                old_section = old[section_path]
            else:
                old_section = Section(path=section_path, expressions=[])

            diffed_sections.append(new_section.diff(old_section))

        return RouterOSConfig(
            timestamp=None,
            router_os_version=None,
            sections=[s for s in diffed_sections if s.expressions],
        )


def quote(s: str):
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


# Natural keys for each section name.
# 'name' will be used if none is found below
# (and only if the 'name' value is available)
NATURAL_KEYS = {
    "/interface ethernet": "default-name",
    "/ip address": "address",
    "/ipv6 address": "address",
    "/routing ospf interface": "interface",
    "/routing ospf-v3 interface": "interface",
    "/routing ospf network": "network",
    "/routing ospf-v3 network": "network",
    "/mpls ldp interface": "interface",
    "/ip dhcp-server network": "address",
}

# Don't perform deletions in these sections
NO_DELETIONS = ("/interface ethernet", "/interface wireless security-profiles")


def get_natural_key(section_path: str) -> str:
    return NATURAL_KEYS.get(section_path, "name")


def find_command(key, value, *args):
    if key == "comment-id":
        # Match an ID in the comment
        return Expression(
            section_path="",
            command="find",
            find_command=None,
            args=ArgList([Arg("where", None), Arg("comment", f"ID:{value}", "~")]),
        )
    else:
        return Expression(
            section_path="",
            command="find",
            find_command=None,
            args=ArgList([Arg(key, value)]),
        )


class CannotDiff(Exception):
    pass
