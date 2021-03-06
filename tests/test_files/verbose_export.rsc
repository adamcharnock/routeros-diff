# feb/22/2021 01:08:08 by RouterOS 6.48.1
# software id = RI0B-IPQ6
#
# model = RB952Ui-5ac2nD
# serial number = CC3E0C039212
/interface bridge
add ageing-time=5m arp=enabled arp-timeout=auto auto-mac=yes dhcp-snooping=no disabled=no ether-type=0x8100 fast-forward=yes forward-delay=15s frame-types=admit-all igmp-snooping=no ingress-filtering=no max-message-age=20s mtu=auto \
    name=downstream priority=0x8000 protocol-mode=rstp pvid=1 transmit-hold-count=6 vlan-filtering=yes
add ageing-time=5m arp=enabled arp-timeout=auto auto-mac=yes dhcp-snooping=no disabled=no fast-forward=yes forward-delay=15s igmp-snooping=no max-message-age=20s mtu=auto name=loopback priority=0x8000 protocol-mode=rstp \
    transmit-hold-count=6 vlan-filtering=no
add ageing-time=5m arp=enabled arp-timeout=auto auto-mac=yes dhcp-snooping=no disabled=no fast-forward=yes forward-delay=15s igmp-snooping=no max-message-age=20s mtu=auto name=upstream priority=0x8000 protocol-mode=rstp \
    transmit-hold-count=6 vlan-filtering=no
/interface ethernet
set [ find default-name=ether1 ] advertise=10M-half,10M-full,100M-half,100M-full arp=enabled arp-timeout=auto auto-negotiation=yes bandwidth=unlimited/unlimited disabled=no full-duplex=yes l2mtu=1598 loop-protect=default \
    loop-protect-disable-time=5m loop-protect-send-interval=5s mac-address=48:8F:5A:5A:90:01 mtu=1500 name=ether1 orig-mac-address=48:8F:5A:5A:90:01 rx-flow-control=off speed=100Mbps tx-flow-control=off
set [ find default-name=ether2 ] advertise=10M-half,10M-full,100M-half,100M-full arp=enabled arp-timeout=auto auto-negotiation=yes bandwidth=unlimited/unlimited disabled=no full-duplex=yes l2mtu=1598 loop-protect=default \
    loop-protect-disable-time=5m loop-protect-send-interval=5s mac-address=48:8F:5A:5A:90:02 mtu=1500 name=ether2 orig-mac-address=48:8F:5A:5A:90:02 rx-flow-control=off speed=100Mbps tx-flow-control=off
set [ find default-name=ether3 ] advertise=10M-half,10M-full,100M-half,100M-full arp=enabled arp-timeout=auto auto-negotiation=yes bandwidth=unlimited/unlimited disabled=no full-duplex=yes l2mtu=1598 loop-protect=default \
    loop-protect-disable-time=5m loop-protect-send-interval=5s mac-address=48:8F:5A:5A:90:03 mtu=1500 name=ether3 orig-mac-address=48:8F:5A:5A:90:03 rx-flow-control=off speed=100Mbps tx-flow-control=off
set [ find default-name=ether4 ] advertise=10M-half,10M-full,100M-half,100M-full arp=enabled arp-timeout=auto auto-negotiation=yes bandwidth=unlimited/unlimited disabled=no full-duplex=yes l2mtu=1598 loop-protect=default \
    loop-protect-disable-time=5m loop-protect-send-interval=5s mac-address=48:8F:5A:5A:90:04 mtu=1500 name=ether4 orig-mac-address=48:8F:5A:5A:90:04 rx-flow-control=off speed=100Mbps tx-flow-control=off
set [ find default-name=ether5 ] advertise=10M-half,10M-full,100M-half,100M-full arp=enabled arp-timeout=auto auto-negotiation=yes bandwidth=unlimited/unlimited disabled=no full-duplex=yes l2mtu=1598 loop-protect=default \
    loop-protect-disable-time=5m loop-protect-send-interval=5s mac-address=48:8F:5A:5A:90:05 mtu=1500 name=ether5 orig-mac-address=48:8F:5A:5A:90:05 poe-out=auto-on poe-priority=10 power-cycle-interval=none !power-cycle-ping-address \
    power-cycle-ping-enabled=no !power-cycle-ping-timeout rx-flow-control=off speed=100Mbps tx-flow-control=off
/queue interface
set downstream queue=no-queue
set loopback queue=no-queue
set upstream queue=no-queue
/interface vlan
add arp=enabled arp-timeout=auto disabled=no interface=ether3 loop-protect=default loop-protect-disable-time=5m loop-protect-send-interval=5s mtu=1550 name=gn-mgmt use-service-tag=no vlan-id=84
/queue interface
set gn-mgmt queue=no-queue
/interface ethernet switch
set 0 cpu-flow-control=yes mirror-source=none mirror-target=none name=switch1
/interface ethernet switch port
set 0 default-vlan-id=0 vlan-header=leave-as-is vlan-mode=disabled
set 1 default-vlan-id=0 vlan-header=leave-as-is vlan-mode=disabled
set 2 default-vlan-id=0 vlan-header=leave-as-is vlan-mode=disabled
set 3 default-vlan-id=0 vlan-header=leave-as-is vlan-mode=disabled
set 4 default-vlan-id=0 vlan-header=leave-as-is vlan-mode=disabled
set 5 default-vlan-id=0 vlan-header=leave-as-is vlan-mode=disabled
/interface list
set [ find name=all ] comment="contains all interfaces" exclude="" include="" name=all
set [ find name=none ] comment="contains no interfaces" exclude="" include="" name=none
set [ find name=dynamic ] comment="contains dynamic interfaces" exclude="" include="" name=dynamic
set [ find name=static ] comment="contains static interfaces" exclude="" include="" name=static
/interface lte apn
set [ find default=yes ] add-default-route=yes apn=internet default-route-distance=2 name=default use-peer-dns=yes
/interface wireless security-profiles
set [ find default=yes ] authentication-types="" disable-pmkid=no eap-methods=passthrough group-ciphers=aes-ccm group-key-update=5m interim-update=0s management-protection=disabled mode=none mschapv2-username="" name=default \
    radius-called-format=mac:ssid radius-eap-accounting=no radius-mac-accounting=no radius-mac-authentication=no radius-mac-caching=disabled radius-mac-format=XX:XX:XX:XX:XX:XX radius-mac-mode=as-username static-algo-0=none \
    static-algo-1=none static-algo-2=none static-algo-3=none static-sta-private-algo=none static-transmit-key=key-0 supplicant-identity=MikroTik tls-certificate=none tls-mode=no-certificates unicast-ciphers=aes-ccm
