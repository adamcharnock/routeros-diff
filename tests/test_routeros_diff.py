from datetime import datetime
from pathlib import Path

import pytest

import routeros_diff.exceptions
import routeros_diff.expressions
import routeros_diff.sections
import routeros_diff.utilities
from routeros_diff import parser


# fmt: off


def test_section():
    section = routeros_diff.sections.Section.parse(OSPF_SECTION)
    assert section.path == "/routing ospf network"

    expression1 = section.expressions[0]
    assert expression1.command == "add"
    assert expression1.args["area"] == "core"
    assert expression1.args["network"] == "10.100.0.0/24"

    assert expression1.args[0].key == "area"
    assert expression1.args[0].value == "core"


def test_simple_config():
    config = parser.RouterOSConfig.parse(
        "/example path \n" 
        "add foo=bar moo=cow"
    )
    exp = config.sections[0].expressions[0]
    assert str(exp) == "add foo=bar moo=cow"
    assert exp.section_path == "/example path"


def test_config():
    config = parser.RouterOSConfig.parse(ENTIRE_CONFIG)
    assert config.timestamp == datetime(2021, 2, 21, 20, 53, 34)
    assert config.router_os_version == (6, 46, 8)
    assert len(config.sections) == 17


def test_line_continuation_simple():
    config = parser.RouterOSConfig.parse(
        "/foo\n" 
        "add foo=bar \\\n" 
        "    moo=cow\n"
    )
    assert str(config.sections[0].expressions[0]) == "add foo=bar moo=cow"


def test_line_continuation_within_key_value_pair():
    config = parser.RouterOSConfig.parse(
        "/foo\n" 
        "add foo=\\\n" 
        "    bar moo=cow\n"
    )
    assert str(config.sections[0].expressions[0]) == "add foo=bar moo=cow"


def test_line_continuation_on_blank_line():
    config = parser.RouterOSConfig.parse(
        "/foo\n" 
        "    \\\n"
        "    add foo=a"
    )
    assert len(config.sections) == 1
    assert str(config.sections[0]) == "/foo\nadd foo=a\n"


def test_line_continuation_before_blank_line():
    config = parser.RouterOSConfig.parse(
        "/foo\n" 
        "add foo=a\\\n\n"
    )
    assert len(config.sections) == 1
    assert str(config.sections[0]) == "/foo\nadd foo=a\n"


def test_line_continuation_after_quotes():
    config = parser.RouterOSConfig.parse(
        "/foo\n" 
        'add foo=Test\\\nmoo=Test\n\n'
    )
    assert len(config.sections) == 1
    assert str(config.sections[0]) == '/foo\nadd foo=Test moo=Test\n'


def test_line_break_in_string_normal():
    config = parser.RouterOSConfig.parse(
        '/ip route\n'
        'add action=src-nat chain=cgnat-100.65.1.0/30 comment="Customer Zoho on plan FA\\\n'
        '    ST [ ID:e509e0a2-73f9-4fb8-94d3-7a640dd033a7-tcp ]"'
    )
    assert len(config.sections) == 1
    assert "Customer Zoho on plan FAST [ ID:" in str(config.sections[0])


def test_line_break_in_string_normal_before_space_char():
    config = parser.RouterOSConfig.parse(
        '/ip route\n'
        'add comment="Fallback static route for ensuring access to management network [\\\n'
        '    \\_ID:mgmt ]" distance=200 dst-address=10.0.0.0/8 gateway=10.100.0.250'
    )
    assert len(config.sections) == 1
    assert "[ ID:mgmt ]" in str(config.sections[0])


def test_find():
    find = "set [ find default-name=ether3 ] name=ether3-bp-backup"
    expression = routeros_diff.expressions.Expression.parse(find, "/interface ethernet")

    assert expression.command == "set"
    assert expression.find_expression.command == "find"
    assert expression.find_expression.find_expression == None
    assert expression.find_expression.args["default-name"] == "ether3"
    assert expression.args["name"] == "ether3-bp-backup"


