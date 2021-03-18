from dataclasses import dataclass
from typing import Union, List, TYPE_CHECKING, Optional

from routeros_diff.settings import Settings
from routeros_diff.utilities import quote
from routeros_diff.exceptions import CannotDiff

if TYPE_CHECKING:
    from routeros_diff.expressions import Expression


@dataclass
class AbstractArgValue:
    """Represent a single value

    For example in the following expression:

        add name=core router-id=10.127.0.88

    The values are `core` and `10.127.0.88`.
    """

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

    def __html__(self):
        return str(self)


@dataclass(eq=False)
class ArgValue(AbstractArgValue):
    """Represent a single standard value

    For example in the following expression:

        add name=core router-id=10.127.0.88

    The values are `core` and `10.127.0.88`. These are just simple values, nothing special
    """

    value: str

    def quote(self) -> str:
        return quote(self.value)

    def __html__(self):
        return f'<span class="ros-v">{self.quote()}</span>'


@dataclass(eq=False)
class ExpressionArgValue(AbstractArgValue):
    """Represent an expression value

    For example in the following expression:

        add chain=b place-before=[ find where comment~ID:3 ]

    The value `[ find where comment~ID:3 ]` is an expression value.
    """

    value: "Expression"

    def quote(self) -> str:
        return f"[ {self.value} ]"

    def __html__(self):
        return f'<span class="ros-v ros-vc">{self}</span>'


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
    # Common comparators are = or ~
    comparator: str = "="

    settings: Settings = None

    def __init__(
        self,
        key: str,
        value: Union[str, "Expression", AbstractArgValue, None] = None,
        comparator: str = "=",
        settings: Settings = None,
    ):
        from routeros_diff.expressions import Expression

        self.key = key
        self.comparator = comparator
        self.settings = settings or Settings()

        # Normalise our value into some kind of AbstractArgValue
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
        """A positional argument has no corresponding value

        For example, take the expression:

            set 0 foo=bar

        Here, `0` would be a positional argument
        """
        return not self.value

    @property
    def is_key_value(self):
        """A key-value argument has both a key and a value

        For example, take the expression:

            set 0 foo=bar

        Here, `foo=bar` would be a key-value argument
        """
        return not self.is_positional

    def __html__(self, natural_key=None):
        if self.value is None:
            # Positional argument, so just render the key
            html = f'<span class="ros-a ros-pa">{self.key}</span>'
        else:
            # Standard key/value pair
            html = (
                f'<span class="ros-k">{self.key}</span>'
                f'<span class="ros-com">{self.comparator}</span>'
                f"{self.value.__html__()}"
            )

        if natural_key == "comment-id":
            natural_key = "comment"
        if natural_key and self.key == natural_key:
            html = f'<span class="ros-nat">{html}</span>'

        return html


class ArgList(list):
    """A list of several arguments"""

    def __str__(self):
        """Turn this parsed list of args back into a config string"""
        return " ".join([str(a) for a in self])

    def __html__(self, natural_key=None):
        return " ".join(
            [f'<span class="ros-a">{a.__html__(natural_key)}</span>' for a in self]
        )

    def __getitem__(self, item):
        """Key an item by index or by key"""
        if isinstance(item, str):
            # By key
            for arg in self:
                if arg.key == item:
                    return arg.value
            raise KeyError(item)
        else:
            # By index
            return super().__getitem__(item)

    def __contains__(self, key):
        """Do these args contain an argument with the given key?"""
        return key in self.keys()

    def __delitem__(self, key):
        """Delete the arg with the given key"""
        if isinstance(key, str):
            for i, arg in enumerate(self):
                if arg.key == key:
                    del self[i]
        else:
            return super().__delitem__(key)

    def get(self, key, default=None):
        """Get the arg for the given key"""
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self) -> List[str]:
        """Get a list of keys for all args"""
        return [arg.key for arg in self]

    def diff(
        self, old: "ArgList", old_verbose: Optional["ArgList"] = None
    ) -> "ArgList":
        """Diff this list with the given old list, and return a new list of args

        This may:

        * Return args which are only present in this list
        * Return args which which appear in both lists but with different values
        * Return args which do not appear in this list, in which case their values will be set to ""
        """
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
                # key is not present in the old list, so it must be new
                added.append(k)

        for k in set(old_keys).intersection(new_keys):
            # key is in both lists, but the value has changed
            if self[k] != old[k]:
                modified.append(k)

        for k in old_keys:
            if k in removed:
                # Removed keys are given a blank value
                diffed_arg_list.append(Arg(key=f"{k}", value=""))

        for k in new_keys:
            if k in added or k in modified:
                # Added keys are added with their value only if
                # their value does not match the value in the
                # old verbose output
                if old_verbose is None or self[k] != old_verbose.get(k):
                    diffed_arg_list.append(Arg(key=k, value=self[k]))

        return diffed_arg_list

    def sort(self):
        """Sort the list by key

        But still ensure positional arguments appear at the start
        """
        positional = [a for a in self if a.is_positional]
        key_value = [a for a in self if a.is_key_value]
        key_value = sorted(key_value, key=str)
        return ArgList(positional + key_value)