/interface wireless
set [ find default-name=wlan1 ] adaptive-noise-immunity=none allow-sharedkey=no ampdu-priorities=0 amsdu-limit=8192 amsdu-threshold=8192 antenna-gain=2 area="" arp=enabled arp-timeout=auto band=2ghz-b/g basic-rates-a/g=6Mbps \
    basic-rates-b=1Mbps bridge-mode=enabled channel-width=20mhz compression=no country=etsi default-ap-tx-limit=0 default-authentication=yes default-client-tx-limit=0 default-forwarding=yes disable-running-check=no disabled=yes \
    disconnect-timeout=3s distance=dynamic frame-lifetime=0 frequency=2412 frequency-mode=regulatory-domain frequency-offset=0 guard-interval=any hide-ssid=no ht-basic-mcs=mcs-0,mcs-1,mcs-2,mcs-3,mcs-4,mcs-5,mcs-6,mcs-7 \
    ht-supported-mcs=mcs-0,mcs-1,mcs-2,mcs-3,mcs-4,mcs-5,mcs-6,mcs-7,mcs-8,mcs-9,mcs-10,mcs-11,mcs-12,mcs-13,mcs-14,mcs-15,mcs-16,mcs-17,mcs-18,mcs-19,mcs-20,mcs-21,mcs-22,mcs-23 hw-fragmentation-threshold=disabled hw-protection-mode=\
    none hw-protection-threshold=0 hw-retries=7 installation=any interworking-profile=disabled keepalive-frames=enabled l2mtu=1600 mac-address=48:8F:5A:5A:90:07 max-station-count=2007 mode=station mtu=1500 multicast-buffering=enabled \
    multicast-helper=default name=wlan1 noise-floor-threshold=default nv2-cell-radius=30 nv2-downlink-ratio=50 nv2-mode=dynamic-downlink nv2-noise-floor-offset=default nv2-qos=default nv2-queue-count=2 nv2-security=disabled \
    nv2-sync-secret="" on-fail-retry-time=100ms preamble-mode=both radio-name=488F5A5A9007 rate-selection=advanced rate-set=default rx-chains=0,1 scan-list=default secondary-channel="" security-profile=default skip-dfs-channels=\
    disabled ssid=MikroTik station-bridge-clone-mac=00:00:00:00:00:00 station-roaming=enabled supported-rates-a/g=6Mbps,9Mbps,12Mbps,18Mbps,24Mbps,36Mbps,48Mbps,54Mbps supported-rates-b=1Mbps,2Mbps,5.5Mbps,11Mbps tdma-period-size=2 \
    tx-chains=0,1 tx-power-mode=default update-stats-interval=disabled vlan-id=1 vlan-mode=no-tag wds-cost-range=50-150 wds-default-bridge=none wds-default-cost=100 wds-ignore-ssid=no wds-mode=disabled wireless-protocol=any \
    wmm-support=disabled wps-mode=push-button
set [ find default-name=wlan2 ] adaptive-noise-immunity=none allow-sharedkey=no ampdu-priorities=0 amsdu-limit=8192 amsdu-threshold=8192 antenna-gain=2 area="" arp=enabled arp-timeout=auto band=5ghz-a basic-rates-a/g=6Mbps \
    bridge-mode=enabled channel-width=20mhz compression=no country=etsi default-ap-tx-limit=0 default-authentication=yes default-client-tx-limit=0 default-forwarding=yes disable-running-check=no disabled=yes disconnect-timeout=3s \
    distance=dynamic frame-lifetime=0 frequency=5180 frequency-mode=regulatory-domain frequency-offset=0 guard-interval=any hide-ssid=no ht-basic-mcs=mcs-0,mcs-1,mcs-2,mcs-3,mcs-4,mcs-5,mcs-6,mcs-7 ht-supported-mcs=\
    mcs-0,mcs-1,mcs-2,mcs-3,mcs-4,mcs-5,mcs-6,mcs-7,mcs-8,mcs-9,mcs-10,mcs-11,mcs-12,mcs-13,mcs-14,mcs-15,mcs-16,mcs-17,mcs-18,mcs-19,mcs-20,mcs-21,mcs-22,mcs-23 hw-fragmentation-threshold=disabled hw-protection-mode=none \
    hw-protection-threshold=0 hw-retries=7 installation=any interworking-profile=disabled keepalive-frames=enabled l2mtu=1600 mac-address=48:8F:5A:5A:90:06 max-station-count=2007 mode=station mtu=1500 multicast-buffering=enabled \
    multicast-helper=default name=wlan2 nv2-cell-radius=30 nv2-downlink-ratio=50 nv2-mode=dynamic-downlink nv2-qos=default nv2-queue-count=2 nv2-security=disabled nv2-sync-secret="" on-fail-retry-time=100ms preamble-mode=both \
    radio-name=488F5A5A9006 rate-selection=advanced rate-set=default rx-chains=0 scan-list=default secondary-channel="" security-profile=default skip-dfs-channels=disabled ssid=MikroTik station-bridge-clone-mac=00:00:00:00:00:00 \
    station-roaming=enabled supported-rates-a/g=6Mbps,9Mbps,12Mbps,18Mbps,24Mbps,36Mbps,48Mbps,54Mbps tdma-period-size=2 tx-chains=0 tx-power-mode=default update-stats-interval=disabled vht-basic-mcs=mcs0-7 vht-supported-mcs=\
    mcs0-9,mcs0-9,mcs0-9 vlan-id=1 vlan-mode=no-tag wds-cost-range=50-150 wds-default-bridge=none wds-default-cost=100 wds-ignore-ssid=no wds-mode=disabled wireless-protocol=any wmm-support=disabled wps-mode=push-button
/interface wireless manual-tx-power-table
set wlan1 manual-tx-powers="1Mbps:17,2Mbps:17,5.5Mbps:17,11Mbps:17,6Mbps:17,9Mbps:17,12Mbps:17,18Mbps:17,24Mbps:17,36Mbps:17,48Mbps:17,54Mbps:17,HT20-0:17,HT20-1:17,HT20-2:17,HT20-3:17,HT20-4:17,HT20-5:17,HT20-6:17,HT20-7:17,HT40-0:17,\
    HT40-1:17,HT40-2:17,HT40-3:17,HT40-4:17,HT40-5:17,HT40-6:17,HT40-7:17"