def test_positional():
    find = "set 0 foo=bar"
    expression = routeros_diff.expressions.Expression.parse(find, "/interface ethernet")
    assert str(expression) == "set 0 foo=bar"



def test_diff_expression_modified():
    old = routeros_diff.expressions.Expression.parse(
        "add name=core router-id=10.127.0.1",
        "/routing ospf instance",
    )
    new = routeros_diff.expressions.Expression.parse(
        "add name=core router-id=10.127.0.99",
        "/routing ospf instance",
    )
    assert str(new.diff(old)[0]) == "set [ find name=core ] router-id=10.127.0.99"


def test_diff_expression_deleted():
    old = routeros_diff.expressions.Expression.parse(
        "add name=core router-id=10.127.0.1",
        "/routing ospf instance",
    )
    new = routeros_diff.expressions.Expression.parse("add name=core",
                                      "/routing ospf instance", )
    assert str(new.diff(old)[0]) == 'set [ find name=core ] router-id=""'


def test_diff_expression_added():
    old = routeros_diff.expressions.Expression.parse(
        "add name=core",
        "/routing ospf instance",
    )
    new = routeros_diff.expressions.Expression.parse(
        "add name=core router-id=10.127.0.1",
        "/routing ospf instance",
    )
    assert str(new.diff(old)[0]) == "set [ find name=core ] router-id=10.127.0.1"


def test_set_without_find():
    """Such as when modifying an IP service"""
    old = routeros_diff.expressions.Expression.parse(
        "set telnet address=10.0.0.0/8 disabled=yes",
        "/foo"
    )
    new = routeros_diff.expressions.Expression.parse(
        "set telnet address=10.0.0.0/8 disabled=no",
        "/foo"
    )
    assert str(new.diff(old)[0]) == "set telnet disabled=no"


def test_diff_expression_source_uses_find_ok():
    old = routeros_diff.expressions.Expression.parse(
        "set [ find name=core ] router-id=10.127.0.1",
        "/routing ospf instance",
    )
    new = routeros_diff.expressions.Expression.parse(
        "add name=core router-id=10.127.0.88",
        "/routing ospf instance",
    )
    assert str(new.diff(old)[0]) == "set [ find name=core ] router-id=10.127.0.88"


def test_diff_expression_both_use_find():
    old = routeros_diff.expressions.Expression.parse(
        "set [ find name=core ] router-id=10.127.0.1",
        "/routing ospf instance",
    )
    new = routeros_diff.expressions.Expression.parse(
        "set [ find name=core ] router-id=10.127.0.99",
        "/routing ospf instance",
    )
    assert str(new.diff(old)[0]) == "set [ find name=core ] router-id=10.127.0.99"


def test_diff_expression_source_uses_find_different_names():
    old = routeros_diff.expressions.Expression.parse(
        "set [ find name=core_foo ] router-id=10.127.0.1",
        "/routing ospf instance",
    )
    new = routeros_diff.expressions.Expression.parse(
        "add name=core router-id=10.127.0.88",
        "/routing ospf instance",
    )
    with pytest.raises(routeros_diff.exceptions.CannotDiff) as cm:
        str(new.diff(old)[0])
    assert "mismatched natural IDs" in str(cm.value)


def test_diff_section_modify_with_natural_key():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "add name=core router-id=10.127.0.1\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "add name=core router-id=10.127.0.99\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set [ find name=core ] router-id=10.127.0.99"


def test_diff_section_create_with_natural_key():
    old = routeros_diff.sections.Section.parse("/routing ospf instance\n")
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "add name=core router-id=10.127.0.1\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "add name=core router-id=10.127.0.1"


def test_diff_section_delete_with_natural_key():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "add name=core router-id=10.127.0.1\n"
    )
    new = routeros_diff.sections.Section.parse("/routing ospf instance\n")

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "remove [ find name=core ]"


