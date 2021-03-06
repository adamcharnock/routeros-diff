# Library and utility for diffing RouterOS files

[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

## Prettify

The `routeros_prettify` (alias `ros_prettify`) command will parse an existing configuration and re-print it in a 
standard format with common sections collapsed:

```
routeros_prettify old_config.rsc new_config.rsc
```

Or using Python:

```python
from routeros_diff.parser import RouterOSConfig
config = RouterOSConfig.parse(config_string)
print(config)
```

## Diff

The `routeros_diff` (alias `ros_diff`) command will take two RouterOS files and diff them:

```
routeros_diff old_config.rsc new_config.rsc
```

Or using Python:

```python
from routeros_diff.parser import RouterOSConfig
old = RouterOSConfig.parse(old_config_string)
new = RouterOSConfig.parse(new_config_string)
print(old.diff(new))
```

### Diffing features

* IDs in comments (i.e. `comment="Block outgoing SMTP [ ID:block-smtp ]"`). IDs in comments allow 
  for diffing of expressions which have no natural IDs (a good example of this is firewall rules).
* Maintaining of order where ordering is important (again, in firewall rules)

### Limitations

This aim is for this diffing process to work well within a limited range of conditions. 
The configuration format is an entire scripting language in itself, and so this library 
cannot sensibly hope to parse any arbitrary input. As a rule of thumb, this library should 
be able to diff anything produced by `/export`

### Reporting errors

Seeing something strange in your diff output? Please report the error with the following information:

* The input
* The actual output
* What you think the output should be instead

Please minimise the size of this data as much as possible. The smaller and more specific the example of the problem,
the easier it will be for us to find a resolution.

## Examples:

Simple:

```
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

Firewall NAT rules:

```
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

# Release process:

```
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