set wlan2 manual-tx-powers="1Mbps:17,2Mbps:17,5.5Mbps:17,11Mbps:17,6Mbps:17,9Mbps:17,12Mbps:17,18Mbps:17,24Mbps:17,36Mbps:17,48Mbps:17,54Mbps:17,HT20-0:17,HT20-1:17,HT20-2:17,HT20-3:17,HT20-4:17,HT20-5:17,HT20-6:17,HT20-7:17,HT40-0:17,\
    HT40-1:17,HT40-2:17,HT40-3:17,HT40-4:17,HT40-5:17,HT40-6:17,HT40-7:17"
/ip dhcp-client option
set clientid_duid code=61 name=clientid_duid value="0xff\$(CLIENT_DUID)"
set clientid code=61 name=clientid value="0x01\$(CLIENT_MAC)"
set hostname code=12 name=hostname value="\$(HOSTNAME)"
/ip hotspot profile
set [ find default=yes ] dns-name="" hotspot-address=0.0.0.0 html-directory=flash/hotspot html-directory-override="" http-cookie-lifetime=3d http-proxy=0.0.0.0:0 login-by=cookie,http-chap name=default rate-limit="" smtp-server=0.0.0.0 \
    split-user-domain=no use-radius=no
/ip hotspot user profile
set [ find default=yes ] add-mac-cookie=yes address-list="" idle-timeout=none !insert-queue-before keepalive-timeout=2m mac-cookie-timeout=3d name=default !parent-queue !queue-type shared-users=1 status-autorefresh=1m \
    transparent-proxy=no
/ip ipsec mode-config
set [ find default=yes ] name=request-only responder=no use-responder-dns=exclusively
/ip ipsec policy group
set [ find default=yes ] name=default
/ip ipsec profile
set [ find default=yes ] dh-group=modp2048,modp1024 dpd-interval=2m dpd-maximum-failures=5 enc-algorithm=aes-128,3des hash-algorithm=sha1 lifetime=1d name=default nat-traversal=yes proposal-check=obey
add dh-group=modp1024 dpd-interval=10s dpd-maximum-failures=3 enc-algorithm=aes-128 hash-algorithm=sha1 lifetime=8h name=vpc nat-traversal=no proposal-check=obey
/ip ipsec peer
add address=99.81.162.31/32 disabled=yes exchange-mode=main local-address=83.132.47.129 name=vpc2 profile=vpc send-initial-contact=yes
add address=52.210.66.152/32 disabled=yes exchange-mode=main local-address=83.132.47.129 name=vpc1 profile=vpc send-initial-contact=yes
/ip ipsec proposal
set [ find default=yes ] auth-algorithms=sha1 disabled=no enc-algorithms=aes-256-cbc,aes-192-cbc,aes-128-cbc lifetime=30m name=default pfs-group=modp1024
add auth-algorithms=sha1 comment="AWS PROPOSAL" disabled=no enc-algorithms=aes-128-cbc lifetime=1h name=aws pfs-group=modp1024
/ip pool
add name=pool1 ranges=192.168.1.100-192.168.1.200
add name=mgmt-pool ranges=10.99.99.10-10.99.99.100
/ip dhcp-server
add address-pool=pool1 authoritative=yes disabled=no interface=downstream lease-script="" lease-time=1h name=server1 use-radius=no
add address-pool=mgmt-pool authoritative=yes disabled=no interface=gn-mgmt lease-script="" lease-time=10m name=gn-mgmt-server use-radius=no
/ppp profile
set *0 address-list="" !bridge !bridge-horizon bridge-learning=default !bridge-path-cost !bridge-port-priority change-tcp-mss=yes !dns-server !idle-timeout !incoming-filter !insert-queue-before !interface-list !local-address name=\
    default on-down="" on-up="" only-one=default !outgoing-filter !parent-queue !queue-type !rate-limit !remote-address !session-timeout use-compression=default use-encryption=default use-mpls=default use-upnp=default !wins-server
set *FFFFFFFE address-list="" !bridge !bridge-horizon bridge-learning=default !bridge-path-cost !bridge-port-priority change-tcp-mss=yes !dns-server !idle-timeout !incoming-filter !insert-queue-before !interface-list !local-address \
    name=default-encryption on-down="" on-up="" only-one=default !outgoing-filter !parent-queue !queue-type !rate-limit !remote-address !session-timeout use-compression=default use-encryption=yes use-mpls=default use-upnp=default \
    !wins-server
/interface sstp-client
add add-default-route=yes authentication=pap,chap,mschap1,mschap2 certificate=client connect-to=54.76.212.121:443 default-route-distance=10 dial-on-demand=no disabled=no http-proxy=0.0.0.0:443 keepalive-timeout=60 max-mru=1500 \
    max-mtu=1500 mrru=disabled name=sstp-out1 pfs=no profile=default tls-version=any user=Quinta verify-server-address-from-certificate=no verify-server-certificate=yes
/queue interface
set sstp-out1 queue=no-queue
/queue type
set 0 kind=pfifo name=default pfifo-limit=50
set 1 kind=pfifo name=ethernet-default pfifo-limit=50
set 2 kind=sfq name=wireless-default sfq-allot=1514 sfq-perturb=5
set 3 kind=red name=synchronous-default red-avg-packet=1000 red-burst=20 red-limit=60 red-max-threshold=50 red-min-threshold=10
set 4 kind=sfq name=hotspot-default sfq-allot=1514 sfq-perturb=5
add kind=sfq name=sfq-default sfq-allot=1514 sfq-perturb=5
set 6 kind=pcq name=pcq-upload-default pcq-burst-rate=0 pcq-burst-threshold=0 pcq-burst-time=10s pcq-classifier=src-address pcq-dst-address-mask=32 pcq-dst-address6-mask=128 pcq-limit=50KiB pcq-rate=0 pcq-src-address-mask=32 \
    pcq-src-address6-mask=128 pcq-total-limit=2000KiB
set 7 kind=pcq name=pcq-download-default pcq-burst-rate=0 pcq-burst-threshold=0 pcq-burst-time=10s pcq-classifier=dst-address pcq-dst-address-mask=32 pcq-dst-address6-mask=128 pcq-limit=50KiB pcq-rate=0 pcq-src-address-mask=32 \
    pcq-src-address6-mask=128 pcq-total-limit=2000KiB