def test_diff_section_modify_with_default_yes():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "set [ find default=yes ] router-id=10.127.1.1 name=old foo=bar\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        'set [ find default=yes ] router-id=10.127.1.2 name=new\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == 'set [ find default=yes ] foo="" router-id=10.127.1.2 name=new'


def test_diff_section_modify_with_default_yes2():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "set [ find default=yes ] disabled=yes redistribute-static=as-type-1\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        'set [ find default=yes ] name=default router-id=10.127.0.250 redistribute-static=as-type-1\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == 'set [ find default=yes ] disabled=no name=default router-id=10.127.0.250'


def test_diff_section_modify_with_default_yes3():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf area\n" 
        'set [ find default=yes ] disabled=yes\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf area\n" 
        "add area-id=1.1.1.1 name=core\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == 'add area-id=1.1.1.1 name=core'


def test_diff_section_delete_with_default_yes():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "set [ find default=yes ] router-id=10.127.1.1 name=old foo=bar\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
    )
    diffed = new.diff(old)
    assert len(diffed.expressions) == 0


def test_diff_section_not_in_old_with_default_yes():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        "set [ find default=yes ] router-id=10.127.1.1 name=old foo=bar\n"
    )
    diffed = new.diff(old)
    assert str(diffed.expressions[0]) == 'set [ find default=yes ] router-id=10.127.1.1 name=old foo=bar'


def test_diff_section_modify_with_comment_natural_key():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        'add comment="Just a comment [ID:123]" router-id=10.127.0.1\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        'add comment="Just a comment [ID:123]" router-id=10.127.0.99\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == 'set [ find where comment~"ID:123" ] router-id=10.127.0.99'


def test_diff_section_modify_with_comment_no_key():
    # There is a comment with no key in it
    old = routeros_diff.sections.Section.parse(
        "/foo\n" 
        'add comment="Just a comment" router-id=10.127.0.99\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/foo\n" 
        'add comment="Just a comment" router-id=10.127.0.99\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 0


def test_diff_section_modify_with_new_comment_natural_key():
    """Sadly we just have to delete and recreate here.

    Auto-transitioning from using 'name' to using a comment-based ID
    is just too tricky right now.
    """
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        'add name="foo" router-id=10.127.0.1\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        'add name="foo" comment="Just a comment [ID:123]" router-id=10.127.0.99\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'remove [ find name=foo ]'
    assert str(diffed.expressions[1]) == 'add name=foo comment="Just a comment [ID:123]" router-id=10.127.0.99'


def test_diff_section_modify_with_old_comment_natural_key():
    """Sadly we just have to delete and recreate here.

    Auto-transitioning from using a comment-based ID to using 'name'
    is just too tricky right now.
    """
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        'add name="foo" comment="Just a comment [ID:123]" router-id=10.127.0.1\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        'add name="foo" router-id=10.127.0.99\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'remove [ find where comment~"ID:123" ]'
    assert str(diffed.expressions[1]) == 'add name=foo router-id=10.127.0.99'


def test_diff_section_modify_with_positional_id():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "set core router-id=10.127.0.1\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "set core router-id=10.127.0.99\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set core router-id=10.127.0.99"


def test_diff_section_add_with_positional_id():
    old = routeros_diff.sections.Section.parse("/routing ospf instance")
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        "set core router-id=10.127.0.99\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set core router-id=10.127.0.99"


def test_diff_section_delete_with_positional_id():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n" 
        "set core router-id=10.127.0.1\n"
    )
    new = routeros_diff.sections.Section.parse("/routing ospf instance")

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "remove core"


def test_diff_section_multiple():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        "add name=deleted router-id=10.127.0.1\n"
        "add name=modified router-id=10.127.0.10\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf instance\n"
        "add name=modified router-id=10.127.0.20\n"
        "add name=added router-id=10.127.0.30\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 3
    assert str(diffed.expressions[0]) == "remove [ find name=deleted ]"
    assert str(diffed.expressions[1]) == "set [ find name=modified ] router-id=10.127.0.20"
    assert str(diffed.expressions[2]) == "add name=added router-id=10.127.0.30"


