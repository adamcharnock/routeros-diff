import re
from dataclasses import dataclass, replace
from typing import List, Optional

from routeros_diff.arguments import Arg, ArgList
from routeros_diff.expressions import Expression
from routeros_diff.utilities import find_expression
from routeros_diff.exceptions import CannotDiff


@dataclass
class Section:
    """An entire configuration section, including the path and its various expressions

    For example, the following is a section with path `/ip address` and two expressions:

        /ip address
        add address=1.2.3.4
        add address=5.6.7.8

    """
    path: str
    expressions: List[Expression]

    def __str__(self):
        """Convert this parsed expression into a valid RouterOS configuration"""
        s = f"{self.path}\n"
        for expression in self.expressions:
            s += f"{expression}\n"
        return s

    @staticmethod
    def parse(s: str):
        """
        Parse an input string into a Section instance

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

        # Santity checks
        assert path.startswith('/'), f"Section path must start with a '/'. It was: {path}"
        for l in lines[1:]:
            assert not l.startswith('/'), f"Expression must not start with a '/'. It was: {path}"

        expressions = [Expression.parse(l, section_path=path) for l in lines[1:]]
        return Section(path=path, expressions=[e for e in expressions if e])

    @property
    def uses_natural_ids(self):
        """Does this section use natural IDs to identify its entities?"""
        return not any(i is None for i in self.natural_ids)

    @property
    def modifies_default_only(self):
        """Do expressions in this section only find default entities

        This normally translates as the section containing a single
        expression in the form:

            set [ default=yes ] foo=bar
        """
        return self.expressions and all(i.finds_by_default for i in self.expressions)

    @property
    def has_any_default_entry(self):
        """Does any expression in this section find based upon defaults entities"""
        return self.expressions and any(i.finds_by_default for i in self.expressions)

    @property
    def is_single_object_section(self):
        """Some sections do not contain multiple entities to update. Is this one of them?

        For example, `/system/identity`
        """
        return self.expressions and all(
            i.is_single_object_expression for i in self.expressions
        )

    @property
    def expression_order_is_important(self):
        """Is expression order important in this section?

        Note: Probably other cases here. Catch them as they come up
        """
        return self.path.startswith("/ip firewall")

    def expression_index_for_natural_key(self, natural_key, natural_id):
        """Get the position of the expression identified by the given natural key & id"""
        for i, expression in enumerate(self.expressions):
            if expression.natural_key_and_id == (natural_key, natural_id):
                return i

        raise KeyError()

    def diff(self, old: "Section") -> "Section":
        """Compare self to the given old section

        Returns a section which will migrate the old section to
        be the new section

        Note that this is a great place to start debugging
        strange diff behaviour.
        """
        if self.path != old.path:
            raise CannotDiff(f"Section paths do not match")
        if self.is_single_object_section or old.is_single_object_section:
            # Eg. /system/identity
            diff = self._diff_single_object(old)
        elif self.modifies_default_only and old.modifies_default_only:
            # Both sections only change the default record
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
            # We have natural keys * ids, so do a diff using those
            diff = self._diff_by_id(old)
        else:
            # Well we lack natural keys/ids, so just compare values and do the
            # best we can. This will result in additions/deletions, but no
            # modifications.
            diff = self._diff_by_value(old)

        # Handle ordering if we need to
        if self.expression_order_is_important and diff.expressions:
            # Order is important here, and we have changes
            if self.uses_natural_ids and old.uses_natural_ids:
                # We can ID each record, so apply the correct ordering
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
                            value=find_expression(*next_expression.natural_key_and_id),
                        )
                    )
            else:
                # Cannot be smart, so do a full wipe and recreate
                wipe_expression = Expression(
                    section_path=self.path,
                    command="remove",
                    find_expression=Expression("", "find", None, ArgList()),
                    args=ArgList(),
                )
                diff = replace(self, expressions=[wipe_expression] + self.expressions)

        return diff

    def _diff_single_object(self, old: "Section") -> "Section":
        """Diff for a single object section

        Eg. /system/identity
        """
        diffed = self._diff_by_value(old)
        single_object_expressions = []
        for expression in diffed.expressions:
            if expression.command == "remove":
                pass
            else:
                single_object_expressions.append(expression)

        return replace(diffed, expressions=single_object_expressions)

    def _diff_default_only(self, old: "Section") -> "Section":
        """Diff a section based on selection of default entity

        I.e. set [ find default=yes ] foo=bar
        """
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
        """Diff using natural keys/ids"""
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
                # Modification
                modify.extend(new_expression.diff(old_expression))

        # No point modifying if nothing needs changing
        modify = [e for e in modify if e.has_kw_args]

        # Note we remove first, as this avoids issue with value conflicts
        expressions = remove + modify + create
        return Section(path=self.path, expressions=[e for e in expressions if e])

    def _diff_by_value(self, old: "Section") -> "Section":
        """Diff based on the values of expressions

        This is the diff of last resort. It is not possible to
        detect modifications in this case. All we can do is delete
        and recreate.
        """
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
        """Get all the natural IDs for expressions in this section"""
        return [e.natural_key_and_id[1] for e in self.expressions]

    def __getitem__(self, natural_id):
        """Get an expression by its natural ID"""
        for expression in self.expressions:
            natural_id_ = expression.natural_key_and_id[-1]
            if natural_id == natural_id_:
                return expression
        raise KeyError(natural_id)

    def with_only_removals(self):
        """Return a copy of this section containing only 'remove' expressions"""
        return replace(
            self, expressions=[e for e in self.expressions if e.command == "remove"]
        )

    def without_any_removals(self):
        """Return a copy of this section containing everything except 'remove' expressions"""
        return replace(
            self, expressions=[e for e in self.expressions if e.command != "remove"]
        )