from dsl import *


def d27_overlay_anatomy():
    d = D('27-overlay-anatomy-inside-a-host', 'Inside one host: the real interfaces behind an overlay network',
          'Names are what Docker 29.9.2 actually creates. The VXLAN device is NOT in the host namespace.')
    y = d.y0
    d.zone(0, y, 330, 330, 'container netns', 'lblue', fs=18)
    d.zone(390, y, 500, 330, 'overlay netns  /var/run/docker/netns/1-<id>', 'lpurple', fs=16)
    d.zone(950, y, 340, 330, 'host netns', 'lgray', fs=18)
    e0 = d.box(40, y + 70, 250, 70, 'eth0  10.0.1.5\nmtu 1450', 'green', fs=17)
    e1 = d.box(40, y + 210, 250, 70, 'eth1  172.18.0.3\n(docker_gwbridge)', 'blue', fs=16)
    vt = d.box(420, y + 70, 150, 70, 'veth0', 'green', fs=17)
    br = d.box(620, y + 70, 120, 70, 'br0\nbridge', 'green', fs=17)
    vx = d.box(620, y + 190, 240, 110, 'vxlan0  (the VTEP)\nid 4097, dstport 4789\nproxy l2miss l3miss', 'purple', fs=14)
    d.link(e0, vt, color='#2f9e44', heads='<->', label='veth pair', lfs=14)
    d.link(vt, br, color='#2f9e44', heads='<->')
    d.link(br, vx, 'b', 't', ta=.5, tb=.25, color='#6741d9', label='FDB lookup,\nwrap', lfs=14)
    rt = d.box(980, y + 60, 280, 60, 'routing table\npicks the interface', 'yellow', fs=15)
    ts = d.box(980, y + 150, 280, 60, 'tailscale0  mtu 1280\n(WireGuard, userspace)', 'teal', fs=15)
    gw = d.box(980, y + 240, 280, 60, 'docker_gwbridge + NAT', 'blue', fs=15)
    d.arrow([d.anchor(vx, 'r', .35), (950, y + 150), d.anchor(rt, 'l', .5)], color='#6741d9', heads='->', dashed=False, label='', lfs=12)
    d.link(rt, ts, 'b', 't', color='#0c8599')
    d.arrow([d.anchor(e1, 'r'), (350, y + 245), (350, y + 318), (925, y + 318), (925, y + 270), d.anchor(gw, 'l')], color='#1971c2', heads='->', dashed=True)
    d.text(10, y + 345, '1  app sends a frame to the MAC of 10.0.1.7   2  veth moves it across the namespace boundary   3  br0 switches by MAC; a remote MAC is behind vxlan0\n4  vxlan0 finds the remote VTEP IP, wraps (UDP 4789, VNI 4097)   5  the HOST routing table picks the egress interface   6  tailscale0 encrypts it and sends it on',
           15, '#495057')
    d.note(0, y + 410, 'No local/dev is set on vxlan0: the kernel routes the wrapped packet using the host table, so with Tailscale addresses as VTEP IPs it leaves through tailscale0.\nDashed blue = north-south traffic (to the Internet) that never touches VXLAN.',
           'lyellow', 15, w=1290, h=66)
    return d