set 8 kind=none name=only-hardware-queue
set 9 kind=mq-pfifo mq-pfifo-limit=50 name=multi-queue-ethernet-default
set 10 kind=pfifo name=default-small pfifo-limit=10
/queue interface
set ether1 queue=only-hardware-queue
set ether2 queue=only-hardware-queue
set ether3 queue=only-hardware-queue
set ether4 queue=only-hardware-queue
set ether5 queue=only-hardware-queue
set wlan1 queue=wireless-default
set wlan2 queue=wireless-default
/interface wireless nstreme
set wlan1 disable-csma=no enable-nstreme=no enable-polling=yes framer-limit=3200 framer-policy=none
set wlan2 disable-csma=no enable-nstreme=no enable-polling=yes framer-limit=3200 framer-policy=none
/queue tree
add bucket-size=0.01 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name=DOWN packet-mark="" parent=downstream priority=8 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="1. VOIP" packet-mark=VOIP parent=DOWN priority=1 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="2. DNS" packet-mark=DNS parent=DOWN priority=2 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="3. ACK" packet-mark=ACK parent=DOWN priority=3 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="4. UDP" packet-mark=UDP parent=DOWN priority=3 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="5. ICMP" packet-mark=ICMP parent=DOWN priority=4 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="6. HTTP" packet-mark=HTTP parent=DOWN priority=5 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="9. HTTP_BIG" packet-mark=HTTP_BIG parent=DOWN priority=6 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="8. QUIC" packet-mark=QUIC parent=DOWN priority=7 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="7. OTHER" packet-mark=OTHER parent=DOWN priority=8 queue=default
add bucket-size=0.01 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=25M name=UP packet-mark="" parent=upstream priority=8 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="1. VOIP_" packet-mark=VOIP parent=UP priority=1 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="2. DNS_" packet-mark=DNS parent=UP priority=2 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="3. ACK_" packet-mark=ACK parent=UP priority=3 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="4. UDP_" packet-mark=UDP parent=UP priority=3 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="5. ICMP_" packet-mark=ICMP parent=UP priority=4 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="6. HTTP_" packet-mark=HTTP parent=UP priority=5 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="7. HTTP_BIG_" packet-mark=HTTP_BIG parent=UP priority=6 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="8. QUIC_" packet-mark=QUIC parent=UP priority=7 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="9. OTHER_" packet-mark=OTHER parent=UP priority=8 queue=default
add bucket-size=0.1 burst-limit=0 burst-threshold=0 burst-time=0s disabled=no limit-at=0 max-limit=0 name="5. PS4" packet-mark=PS4 parent=DOWN priority=8 queue=default
/routing bgp instance
set default as=65530 client-to-client-reflection=yes !cluster-id !confederation disabled=yes ignore-as-path-len=no name=default out-filter="" redistribute-connected=no redistribute-ospf=no redistribute-other-bgp=no redistribute-rip=no \
    redistribute-static=no router-id=0.0.0.0 routing-table=""
/routing ospf instance
set [ find default=yes ] disabled=no distribute-default=never !domain-id !domain-tag in-filter=ospf-in metric-bgp=auto metric-connected=20 metric-default=1 metric-other-ospf=auto metric-rip=20 metric-static=20 !mpls-te-area \
    !mpls-te-router-id name=default out-filter=ospf-out redistribute-bgp=no redistribute-connected=no redistribute-other-ospf=no redistribute-rip=no redistribute-static=no router-id=10.254.0.5 !routing-table !use-dn
/routing ospf area
set [ find default=yes ] area-id=0.0.0.0 disabled=no instance=default name=backbone type=default
add area-id=1.1.1.1 disabled=no instance=default name=world type=default
/snmp community
set [ find default=yes ] addresses=::/0 authentication-protocol=MD5 disabled=no encryption-protocol=DES name=public read-access=yes security=none write-access=no
/system logging action
set 0 memory-lines=1000 memory-stop-on-full=no name=memory target=memory
set 1 disk-file-count=2 disk-file-name=flash/log disk-lines-per-file=1000 disk-stop-on-full=no name=disk target=disk
set 2 name=echo remember=yes target=echo
set 3 bsd-syslog=no name=remote remote=0.0.0.0 remote-port=514 src-address=0.0.0.0 syslog-facility=daemon syslog-severity=auto syslog-time-format=bsd-syslog target=remote
add bsd-syslog=no name=syslog remote=10.200.0.20 remote-port=514 src-address=0.0.0.0 syslog-facility=daemon syslog-severity=auto syslog-time-format=bsd-syslog target=remote
/user group
set read name=read policy=local,telnet,ssh,reboot,read,test,winbox,password,web,sniff,sensitive,api,romon,tikapp,!ftp,!write,!policy,!dude skin=default
set write name=write policy=local,telnet,ssh,reboot,read,write,test,winbox,password,web,sniff,sensitive,api,romon,tikapp,!ftp,!policy,!dude skin=default
set full name=full policy=local,telnet,ssh,ftp,reboot,read,write,policy,test,winbox,password,web,sniff,sensitive,api,romon,dude,tikapp skin=default
/caps-man aaa
set called-format=mac:ssid interim-update=disabled mac-caching=disabled mac-format=XX:XX:XX:XX:XX:XX mac-mode=as-username
/caps-man manager
set ca-certificate=none certificate=none enabled=no package-path="" require-peer-certificate=no upgrade-policy=none
/caps-man manager interface
set [ find default=yes ] disabled=no forbid=no interface=all
/certificate settings
set crl-download=no crl-store=ram crl-use=no
/interface bridge port
add auto-isolate=no bpdu-guard=no bridge=upstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none hw=yes ingress-filtering=no interface=ether2 internal-path-cost=10 learn=auto \
    multicast-router=temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
add auto-isolate=no bpdu-guard=no bridge=downstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none hw=yes ingress-filtering=no interface=ether1 internal-path-cost=10 learn=auto \
    multicast-router=temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
add auto-isolate=no bpdu-guard=no bridge=downstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none hw=yes ingress-filtering=no interface=ether3 internal-path-cost=10 learn=auto \
    multicast-router=temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
add auto-isolate=no bpdu-guard=no bridge=downstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none hw=yes ingress-filtering=no interface=ether4 internal-path-cost=10 learn=auto \
    multicast-router=temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