def test_diff_section_no_ids_modify():
    old = routeros_diff.sections.Section.parse(
        "/ip blah\n" 
        "add address=10.100.0.1/24 interface=ether1-core\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/ip blah\n" 
        "add address=10.120.0.1/24 interface=ether1-core\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'remove [ find address="10.100.0.1/24" interface=ether1-core ]'
    assert str(diffed.expressions[1]) == 'add address="10.120.0.1/24" interface=ether1-core'


def test_diff_section_order_important():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        "add foo=bar moo=cow\n"
        "add foo=a moo=b\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        "add foo=bar moo=cow\n"
        "add foo=a moo=new-value\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 3
    assert str(diffed.expressions[0]) == "remove [ find ]"
    assert str(diffed.expressions[1]) == "add foo=bar moo=cow"
    assert str(diffed.expressions[2]) == "add foo=a moo=new-value"


def test_diff_section_order_important_with_ids_modify_same_order():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add foo=bar moo=sheep comment="[ ID:1 ]"\n'
        'add foo=a moo=b comment="[ ID:2 ]"\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add foo=bar moo=cow comment="[ ID:1 ]"\n'
        'add foo=a moo=new-value comment="[ ID:2 ]"\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'set [ find where comment~"ID:1" ] moo=cow'
    assert str(diffed.expressions[1]) == 'set [ find where comment~"ID:2" ] moo=new-value'


def test_diff_section_order_important_with_ids_insert_at_start():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add value=x comment="[ ID:x ]"\n'
        'add value=y comment="[ ID:y ]"\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add value=a comment="[ ID:a ]"\n'
        'add value=b comment="[ ID:b ]"\n'
        'add value=x comment="[ ID:x ]"\n'
        'add value=y comment="[ ID:y ]"\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'add value=a comment="[ ID:a ]" place-before=[ find where comment~"ID:x" ]'
    assert str(diffed.expressions[1]) == 'add value=b comment="[ ID:b ]" place-before=[ find where comment~"ID:x" ]'


def test_diff_section_order_important_with_ids_insert_at_end():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add value=x comment="[ ID:x ]"\n'
        'add value=y comment="[ ID:y ]"\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add value=x comment="[ ID:x ]"\n'
        'add value=y comment="[ ID:y ]"\n'
        'add value=a comment="[ ID:a ]"\n'
        'add value=b comment="[ ID:b ]"\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'add value=a comment="[ ID:a ]"'
    assert str(diffed.expressions[1]) == 'add value=b comment="[ ID:b ]"'


def test_diff_section_order_important_with_ids_insert_at_middle():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add value=x comment="[ ID:x ]"\n'
        'add value=y comment="[ ID:y ]"\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add value=x comment="[ ID:x ]"\n'
        'add value=a comment="[ ID:a ]"\n'
        'add value=b comment="[ ID:b ]"\n'
        'add value=y comment="[ ID:y ]"\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'add value=a comment="[ ID:a ]" place-before=[ find where comment~"ID:y" ]'
    assert str(diffed.expressions[1]) == 'add value=b comment="[ ID:b ]" place-before=[ find where comment~"ID:y" ]'

def test_diff_section_order_important_with_ids_add_to_empty_section():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add moo=sheep comment="[ ID:2 ]"\n'
        'add moo=duck comment="[ ID:3 ]"\n'
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'add moo=sheep comment="[ ID:2 ]"'
    assert str(diffed.expressions[1]) == 'add moo=duck comment="[ ID:3 ]"'


def test_diff_section_ethernet_names_reset():
    old = routeros_diff.sections.Section.parse(
        "/interface ethernet\n" 
        "set [ find default-name=ether1 ] name=ether1-core-primary\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/interface ethernet\n" 
        "set [ find default-name=ether1 ] name=ether1\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set [ find default-name=ether1 ] name=ether1"


def test_diff_section_dont_remove_ethernet_interfaces():
    old = routeros_diff.sections.Section.parse(
        "/interface ethernet\n" 
        "set [ find default-name=ether1 ] name=ether1\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/interface ethernet\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 0


def test_diff_section_firewall():
    old = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add chain=a comment="[ ID:1 ]"\n'
        'add chain=c comment="[ ID:3 ]"\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/ip firewall nat\n" 
        'add chain=a comment="[ ID:1 ]"\n'
        'add chain=b comment="[ ID:2 ]"\n'
        'add chain=c comment="[ ID:3 ]"\n'
    )

    diffed = new.diff(old)
    assert str(diffed.expressions[0]) == 'add chain=b comment="[ ID:2 ]" place-before=[ find where comment~"ID:3" ]'


def test_diff_section_named_default_with_comment_id():
    old = routeros_diff.sections.Section.parse(
        "/routing bgp instance\n" 
        'set default as=65000 comment="[ ID:main ]" router-id=100.127.0.1\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/routing bgp instance\n" 
        'set default as=65000 router-id=100.127.0.1 comment="[ ID:main ]" client-to-client-reflection=yes\n'
    )

    diffed = new.diff(old)
    assert str(diffed.expressions[0]) == 'set [ find where comment~"ID:main" ] client-to-client-reflection=yes'


def test_diff_section_named_default_with_comment_id_with_verbose():
    old = routeros_diff.sections.Section.parse(
        "/routing bgp instance\n" 
        'set default as=65000 comment="[ ID:main ]" router-id=100.127.0.1\n'
    )
    old_verbose = routeros_diff.sections.Section.parse(
        "/routing bgp instance\n" 
        'set default as=65000 comment="[ ID:main ]" router-id=100.127.0.1 client-to-client-reflection=yes\n'
    )
    new = routeros_diff.sections.Section.parse(
        "/routing bgp instance\n" 
        'set default as=65000 router-id=100.127.0.1 comment="[ ID:main ]" client-to-client-reflection=yes\n'
    )

    diffed = new.diff(old, old_verbose)
    assert len(diffed.expressions) == 0


def test_dont_remove_anything_that_is_already_disabled():
    old = routeros_diff.sections.Section.parse(
        "/routing ospf area\n"
        "set [ find default=yes ] disabled=yes\n"
        "add area-id=1.1.1.1 name=core\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/routing ospf area\n"
        "add area-id=1.1.1.1 name=core\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 0


def test_diff_section_dont_add_ethernet_interfaces():
    old = routeros_diff.sections.Section.parse(
        "/interface ethernet\n"
    )
    new = routeros_diff.sections.Section.parse(
        "/interface ethernet\n"
        "set [ find default-name=ether1 ] name=ether1\n"
    )

    diffed = new.diff(old)
    assert len(diffed.expressions) == 0


def test_diff_config_modify_section():
    old = parser.RouterOSConfig.parse(
        "/ip blah\n" 
        "add address=10.100.0.1/24 interface=ether1-core\n"
    )
    new = parser.RouterOSConfig.parse(
        "/ip blah\n" 
        "add address=10.120.0.1/24 interface=ether1-core\n"
    )

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 2
    assert str(diffed.expressions[0]) == 'remove [ find address="10.100.0.1/24" interface=ether1-core ]'
    assert str(diffed.expressions[1]) == 'add address="10.120.0.1/24" interface=ether1-core'


def test_diff_config_modify_identity():
    """This is one of menus that has no kind of object ids,
    rather the menu just edits one thing, the router's identity
    """
    old = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core\n"
    )
    new = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=foo\n"
    )

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set name=foo"


def test_diff_config_modify_identity_order_changed():
    old = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core foo=bar\n"
    )
    new = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set foo=bar name=core\n"
    )

    diffed = new.diff(old)
    assert len(diffed.sections) == 0, str(diffed)


