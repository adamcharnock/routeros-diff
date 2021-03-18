from fnmatch import fnmatch
from typing import Dict, List


class Settings:
    """Parser settings

    You can customise settings in one of two ways.

    The simplest way is to pass settings to RouterOSConfig.parse():

        RouterOSConfig.parse(s=my_config, settings=dict(
            natural_keys={
                "/ip address": "address",
                ...
            },
            no_deletions={
                "/interface ethernet",
                ...
            },
            no_creations={
                "/interface ethernet",
                ...
            },
            expression_order_important={
                "/ip firewall*",
                ...
            },
        ))

    Note that section paths can be specified using '*' wildcards.
    For example, `/ip firewall*`.

    Alternatively, you can extend this class and override its methods.
    This allows you to implement more complex logic should you require.
    In this case, you can pass your customised class to the parser as follows:

        RouterOSConfig.parse(my_config, settings=MyCustomSettings())
    """

    # Natural keys for each section name.
    # 'name' will be used if none is found below
    # (and only if the 'name' value is available)
    natural_keys = {
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
    no_deletions = {"/interface ethernet", "/interface wireless security-profiles"}

    # Don't perform creations in these sections
    no_creations = {
        "/interface ethernet",
    }

    # Ordering is important in these sections. Ensure
    # entities maintain their order. Natural keys/ids must be
    # present in sections listed here
    expression_order_important = {
        "/ip firewall calea",
        "/ip firewall filter",
        "/ip firewall mangle",
        "/ip firewall nat",
    }

    def __init__(
        self,
        natural_keys: Dict[str, str] = None,
        no_deletions: List[str] = None,
        no_creations: List[str] = None,
    ):
        if natural_keys is not None:
            self.natural_keys = natural_keys

        if no_deletions is not None:
            self.no_deletions = no_deletions

        if no_creations is not None:
            self.no_creations = no_creations

    def get_natural_key(self, section_path: str):
        """Get the natural key for a given section path

        Will default to 'name' if no entry is found in NATURAL_KEYS
        """
        return self.natural_keys.get(section_path, "name")

    def deletion_allowed(self, section_path: str):
        foo = [fnmatch(section_path, pattern) for pattern in self.no_deletions]
        return not any(fnmatch(section_path, pattern) for pattern in self.no_deletions)

    def creation_allowed(self, section_path: str):
        return not any(fnmatch(section_path, pattern) for pattern in self.no_creations)

    def is_expression_order_important(self, section_path: str):
        return any(
            fnmatch(section_path, pattern)
            for pattern in self.expression_order_important
        )
