
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

# Don't perform creations in these sections
NO_CREATIONS = ("/interface ethernet", )