def test_diff_config_modify_identity_remove_arg():
    """This is one of menus that has no kind of object ids,
    rather the menu just edits one thing, the router's identity
    """
    old = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core arg=value\n"
    )
    new = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core\n"
    )

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == 'set arg=""'


def test_diff_config_modify_identity_add_arg():
    """This is one of menus that has no kind of object ids,
    rather the menu just edits one thing, the router's identity
    """
    old = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core\n"
    )
    new = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core arg=value\n"
    )

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set arg=value"


def test_diff_config_modify_identity_add_arg_with_verbose():
    """This is one of menus that has no kind of object ids,
    rather the menu just edits one thing, the router's identity
    """
    old = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core\n"
    )
    old_verbose = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core arg=value\n"
    )

    new = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core arg=value\n"
    )

    # The verbose data shows that arg=value is already set,
    # but is just isn't visible in the regular export from the router.
    # Therefore, because the value is already set, the parser
    # can see that no changes are required
    diffed = new.diff(old, old_verbose=old_verbose)
    assert len(diffed.sections) == 0


def test_diff_config_add_identity():
    old = parser.RouterOSConfig.parse("")
    new = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=foo\n"
    )

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "set name=foo"


def test_diff_config_remove_identity():
    """This is one of menus that has no kind of object ids,
    rather the menu just edits one thing, the router's identity
    """
    old = parser.RouterOSConfig.parse(
        "/system identity\n" 
        "set name=core\n"
    )
    new = parser.RouterOSConfig.parse("")
    assert len(new.diff(old).sections) == 0