def d28_vtep_tables():
    d = D('28-how-the-vtep-knows-where-containers-are', 'How the VTEP finds remote containers (and why ARP proxying is needed)',
          'Docker fills the kernel tables from its gossip-fed peer database; vxlan0 then answers ARP locally.')
    y = d.y0
    d.text(0, y, 'Who fills the tables', 20, '#1971c2')
    g = d.box(0, y + 40, 300, 80, 'gossip (7946):\n"10.0.1.7 is on host B"', 'purple', fs=16)
    pdb = d.box(0, y + 170, 300, 80, 'Docker peer database\n(remote peers only)', 'blue', fs=16)
    fdb = d.box(360, y + 110, 340, 70, 'FDB  (forwarding table)\nMAC 02:42:0a:00:01:07 -> VTEP 192.168.1.20', 'green', fs=14)
    nb = d.box(360, y + 200, 340, 70, 'neighbour table  (ARP answers)\n10.0.1.7 -> 02:42:0a:00:01:07', 'green', fs=14)
    d.link(g, pdb, 'b', 't', color='#6741d9')
    d.link(pdb, fdb, 'r', 'l', ta=.3, color='#2f9e44'); d.link(pdb, nb, 'r', 'l', ta=.7, color='#2f9e44')
    d.text(0, y + 285, 'A local container gets no VTEP entry: it is a port on br0.', 15, MUTED)
    d.text(780, y, 'What happens on the first packet', 20, '#e8590c')
    st = [('1  Container-1 asks (ARP):\n"who has 10.0.1.7?"', 'blue'),
          ('2  br0 passes it to vxlan0,\nwhich has the "proxy" flag', 'purple'),
          ('3  vxlan0 answers from the\nneighbour table (no broadcast\nacross the tunnel)', 'green'),
          ('4  frame to that MAC: FDB gives\nthe remote VTEP -> wrap + send', 'orange')]
    for i, (t, c) in enumerate(st):
        d.box(780, y + 40 + i * 100, 500, 84, t, c, fs=15)
    for i in range(3):
        d.arrow([(1030, y + 124 + i * 100), (1030, y + 140 + i * 100)], heads='->')
    d.note(0, y + 470, 'Without ARP proxying, Container-1\'s broadcast ARP stops at the L3 boundary between hosts: nobody answers and the failure is silent.\nl2miss / l3miss ask the kernel to report lookups it could not answer, so the driver can react.',
           'lred', 15, w=1290, h=70)
    return d


def d29_packet_journey():
    d = D('29-packet-journey-container-to-container', 'One request, across two hosts: Container-1 -> Container-2',
          'curl http://10.0.1.7/api/data from 10.0.1.5. The reply takes the reverse path.')
    y = d.y0
    d.zone(-10, y - 6, 1310, 224, 'Host A  (192.168.1.10 / Tailscale 100.x)', 'lblue', dashed=False, fs=18)
    top = [('1 Container-1\neth0', 'green', 'app sends; frame dst MAC\n= Container-2'), ('2 veth pair', 'green', 'crosses from the\ncontainer namespace'),
           ('3 br0', 'green', 'MAC not on a local\nport -> vxlan0'), ('4 vxlan0 (VTEP)', 'purple', 'FDB: MAC -> VTEP IP;\nwrap in UDP 4789 + VNI'),
           ('5 host routing', 'teal', 'route -> tailscale0 ->\nWireGuard -> UDP out')]
    ids = []
    for i, (t, c, cap) in enumerate(top):
        x = i * 262
        ids.append(d.box(x, y + 50, 220, 80, t, c, fs=16))
        d.text(x + 6, y + 142, cap, 14, '#495057')
    for a, b in zip(ids, ids[1:]):
        d.link(a, b, color='#2f9e44')
    ya = y + 300
    d.zone(-10, ya - 6, 1310, 224, 'Host B  (192.168.1.20 / Tailscale 100.x)', 'lgreen', dashed=False, fs=18)
    bot = [('10 Container-2\neth0', 'green', 'nginx receives GET;\nreply goes back'), ('9 veth pair', 'green', 'into the container\nnamespace'),
           ('8 br0', 'green', 'MAC is a local port\n(the veth)'), ('7 vxlan0 (VTEP)', 'purple', 'VNI known? yes ->\nunwrap the inner frame'),
           ('6 host NIC', 'teal', 'decrypt; UDP 4789\narrives')]
    ids2 = []
    for i, (t, c, cap) in enumerate(bot):
        x = i * 262
        ids2.append(d.box(x, ya + 50, 220, 80, t, c, fs=16))
        d.text(x + 6, ya + 142, cap, 14, '#495057')
    for a, b in zip(ids2, ids2[1:]):
        d.link(b, a, 'l', 'r', color='#2f9e44')
    d.arrow([(4 * 262 + 110, y + 190), (4 * 262 + 110, ya + 50)], color='#e8590c', heads='->', sw=3)
    d.text(4 * 262 + 124, y + 232, 'underlay: tunnel across the Internet\n(direct, or relayed via DERP)', 14, '#e8590c')
    d.note(0, ya + 240, 'The routers and NATs in between see only UDP between the two hosts (and, with Tailscale, only encrypted WireGuard UDP). They never see 10.0.1.x.',
           'lyellow', 15, w=1290, h=50)
    return d