add auto-isolate=no bpdu-guard=no bridge=downstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none hw=yes ingress-filtering=no interface=ether5 internal-path-cost=10 learn=auto \
    multicast-router=temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
add auto-isolate=no bpdu-guard=no bridge=downstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none ingress-filtering=no interface=wlan1 internal-path-cost=10 learn=auto multicast-router=\
    temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
add auto-isolate=no bpdu-guard=no bridge=downstream broadcast-flood=yes disabled=no edge=auto fast-leave=no frame-types=admit-all horizon=none ingress-filtering=no interface=wlan2 internal-path-cost=10 learn=auto multicast-router=\
    temporary-query path-cost=10 point-to-point=auto priority=0x80 pvid=1 restricted-role=no restricted-tcn=no tag-stacking=no trusted=no unknown-multicast-flood=yes unknown-unicast-flood=yes
/interface bridge port-controller
# disabled
set bridge=none cascade-ports="" switch=none
/interface bridge port-extender
# disabled
set control-ports="" excluded-ports="" switch=none
/interface bridge settings
set allow-fast-path=yes use-ip-firewall=no use-ip-firewall-for-pppoe=no use-ip-firewall-for-vlan=no
/ip firewall connection tracking
set enabled=auto generic-timeout=10m icmp-timeout=10s loose-tcp-tracking=yes tcp-close-timeout=10s tcp-close-wait-timeout=10s tcp-established-timeout=1d tcp-fin-wait-timeout=10s tcp-last-ack-timeout=10s tcp-max-retrans-timeout=5m \
    tcp-syn-received-timeout=5s tcp-syn-sent-timeout=5s tcp-time-wait-timeout=10s tcp-unacked-timeout=5m udp-stream-timeout=3m udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic lldp-med-net-policy-vlan=disabled protocol=cdp,lldp,mndp
/ip settings
set accept-redirects=no accept-source-route=no allow-fast-path=yes arp-timeout=30s icmp-rate-limit=10 icmp-rate-mask=0x1818 ip-forward=yes max-neighbor-entries=8192 route-cache=yes rp-filter=no secure-redirects=yes send-redirects=yes \
    tcp-syncookies=no
/interface bridge vlan
#
add bridge=upstream disabled=no tagged=downstream,upstream untagged="" vlan-ids=99
/interface detect-internet
set detect-interface-list=none internet-interface-list=none lan-interface-list=none wan-interface-list=none
/interface l2tp-server server
set allow-fast-path=no authentication=pap,chap,mschap1,mschap2 caller-id-type=ip-address default-profile=default-encryption enabled=no keepalive-timeout=30 max-mru=1450 max-mtu=1450 max-sessions=unlimited mrru=disabled \
    one-session-per-host=no use-ipsec=no
/interface ovpn-server server
set auth=sha1,md5 cipher=blowfish128,aes128 default-profile=default enabled=no keepalive-timeout=60 mac-address=FE:7E:D8:FF:41:EC max-mtu=1500 mode=ip netmask=24 port=1194 require-client-certificate=no
/interface pptp-server server
set authentication=mschap1,mschap2 default-profile=default-encryption enabled=no keepalive-timeout=30 max-mru=1450 max-mtu=1450 mrru=disabled
/interface sstp-server server
set authentication=pap,chap,mschap1,mschap2 certificate=none default-profile=default enabled=no force-aes=no keepalive-timeout=60 max-mru=1500 max-mtu=1500 mrru=disabled pfs=no port=443 tls-version=any verify-client-certificate=no
/interface wireless align
set active-mode=yes audio-max=-20 audio-min=-100 audio-monitor=00:00:00:00:00:00 filter-mac=00:00:00:00:00:00 frame-size=300 frames-per-second=25 receive-all=no ssid-all=no
/interface wireless cap
set bridge=none caps-man-addresses="" caps-man-certificate-common-names="" caps-man-names="" certificate=none discovery-interfaces="" enabled=no interfaces="" lock-to-caps-man=no static-virtual=no
/interface wireless sniffer
set channel-time=200ms file-limit=10 file-name="" memory-limit=10 multiple-channels=no only-headers=no receive-errors=no streaming-enabled=no streaming-max-rate=0 streaming-server=0.0.0.0
/interface wireless snooper
set channel-time=200ms multiple-channels=yes receive-errors=no
/ip accounting
set account-local-traffic=no enabled=no threshold=256
/ip accounting web-access
set accessible-via-web=no address=0.0.0.0/0
/ip address
add address=192.168.1.1/24 disabled=no interface=downstream network=192.168.1.0
add address=10.254.0.5/32 disabled=no interface=loopback network=10.254.0.5
add address=10.99.99.1/24 disabled=no interface=gn-mgmt network=10.99.99.0
/ip cloud
set ddns-enabled=no ddns-update-interval=none update-time=yes
/ip cloud advanced
set use-local-address=no
/ip dhcp-client
add add-default-route=yes default-route-distance=2 dhcp-options=hostname,clientid disabled=no interface=upstream use-peer-dns=yes use-peer-ntp=yes
/ip dhcp-server config
set accounting=yes interim-update=0s store-leases-disk=5m
/ip dhcp-server lease
add address=192.168.1.200 address-lists="" client-id=1:f0:18:98:6b:f8:ce dhcp-option="" disabled=no !insert-queue-before mac-address=F0:18:98:6B:F8:CE server=server1
add address=192.168.1.145 address-lists="" client-id=1:2c:cc:44:83:23:6c dhcp-option="" disabled=no !insert-queue-before mac-address=2C:CC:44:83:23:6C server=server1
add address=192.168.1.2 address-lists="" client-id=1:0:11:32:9e:7f:63 dhcp-option="" disabled=no !insert-queue-before mac-address=00:11:32:9E:7F:63 server=server1
add address=192.168.1.246 address-lists="" client-id=1:0:90:ea:e0:88:ca dhcp-option="" disabled=no !insert-queue-before mac-address=00:90:EA:E0:88:CA server=server1
add address=192.168.1.136 address-lists="" dhcp-option="" disabled=no !insert-queue-before mac-address=48:8F:5A:99:BA:24 server=server1
add address=10.99.99.11 address-lists="" client-id=1:f0:18:98:6b:f8:ce dhcp-option="" disabled=no !insert-queue-before mac-address=F0:18:98:6B:F8:CE server=gn-mgmt-server
/ip dhcp-server network
add address=10.99.99.0/24 caps-manager="" dhcp-option="" dns-server=10.99.99.1 gateway=10.99.99.1 ntp-server=10.200.0.15 wins-server=""
add address=192.168.1.0/24 caps-manager="" dhcp-option="" dns-server=192.168.1.1 gateway=192.168.1.1 netmask=24 ntp-server="" wins-server=""
/ip dns
set allow-remote-requests=yes cache-max-ttl=1w cache-size=2048KiB max-concurrent-queries=100 max-concurrent-tcp-sessions=20 max-udp-packet-size=4096 query-server-timeout=2s query-total-timeout=10s servers=192.168.1.2,192.168.2.1 \
    use-doh-server="" verify-doh-cert=no
