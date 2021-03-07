# Diff and prettify RouterOS configuration files

[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![Tests](https://github.com/gardunha/routeros-diff/actions/workflows/ci.yaml/badge.svg)](https://github.com/gardunha/routeros-diff/actions/workflows/ci.yaml)


## Get a diff

The `routeros_diff` (alias `ros_diff`) command will take two RouterOS files and diff them:

    routeros_diff old_config.rsc new_config.rsc

Or using Python:

```python
from routeros_diff.parser import RouterOSConfig
old = RouterOSConfig.parse(old_config_string)
new = RouterOSConfig.parse(new_config_string)
print(old.diff(new))
```

## Examples:

A simple example first:

```r
# Old:
/routing ospf instance
add name=core router-id=100.127.0.1

# New:
/routing ospf instance
add name=core router-id=100.127.0.99

# Diff:
/routing ospf instance
set [ find name=core ] router-id=100.127.0.99
```

Here is a more complex example where we use custom IDs in order to maintain 
expression ordering (see 'Natural Keys & IDs' below for details):

```r
# Old:
/ip firewall nat 
add chain=a comment="Example text [ ID:1 ]"
add chain=c comment="[ ID:3 ]"

# New:
/ip firewall nat 
add chain=a comment="Example text [ ID:1 ]"
add chain=b comment="[ ID:2 ]"
add chain=c comment="[ ID:3 ]"

# Diff:
/ip firewall nat 
add chain=b comment="[ ID:2 ]" place-before=[ find where comment~ID:3 ]
```

### Usage & limitations

This aim is for this diffing process to work well within a limited range of conditions.
The configuration format is an entire scripting language in itself, and so this library
cannot sensibly hope to parse any arbitrary input. As a rule of thumb, this library should
be able to diff anything produced by `/export`.

### Sections and expressions

The following is NOT supported:

```r
## NOT SUPPORTED, DONT DO THIS ##
/routing ospf instance add name=core router-id=100.127.0.1
```

Rather, this must be formatted as separate 'sections' and 'expressions'. For example:

```r
/routing ospf instance 
add name=core router-id=100.127.0.1
```

The section in this example is `/routing ospf instance`, and the expression is `add name=core router-id=100.127.0.1`.
Each section may contain multiple expressions (just like the output you see from `/export`).

### Natural Keys & IDs

The parser will try to uniquely identify each expression. This allows the parser to be intelligent regarding
additions, modifications, deletions, and ordering.

The parser refers to these unique identities as naturals keys & natural IDs. For example:

```r
add name=core router-id=100.127.0.1
```

Here the natural key is `name` and the natural ID is `core`. The parser assumes `name` will be the natural key,
but is configured to use other keys in some situations (see `NATURAL_KEYS`).

Additionally, you can choose to manually add your own IDs to expressions. This is done using comments.
For example:

```r
add chain=a comment="[ ID:1 ]"
```

These comment-based IDs take priority over whatever the parser may have otherwise used.
If using comment IDs, you should make sure you set them for all expressions in
that section.

This is especially useful for firewall rules. The order of firewall rules is important, and they have no
obvious natural keys/IDs. Using comments IDs for your firewall rules allows the parser to
intelligently maintain order. For example:

```r
# Old:
/ip firewall nat 
add chain=a comment="Example text [ ID:1 ]"
add chain=c comment="[ ID:3 ]"

# New:
/ip firewall nat 
add chain=a comment="Example text [ ID:1 ]"
add chain=b comment="[ ID:2 ]"
add chain=c comment="[ ID:3 ]"

# Diff:
/ip firewall nat 
add chain=b comment="[ ID:2 ]" place-before=[ find where comment~ID:3 ]
```

Note that the parser uses `place-before` to correctly place the new firewall rule.

*Without using comment IDs, the parse would have to drop and recreate all firewall rules.* This would
be non-ideal for reasons of both security and reliability.

### Reporting errors

Seeing something strange in your diff output? Please report the error with the following information:

* The input
* The actual output
* What you think the output should be instead

Please minimise the size of this data as much as possible. The smaller and more specific the example of the problem,
the easier it will be for us to find a resolution.

## Prettify

The `routeros_prettify` (alias `ros_prettify`) command will parse an existing configuration and re-print it in a
standard format with common sections collapsed:

```r
routeros_prettify old_config.rsc new_config.rsc
```

Or using Python:

```python
from routeros_diff.parser import RouterOSConfig
config = RouterOSConfig.parse(config_string)
print(config)
```

## Concepts

This is a **section** with a path of `/ip address` and two expressions:

```r
/ip address
add address=1.2.3.4
add address=5.6.7.8
```

This is an **expression** with a command of **add**, and a key-value argument of `address=1.2.3.4`:

```r
add address=1.2.3.4
```

# Release process:

```bash
export VERSION=a.b.c
dephell convert
black setup.py

git add .
git commit -m "Releasing version $VERSION"

git tag "v$VERSION"
git branch "v$VERSION"
git push origin \
    refs/tags/"v$VERSION" \
    refs/heads/"v$VERSION" \
    main

# Wait for CI to pass

poetry publish --build
```