def test_diff_config_add_section():
    old = parser.RouterOSConfig.parse("")
    new = parser.RouterOSConfig.parse(
        "/routing ospf instance\n" 
        "add name=core router-id=10.127.0.1\n"
    )

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "add name=core router-id=10.127.0.1"


def test_diff_config_delete_section():
    old = parser.RouterOSConfig.parse(
        "/routing ospf instance\n" 
        "add name=core router-id=10.127.0.1\n"
    )
    new = parser.RouterOSConfig.parse("")

    diffed = new.diff(old).sections[0]
    assert len(diffed.expressions) == 1
    assert str(diffed.expressions[0]) == "remove [ find name=core ]"


def test_diff_config_integration():
    old = parser.RouterOSConfig.parse(ENTIRE_CONFIG)
    new = parser.RouterOSConfig.parse(GENERATED_CORE)
    diffed = new.diff(old)

    print(diffed)


def test_duplicate_section():
    config = parser.RouterOSConfig.parse(
        "/routing ospf instance\n"
        "add name=core router-id=10.127.0.1\n"
        "/routing ospf instance\n"
        "add name=another-area router-id=10.127.0.1\n"
    )
    assert len(config.sections) == 1
    assert len(config.sections[0].expressions) == 2


# fmt: on

OSPF_SECTION = """
/routing ospf network
add area=core network=10.100.0.0/24
add area=another-area network=10.126.0.0/29
add area=another-area network=10.126.0.8/29
add area=core network=10.127.0.0/24
"""