/ip dns static
add disabled=no forward-to=10.200.0.10 regexp=".*\\.gnint\\.net\$" ttl=1d type=FWD
add address=192.168.1.2 disabled=no name=simone.local ttl=1d
/ip firewall filter
add action=accept chain=input dst-address=83.132.47.129 dst-port=500 in-interface=upstream protocol=udp src-address=99.81.162.31 src-port=500
add action=accept chain=input dst-address=83.132.47.129 in-interface=upstream protocol=ipsec-esp src-address=52.210.66.152
add action=accept chain=input dst-address=83.132.47.129 dst-port=500 in-interface=upstream protocol=udp src-address=99.81.162.31 src-port=500
add action=accept chain=input dst-address=169.254.82.50 dst-port=179 protocol=tcp src-address=169.254.82.49
add action=accept chain=input dst-address=169.254.36.10 dst-port=179 protocol=tcp src-address=169.254.36.9
add action=accept chain=input dst-address=83.132.47.129 in-interface=upstream protocol=ipsec-esp src-address=52.210.66.152
add action=accept chain=forward in-interface=upstream src-address=172.31.0.0/16
add action=accept chain=forward dst-address=172.31.0.0/16 in-interface=downstream
add action=accept chain=forward !connection-bytes !connection-limit !connection-mark !connection-nat-state !connection-rate connection-state=established,related !connection-type !content disabled=no !dscp dst-address=10.99.99.0/24 \
    !dst-address-list !dst-address-type !dst-limit !dst-port !fragment !hotspot !icmp-options !in-bridge-port !in-bridge-port-list !in-interface !in-interface-list !ingress-priority !ipsec-policy !ipv4-options !layer7-protocol !limit \
    log=no log-prefix="" !nth !out-bridge-port !out-bridge-port-list !out-interface !out-interface-list !packet-mark !packet-size !per-connection-classifier !port !priority !protocol !psd !random !routing-mark !routing-table \
    src-address=192.168.1.0/24 !src-address-list !src-address-type !src-mac-address !src-port !tcp-flags !tcp-mss !time !tls-host !ttl
add action=drop chain=forward !connection-bytes !connection-limit !connection-mark !connection-nat-state !connection-rate connection-state="" !connection-type !content disabled=no !dscp dst-address=10.0.0.0/8 !dst-address-list \
    !dst-address-type !dst-limit !dst-port !fragment !hotspot !icmp-options !in-bridge-port !in-bridge-port-list !in-interface !in-interface-list !ingress-priority !ipsec-policy !ipv4-options !layer7-protocol !limit log=no log-prefix=\
    "" !nth !out-bridge-port !out-bridge-port-list !out-interface !out-interface-list !packet-mark !packet-size !per-connection-classifier !port !priority !protocol !psd !random !routing-mark !routing-table src-address=192.168.1.0/24 \
    !src-address-list !src-address-type !src-mac-address !src-port !tcp-flags !tcp-mss !time !tls-host !ttl
/ip firewall mangle
add action=mark-connection chain=prerouting comment=PS4 !connection-bytes !connection-limit !connection-mark !connection-nat-state !connection-rate connection-state=new !connection-type !content disabled=no !dscp dst-address=\
    192.168.1.145 !dst-address-list !dst-address-type !dst-limit !dst-port !fragment !hotspot !icmp-options !in-bridge-port !in-bridge-port-list !in-interface !in-interface-list !ingress-priority !ipsec-policy !ipv4-options \
    !layer7-protocol !limit log=no log-prefix="" new-connection-mark=PS4 !nth !out-bridge-port !out-bridge-port-list !out-interface !out-interface-list !packet-mark !packet-size passthrough=yes !per-connection-classifier !port \
    !priority !protocol !psd !random !routing-mark !routing-table !src-address !src-address-list !src-address-type !src-mac-address !src-port !tcp-flags !tcp-mss !time !tls-host !ttl
add action=mark-packet chain=prerouting !connection-bytes !connection-limit !connection-mark !connection-nat-state !connection-rate !connection-state !connection-type !content disabled=no !dscp dst-address=192.168.1.145 \
    !dst-address-list !dst-address-type !dst-limit !dst-port !fragment !hotspot !icmp-options !in-bridge-port !in-bridge-port-list !in-interface !in-interface-list !ingress-priority !ipsec-policy !ipv4-options !layer7-protocol !limit \
    log=no log-prefix="" new-packet-mark=PS4 !nth !out-bridge-port !out-bridge-port-list !out-interface !out-interface-list !packet-mark !packet-size passthrough=no !per-connection-classifier !port !priority !protocol !psd !random \
    !routing-mark !routing-table !src-address !src-address-list !src-address-type !src-mac-address !src-port !tcp-flags !tcp-mss !time !tls-host !ttl