def d30_same_vs_cross():
    d = D('30-same-host-vs-cross-host-overlay', 'Same host skips the tunnel; different hosts use it',
          'Tested: 20 pings between two replicas on one node left vxlan0 at tx_packets 0 -> 0, while br0 carried them.')
    y = d.y0
    d.zone(0, y, 1290, 150, 'Same host', 'lgreen', dashed=False, fs=19)
    chain = [('Container-1', 'green'), ('veth', 'lgray'), ('br0', 'green'), ('veth', 'lgray'), ('Container-2', 'green')]
    ids = [d.box(40 + i * 245, y + 56, 190, 60, t, c, fs=16) for i, (t, c) in enumerate(chain)]
    for a, b in zip(ids, ids[1:]): d.link(a, b, color='#2f9e44')
    d.text(40, y + 124, 'no VXLAN, no UDP 4789, no encapsulation overhead', 15, '#2f9e44')
    y2 = y + 190
    d.zone(0, y2, 1290, 340, 'Different hosts', 'lblue', dashed=False, fs=19)
    A = [('Container-1', 'green'), ('br0', 'green'), ('vxlan0\nwrap', 'purple'), ('host NIC', 'teal')]
    B = [('host NIC', 'teal'), ('vxlan0\nunwrap', 'purple'), ('br0', 'green'), ('Container-2', 'green')]
    ida = [d.box(40 + i * 300, y2 + 60, 200, 66, t, c, fs=16) for i, (t, c) in enumerate(A)]
    for a, b in zip(ida, ida[1:]): d.link(a, b, color='#1971c2')
    idb = [d.box(40 + (3 - i) * 300, y2 + 200, 200, 66, t, c, fs=16) for i, (t, c) in enumerate(B)]
    for a, b in zip(idb, idb[1:]): d.link(a, b, 'l', 'r', color='#1971c2')
    d.arrow([(940, y2 + 126), (940, y2 + 200)], color='#e8590c', heads='->', sw=3, label='underlay', lfs=15, lpos=(956, y2 + 150))
    d.text(40, y2 + 284, 'adds ~50 bytes per packet + CPU for wrap/unwrap. Placing chatty replicas on one node (placement constraints) avoids it; Swarm does not do this for you.', 15, '#495057')
    return d


def d31_vni():
    d = D('31-vni-keeps-overlays-apart', 'The VNI keeps overlay networks apart on the same wire',
          'Two overlays share the same hosts, the same UDP 4789 and the same physical links.')
    y = d.y0
    pk = d.box(0, y + 150, 280, 90, 'UDP 4789 packet\narrives at host B', 'orange', fs=17)
    vt = d.box(380, y + 150, 280, 90, 'VTEP reads the VNI\nfrom the VXLAN header', 'purple', fs=17)
    d.link(pk, vt)
    br = [('VNI 4097', 'overlay "frontend"', 'deliver to frontend br0', 'green'),
          ('VNI 4098', 'overlay "backend"', 'deliver to backend br0', 'green'),
          ('VNI 9999', 'no such network here', 'discard', 'red')]
    for i, (v, n, act, c) in enumerate(br):
        yy = y + i * 150
        b = d.box(800, yy, 480, 120, f'{v}  =  {n}\n->  {act}', c, fs=17)
        d.link(vt, b, 'r', 'l', color=C[c][1], tb=.5)
    d.note(0, y + 470, 'Numbers from Docker 29.9.2: ingress = 4096; user overlays 4097, 4098, ... (VNIs are 24-bit, so ~16 million are possible).\nThis check is why a "frontend" container cannot see "backend" traffic even though both ride the same UDP channel.',
           'lyellow', 15, w=1290, h=70)
    return d


ALL = [d27_overlay_anatomy, d28_vtep_tables, d29_packet_journey, d30_same_vs_cross, d31_vni]
