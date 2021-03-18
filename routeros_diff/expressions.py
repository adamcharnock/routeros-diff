import re
import shlex
from dataclasses import dataclass, replace
from ipaddress import ip_address
from typing import Optional, List, Tuple

from routeros_diff.arguments import ArgList, Arg
from routeros_diff.settings import Settings
from routeros_diff.utilities import find_expression
from routeros_diff.exceptions import CannotDiff


@dataclass
class Expression:
    """Represents an entire expression

    Example expressions are:

        add address=1.2.3.4
        set [ find name=core ] router-id=10.127.0.99
        remove name=loopback

    """

    # Eg: "/ip/address"
    section_path: str

    # Eg: "add", "set", "remove"
    command: str

    # Used in the case where expressions identify their target using [ find key=value ].
    find_expression: Optional["Expression"]

    # The list of args in this expression
    args: ArgList

    settings: Settings = None

    def __post_init__(self):
        assert "=" not in self.command, (
            f"Not a valid command: {self.command}. "
            f"It looks like you have parsed an expression which does not start with a command."
        )

    def __str__(self):
        """Format this parsed expresion into a valid RouterOS string"""
        if self.find_expression:
            find_expression_ = f"[ {self.find_expression} ]"
        else:
            find_expression_ = ""

        return " ".join(
            [x for x in (self.command, find_expression_, str(self.args)) if x]
        )

    def __html__(self):
        if self.find_expression:
            find_expression_ = (
                f'<span class="ros-fc">[ {self.find_expression.__html__()} ]</span>'
            )
        else:
            find_expression_ = ""

        if self.command:
            command = f'<span class="ros-c">{self.command}</span>'
        else:
            command = ""

        natural_key, _ = self.natural_key_and_id

        html = " ".join(
            [
                x
                for x in (command, find_expression_, self.args.__html__(natural_key))
                if x
            ]
        )
        return f'<span class="ros-e">{html}</span>'

    @staticmethod
    def parse(s: str, section_path: str, settings: Settings = None):
        """Return an Expression object for the given string

        Example:

            Expression.parse("add area=core network=100.127.0.0/24", "/routing ospf area")
        """
        settings = settings or Settings()

        # Sanity check
        assert s.count("[") <= 1, f"Too many sub-expressions, cannot parse: {s}"

        # Regex matching for find expressions (usingn a regex isn't ideal, but it works)
        find_expression_ = re.search(r"\[\s*(find.*?)\]", s)
        if find_expression_:
            find_expression_ = find_expression_.group(1).strip()
            s = re.sub(r"\[.*?\]", "", s)
            find_expression_ = Expression.parse(
                find_expression_, section_path, settings
            )
        else:
            find_expression_ = None

        # Use python's shlex module for the smart parsing
        try:
            command, *args = shlex.split(s)
        except ValueError:
            raise ValueError(f"Error parsing line: {s}")

        # Parse the args
        args = [Arg.parse(arg) for arg in args]

        # And return our new Expression
        return Expression(
            command=command,
            find_expression=find_expression_,
            args=ArgList(args),
            section_path=section_path,
            settings=settings,
        )

    def diff(
        self, old: "Expression", old_verbose: Optional["Expression"] = None
    ) -> List["Expression"]:
        """Compare self to the given old expression

        Returns an expression which will migrate the old expression to
        be the new expression
        """
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
            old_verbose_args = old_verbose.args if old_verbose else None
            diffed_args = self.args.diff(old.args, old_verbose_args)
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
                    find_expression=None,
                    settings=self.settings,
                )
            ]
        else:
            if diffed_args and diffed_args[0].is_positional:
                # We're using a find expression here, so no need for a
                # positional arg identifying the record to modify
                diffed_args.pop(0)
            return [
                Expression(
                    section_path=self.section_path,
                    command="set",
                    args=diffed_args,
                    find_expression=find_expression(
                        new_natural_key, new_natural_id, self.settings
                    ),
                    settings=self.settings,
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

            natural_key = self.settings.get_natural_key(self.section_path)
            # ID is in args
            try:
                return natural_key, self.args[natural_key]
            except KeyError:
                pass

            # ID is in find expression
            try:
                if self.find_expression:
                    return natural_key, self.find_expression.args[natural_key]
            except KeyError:
                pass

            # ID is positional arg
            if self.args and self.args[0].is_positional:
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
        """Does this expression contain any kwargs?"""
        return any(not a.is_positional for a in self.args)

    @property
    def finds_by_default(self):
        """Does this expression select it's target by selecting default=yes / default=no"""
        return (
            self.find_expression
            and self.find_expression.args
            and self.find_expression.args[0].key == "default"
        )

    def as_delete(self):
        """Return this expression as a deletion"""
        if not self.settings.deletion_allowed(self.section_path):
            # We cannot delete this entity (eg it is a physical interface)
            return None

        natural_key, natural_id = self.natural_key_and_id
        if natural_id:
            if natural_key:
                # Find by key: "remove [ find key=value ]"
                return Expression(
                    section_path=self.section_path,
                    command="remove",
                    find_expression=find_expression(
                        natural_key, natural_id, self.settings
                    ),
                    args=ArgList(),
                    settings=self.settings,
                )
            else:
                # Find by positional name: "remove value"
                if natural_id == "default":
                    # We generally cannot remove default things
                    return None

                # Remove the expression using the natural id as a positional argument
                return Expression(
                    section_path=self.section_path,
                    command="remove",
                    find_expression=None,
                    args=ArgList([Arg(natural_id, None)]),
                    settings=self.settings,
                )

        if natural_key:
            # The natural key is a positional argument. This probably shouldn't happen
            raise NotImplementedError()

        # Delete by value
        return Expression(
            section_path=self.section_path,
            command="remove",
            find_expression=Expression(
                section_path="",
                command="find",
                find_expression=None,
                args=self.args,
                settings=self.settings,
            ),
            args=ArgList(),
            settings=self.settings,
        )

    def as_create(self):
        if not self.settings.creation_allowed(self.section_path):
            # Is probably a physical interface
            return None

        if self.is_single_object_expression or (
            self.args and self.args[0].is_positional
        ):
            # Some sections do not contain multiple entities to update.
            # For example, /system/identity
            command = "set"
        else:
            command = "add"

        return Expression(
            section_path=self.section_path,
            command=command,
            find_expression=None,
            args=self.args,
            settings=self.settings,
        )

    @property
    def is_single_object_expression(self):
        """Some sections do not contain multiple entities to update. Is this one of them?

        For example, `/system/identity`
        """
        return (
            self.command == "set"
            and self.args
            and self.args[0].is_key_value
            and not self.find_expression
        )

    def with_ordered_args(self):
        """Return a new Expression where the arguments have been deterministically ordered"""
        return replace(self, args=self.args.sort())