add action=mark-connection chain=prerouting comment=DNS connection-state=new new-connection-mark=DNS passthrough=yes port=53 protocol=udp
add action=mark-packet chain=prerouting connection-mark=DNS new-packet-mark=DNS passthrough=no
add action=mark-connection chain=postrouting connection-state=new new-connection-mark=DNS passthrough=yes port=53 protocol=udp
add action=mark-packet chain=postrouting connection-mark=DNS new-packet-mark=DNS passthrough=no
add action=mark-connection chain=prerouting comment=VOIP new-connection-mark=VOIP passthrough=yes port=5060-5062,10000-10050 protocol=udp
add action=mark-packet chain=prerouting connection-mark=VOIP new-packet-mark=VOIP passthrough=no
add action=mark-connection chain=prerouting comment=QUIC connection-state=new new-connection-mark=QUIC passthrough=yes port=80,443 protocol=udp
add action=mark-packet chain=prerouting connection-mark=QUIC new-packet-mark=QUIC passthrough=no
add action=mark-connection chain=prerouting comment=UDP connection-state=new new-connection-mark=UDP passthrough=yes protocol=udp
add action=mark-packet chain=prerouting connection-mark=UDP new-packet-mark=UDP passthrough=no
add action=mark-connection chain=prerouting comment=ICMP connection-state=new new-connection-mark=ICMP passthrough=yes protocol=icmp
add action=mark-packet chain=prerouting connection-mark=ICMP new-packet-mark=ICMP passthrough=no
add action=mark-connection chain=postrouting connection-state=new new-connection-mark=ICMP passthrough=yes protocol=icmp
add action=mark-packet chain=postrouting connection-mark=ICMP new-packet-mark=ICMP passthrough=no
add action=mark-packet chain=postrouting comment=ACK new-packet-mark=ACK packet-size=0-123 passthrough=no protocol=tcp tcp-flags=ack
add action=mark-packet chain=prerouting new-packet-mark=ACK packet-size=0-123 passthrough=no protocol=tcp tcp-flags=ack
add action=mark-connection chain=prerouting comment=HTTP connection-mark=no-mark connection-state=new new-connection-mark=HTTP passthrough=yes port=80,443 protocol=tcp
add action=mark-connection chain=prerouting connection-bytes=5000000-0 connection-mark=HTTP connection-rate=2M-100M new-connection-mark=HTTP_BIG passthrough=yes protocol=tcp
add action=mark-packet chain=prerouting connection-mark=HTTP_BIG new-packet-mark=HTTP_BIG passthrough=no
add action=mark-packet chain=prerouting connection-mark=HTTP new-packet-mark=HTTP passthrough=no
add action=mark-connection chain=prerouting comment=OTHER connection-state=new new-connection-mark=POP3 passthrough=yes port=995,465,587 protocol=tcp
add action=mark-packet chain=prerouting connection-mark=POP3 new-packet-mark=OTHER passthrough=no
add action=mark-connection chain=prerouting connection-mark=no-mark new-connection-mark=OTHER passthrough=yes
add action=mark-packet chain=prerouting connection-mark=OTHER new-packet-mark=OTHER passthrough=no
/ip firewall nat
add action=accept chain=dstnat comment=AWS-VPN in-interface=upstream src-address=172.31.0.0/16 !to-addresses !to-ports
add action=src-nat chain=srcnat comment=AWS-VPN dst-address=172.31.0.0/16 to-addresses=192.168.1.0/24 !to-ports
/ip firewall service-port
set ftp disabled=no ports=21
set tftp disabled=no ports=69
set irc disabled=no ports=6667
set h323 disabled=no
set sip disabled=no ports=5060,5061 sip-direct-media=yes sip-timeout=1h
set pptp disabled=no
set udplite disabled=no
set dccp disabled=no
set sctp disabled=no
/ip hotspot service-port
set ftp disabled=no ports=21
/ip hotspot user
set [ find default=yes ] comment="counters and limits for trial users" disabled=no name=default-trial
/ip ipsec identity
add auth-method=pre-shared-key disabled=no generate-policy=no peer=vpc1
add auth-method=pre-shared-key disabled=no generate-policy=no peer=vpc2
/ip ipsec policy
set 0 disabled=no dst-address=::/0 group=default proposal=default protocol=all src-address=::/0 template=yes
add action=encrypt disabled=no dst-address=172.31.0.0/16 dst-port=any ipsec-protocols=esp level=require peer=vpc1 proposal=aws protocol=all sa-dst-address=:: sa-src-address=:: src-address=0.0.0.0/0 src-port=any tunnel=yes
add action=encrypt disabled=no dst-address=172.31.0.0/16 dst-port=any ipsec-protocols=esp level=require peer=vpc2 proposal=aws protocol=all sa-dst-address=:: sa-src-address=:: src-address=0.0.0.0/0 src-port=any tunnel=yes
add action=encrypt disabled=no dst-address=169.254.82.49/32 dst-port=any ipsec-protocols=esp level=require peer=vpc1 proposal=aws protocol=all sa-dst-address=:: sa-src-address=:: src-address=0.0.0.0/0 src-port=any tunnel=yes
add action=encrypt disabled=no dst-address=169.254.36.9/32 dst-port=any ipsec-protocols=esp level=require peer=vpc2 proposal=aws protocol=all sa-dst-address=:: sa-src-address=:: src-address=0.0.0.0/0 src-port=any tunnel=yes
/ip ipsec settings
set accounting=yes interim-update=0s xauth-use-radius=no
/ip proxy
set always-from-cache=no anonymous=no cache-administrator=webmaster cache-hit-dscp=4 cache-on-disk=no cache-path=web-proxy enabled=no max-cache-object-size=2048KiB max-cache-size=unlimited max-client-connections=600 max-fresh-time=3d \
    max-server-connections=600 parent-proxy=:: parent-proxy-port=0 port=8080 serialize-connections=no src-address=::
/ip service
set telnet address="" disabled=no port=23
set ftp address="" disabled=no port=21
set www address="" disabled=no port=80
set ssh address="" disabled=no port=22
set www-ssl address="" certificate=none disabled=yes port=443 tls-version=any
set api address="" disabled=no port=8728
set winbox address="" disabled=no port=8291
set api-ssl address="" certificate=none disabled=no port=8729 tls-version=any
/ip smb
set allow-guests=yes comment=MikrotikSMB domain=MSHOME enabled=no interfaces=all
/ip smb shares
set [ find default=yes ] comment="default share" directory=/flash/pub disabled=no max-sessions=10 name=pub
/ip smb users
set [ find default=yes ] disabled=no name=guest read-only=yes
/ip socks
set auth-method=none connection-idle-timeout=2m enabled=no max-connections=200 port=1080 version=4
/ip ssh
set allow-none-crypto=no always-allow-password-login=no forwarding-enabled=no host-key-size=2048 strong-crypto=no
/ip tftp settings
set max-block-size=4096
/ip traffic-flow
set active-flow-timeout=15s cache-entries=16k enabled=yes inactive-flow-timeout=1s interfaces=upstream
/ip traffic-flow ipfix
set bytes=yes dst-address=yes dst-address-mask=yes dst-mac-address=yes dst-port=yes first-forwarded=yes gateway=yes icmp-code=yes icmp-type=yes igmp-type=yes in-interface=yes ip-header-length=yes ip-total-length=yes ipv6-flow-label=\
    yes is-multicast=yes last-forwarded=yes nat-dst-address=yes nat-dst-port=yes nat-events=no nat-src-address=yes nat-src-port=yes out-interface=yes packets=yes protocol=yes src-address=yes src-address-mask=yes src-mac-address=yes \
    src-port=yes sys-init-time=yes tcp-ack-num=yes tcp-flags=yes tcp-seq-num=yes tcp-window-size=yes tos=yes ttl=yes udp-length=yes
