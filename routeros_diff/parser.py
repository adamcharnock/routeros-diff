import re
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Union

import dateutil.parser

from routeros_diff.settings import Settings
from routeros_diff.exceptions import CannotDiff
from routeros_diff.sections import Section


@dataclass
class RouterOSConfig:
    """An entire RouterOS config file.

    You probably want ot use `RouterOSConfig.parse(config_string)`
    to parse your config data.
    """

    # Timestamp, as parsed from header comment (if present)
    timestamp: Optional[datetime]

    # RouterOS version, as parsed from header comment (if present)
    router_os_version: Optional[Tuple[int, int, int]]

    # All sections parsed from the config file
    sections: List[Section]

    settings: Settings = None

    def __str__(self):
        return "\n".join(str(s) for s in self.sections if s.expressions)

    def __html__(self):
        html = "<br>\n".join(s.__html__() for s in self.sections if s.expressions)
        return f'<span class="ros">{html}</span>'

    @classmethod
    def parse(cls, s: str, settings: Union[Settings, dict] = None):
        """Takes an entire RouterOS configuration blob"""
        settings = settings or Settings()
        if isinstance(settings, dict):
            settings = Settings(**settings)

        # Normalise new lines
        s = s.strip().replace("\r\n", "\n")

        # Parse out version & timestamp
        first_line: str
        first_line, *_ = s.split("\n", maxsplit=1)
        if first_line.startswith("#") and " by RouterOS " in first_line:
            first_line = first_line.strip("#").strip()
            timestamp, *_ = first_line.split(" by ")
            timestamp = dateutil.parser.parse(timestamp)
            router_os_version = re.search(r"(\d\.[\d\.]+\d)", first_line).group(1)
            router_os_version = tuple([int(x) for x in router_os_version.split(".")])
        else:
            timestamp = None
            router_os_version = None

        # Split on lines that start with a slash as these are our sections
        sections = ("\n" + s).split("\n/")
        # Add the slash back in, and skip off the first comment
        sections = ["/" + s for s in sections[1:]]

        # Note that this dict will maintain it's ordering
        parsed_sections: Dict[str, Section] = {}
        for section in sections:
            # Parse the section
            parsed_section = Section.parse(section, settings=settings)
            if parsed_section.path not in parsed_sections:
                # Not seen this section, so store it as normal
                parsed_sections[parsed_section.path] = parsed_section
            else:
                # This is a duplicate section, so append its expressions to the existing section
                parsed_sections[parsed_section.path].expressions.extend(
                    parsed_section.expressions
                )

        return cls(
            timestamp=timestamp,
            router_os_version=router_os_version,
            sections=list(parsed_sections.values()),
            settings=settings,
        )

    def keys(self):
        """Get all section paths in this config file"""
        return [section.path for section in self.sections]

    def __getitem__(self, path):
        """Get the section at the given path"""
        for section in self.sections:
            if section.path == path:
                return section
        raise KeyError(path)

    def __contains__(self, path):
        """Is the given section path in this config file?"""
        return path in self.keys()

    def get(self, path, default=None):
        """Get the section for the given section path"""
        try:
            return self[path]
        except KeyError:
            return default

    def diff(
        self, old: "RouterOSConfig", old_verbose: Optional["RouterOSConfig"] = None
    ):
        """Diff this config file with an old config file

        Will return a new config file which can be used to
        migrate from the old config to the new config.
        """
        new_sections = self.keys()
        old_sections = old.keys()
        diffed_sections = []

        # Sanity checks
        if len(new_sections) != len(set(new_sections)):
            raise CannotDiff("Duplicate section names present in new config")

        if len(old_sections) != len(set(old_sections)):
            raise CannotDiff("Duplicate section names present in old config")

        # Create a list of sections paths which are present in
        # either config file
        section_paths = copy(new_sections)
        for section_path in old_sections:
            if section_path not in new_sections:
                section_paths.append(section_path)

        # Diff each section
        for section_path in section_paths:
            if section_path in new_sections:
                new_section = self[section_path]
            else:
                # Section not found in new config, so just create a dummy empty section
                new_section = Section(
                    path=section_path, expressions=[], settings=self.settings
                )

            if section_path in old_sections:
                old_section = old[section_path]
            else:
                # Section not found in old config, so just create a dummy empty section
                old_section = Section(
                    path=section_path, expressions=[], settings=self.settings
                )

            old_section_verbose = old_verbose.get(section_path) if old_verbose else None
            diffed_sections.append(
                new_section.diff(old_section, old_verbose=old_section_verbose)
            )

        return RouterOSConfig(
            timestamp=None,
            router_os_version=None,
            sections=[s for s in diffed_sections if s.expressions],
        )