ENTIRE_CONFIG = """
# feb/21/2021 20:53:34 by RouterOS 6.46.8
# software id =
#
#
#
/interface bridge
add name=loopback
/interface ethernet
set [ find default-name=ether1 ] name=ether1-core
set [ find default-name=ether2 ] name=ether2-bp-primary
set [ find default-name=ether3 ] name=ether3-bp-backup
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/routing bgp instance
set default as=65555 client-to-client-reflection=no router-id=10.127.0.1
/routing ospf area
set [ find default=yes ] name=another-area
add area-id=1.1.1.1 name=core
/routing ospf instance
set [ find default=yes ] name=another-area router-id=10.127.0.1
add name=core router-id=10.127.0.1
/ip address
add address=10.100.0.1/24 interface=ether1-core network=10.100.0.0
add address=10.127.0.1 interface=loopback network=10.127.0.1
add address=10.126.0.1/29 interface=ether2-bp-primary network=10.126.0.0
add address=10.126.0.9/29 interface=ether3-bp-backup network=10.126.0.8
/ip dhcp-client
add disabled=no interface=ether1-core
/ip service
set telnet address=10.0.0.0/8 disabled=yes
set ftp address=10.0.0.0/8 disabled=yes
set www address=10.0.0.0/8 disabled=yes
set ssh address=10.0.0.0/8
set www-ssl address=10.0.0.0/8
set api address=10.0.0.0/8 disabled=yes
set winbox address=10.0.0.0/8
set api-ssl address=10.0.0.0/8
/mpls ldp
set enabled=yes lsr-id=10.127.0.1 transport-address=10.127.0.1
/mpls ldp interface
add interface=ether1-core transport-address=10.127.0.1
add interface=ether2-bp-primary transport-address=10.127.0.1
add interface=ether3-bp-backup transport-address=10.127.0.1
/routing bgp peer
add hold-time=1m30s multihop=yes name=rr1 remote-address=10.127.0.3 remote-as=65555 update-source=loopback
/routing ospf interface
add dead-interval=4s hello-interval=1s interface=ether2-bp-primary network-type=point-to-point
/routing ospf network
add area=core network=10.100.0.0/24
add area=another-area network=10.126.0.0/29
add area=another-area network=10.126.0.8/29
add area=core network=10.127.0.0/24
/system identity
set name=core
/system logging
add topics=bgp,!raw
/tool sniffer
set filter-ip-protocol=icmp
"""


GENERATED_CORE = """
#########################################
####### CORE
# #######################################
# Auto-generated configuration

/system identity
set name=core

/interface vlan
add interface=ether1 on core vlan-id=99 name=management
add interface=ether1 on core vlan-id=1001 name=core-vlan
add interface=ether1 on core vlan-id=2050 name=ptp-core-bp-primary
add interface=ether1 on core vlan-id=2051 name=ptp-core-bp-backup

/interface bridge
add name=loopback

/ip address
add address=10.127.0.1 interface=loopback network=10.127.0.1
add address=10.100.0.1/16 interface=management network=10.100.0.0
add address=10.125.0.1/24 interface=core-vlan network=10.125.0.0
add address=10.126.0.1/29 interface=ptp-core-bp-primary network=10.126.0.0
add address=10.126.0.9/29 interface=ptp-core-bp-backup network=10.126.0.8

/routing ospf area
add area-id=1.1.1.1 name=core
add area-id=2.2.2.2 name=another-area

/routing ospf instance
add name=core router-id=10.127.0.1
add name=another-area router-id=10.127.0.1

/routing ospf interface
add dead-interval=4s hello-interval=1s interface=core-vlan network-type=broadcast
add dead-interval=4s hello-interval=1s interface=ptp-core-bp-primary network-type=point-to-point
add dead-interval=4s hello-interval=1s interface=ptp-core-bp-backup network-type=point-to-point

/routing ospf network
add area=core network=10.125.0.0/24
add area=another-area network=10.126.0.0/29
add area=another-area network=10.126.0.8/29

/routing bgp instance
set default as=65555 client-to-client-reflection=no router-id=10.127.0.1

/routing bgp peer

/mpls ldp
set enabled=yes lsr-id=10.127.0.1 transport-address=10.127.0.1

/mpls ldp interface
add interface=management transport-address=10.127.0.1
add interface=core-vlan transport-address=10.127.0.1
add interface=ptp-core-bp-primary transport-address=10.127.0.1
add interface=ptp-core-bp-backup transport-address=10.127.0.1

/ip service
set telnet address=10.0.0.0/8 disabled=yes
set ftp address=10.0.0.0/8 disabled=yes
set www address=10.0.0.0/8 disabled=yes
set ssh address=10.0.0.0/8
set www-ssl address=10.0.0.0/8
set api address=10.0.0.0/8 disabled=yes
set winbox address=10.0.0.0/8
set api-ssl address=10.0.0.0/8

/ip pool

/ip dhcp-server network

/ip dhcp-server
"""