/ip traffic-flow target
add disabled=no dst-address=10.99.99.11 port=2055 src-address=0.0.0.0 v9-template-refresh=20 v9-template-timeout=30m version=9
/ip upnp
set allow-disable-external-interface=no enabled=no show-dummy-rule=yes
/mpls
set dynamic-label-range=16-1048575 propagate-ttl=yes
/mpls interface
set [ find default=yes ] disabled=no interface=all mpls-mtu=1508
/mpls ldp
set distribute-for-default-route=no enabled=yes hop-limit=255 loop-detect=no lsr-id=10.254.0.5 path-vector-limit=255 transport-address=10.254.0.5 use-explicit-null=no
/mpls ldp interface
add accept-dynamic-neighbors=yes disabled=no hello-interval=5s hold-time=15s interface=sstp-out1 transport-address=10.254.0.5
/port firmware
set directory=firmware ignore-directip-modem=no
/ppp aaa
set accounting=yes interim-update=0s use-circuit-id-in-nas-port-id=no use-radius=no
/radius incoming
set accept=no port=3799
/routing bfd interface
set [ find default=yes ] disabled=no interface=all interval=0.2s min-rx=0.2s multiplier=5
/routing mme
set bidirectional-timeout=2 gateway-class=none gateway-keepalive=1m gateway-selection=no-gateway origination-interval=5s preferred-gateway=0.0.0.0 timeout=1m ttl=50
/routing ospf network
add area=world disabled=no network=192.168.1.0/24
add area=world disabled=no network=10.201.0.0/16
add area=world disabled=no network=10.99.99.0/24
add area=world comment="The quinta teltonika router has OSPF enabled" disabled=no network=192.168.2.0/24
/routing rip
set distribute-default=never garbage-timer=2m metric-bgp=1 metric-connected=1 metric-default=1 metric-ospf=1 metric-static=1 redistribute-bgp=no redistribute-connected=no redistribute-ospf=no redistribute-static=no routing-table=main \
    timeout-timer=3m update-timer=30s
/snmp
set contact="" enabled=yes engine-id="" location="" trap-community=public trap-generators=temp-exception trap-target="" trap-version=1
/system clock
set time-zone-autodetect=yes time-zone-name=Europe/Lisbon
/system clock manual
set dst-delta=+00:00 dst-end="jan/01/1970 00:00:00" dst-start="jan/01/1970 00:00:00" time-zone=+00:00
/system identity
set name="Quinta Router"
/system leds
set 0 disabled=no interface=ether1 leds=led1 type=interface-activity
set 1 disabled=no interface=ether2 leds=led2 type=interface-activity
set 2 disabled=no interface=ether3 leds=led3 type=interface-activity
set 3 disabled=no interface=ether4 leds=led4 type=interface-activity
set 4 disabled=no interface=ether5 leds=led5 type=interface-activity
/system leds settings
set all-leds-off=never
/system logging
set 0 action=memory disabled=no prefix="" topics=info
set 1 action=memory disabled=no prefix="" topics=error
set 2 action=memory disabled=no prefix="" topics=warning
set 3 action=echo disabled=no prefix="" topics=critical
add action=memory disabled=no prefix="" topics=ppp
add action=syslog disabled=no prefix="" topics=!debug
/system note
set note="" show-at-login=yes
/system ntp client
set enabled=yes primary-ntp=10.200.0.15 secondary-ntp=10.200.0.15 server-dns-names=""
/system resource irq
set 0 cpu=auto
set 1 cpu=auto
set 2 cpu=auto
set 3 cpu=auto
/system routerboard settings
set auto-upgrade=no boot-device=nand-if-fail-then-ethernet boot-protocol=bootp force-backup-booter=no protected-routerboot=disabled reformat-hold-button=20s reformat-hold-button-max=10m silent-boot=no
/system routerboard reset-button
set enabled=no hold-time=0s..1m on-event=""
/system scheduler
add disabled=no interval=1d name=cloud-backup on-event="system backup cloud upload-file action=create-and-upload password=v4psfEVwhCVeiRnRr86uqsgUMihbFAhMLnVya6nrvMuvuxYE6k4tympQ7RzF362z" policy=\
    ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon start-date=sep/13/2020 start-time=00:00:00
/system upgrade mirror
set check-interval=1d enabled=no primary-server=0.0.0.0 secondary-server=0.0.0.0 user=""
/system watchdog
set auto-send-supout=no automatic-supout=yes ping-start-after-boot=5m ping-timeout=1m watch-address=none watchdog-timer=yes
/tool bandwidth-server
set allocate-udp-ports-from=2000 authenticate=yes enabled=yes max-sessions=100
/tool e-mail
set address=0.0.0.0 from=<> port=25 start-tls=no user=""
/tool graphing
set page-refresh=300 store-every=5min
/tool mac-server
set allowed-interface-list=all
/tool mac-server mac-winbox
set allowed-interface-list=all
/tool mac-server ping
set enabled=yes
/tool romon
set enabled=no id=00:00:00:00:00:00
/tool romon port
set [ find default=yes ] cost=100 disabled=no forbid=no interface=all
/tool sms
set allowed-number="" auto-erase=no channel=0 port=none receive-enabled=no
/tool sniffer
set file-limit=1000KiB file-name="" filter-cpu="" filter-direction=any filter-interface=downstream filter-ip-address=0.0.0.0/0 filter-ip-protocol=icmp filter-ipv6-address="" filter-mac-address="" filter-mac-protocol="" \
    filter-operator-between-entries=or filter-port="" filter-size="" filter-stream=no memory-limit=100KiB memory-scroll=yes only-headers=no streaming-enabled=no streaming-server=0.0.0.0:37008
/tool traffic-generator
set latency-distribution-max=100us measure-out-of-order=yes stats-samples-to-keep=100 test-id=0
/user aaa
set accounting=yes default-group=read exclude-groups="" interim-update=0s use-radius=no
