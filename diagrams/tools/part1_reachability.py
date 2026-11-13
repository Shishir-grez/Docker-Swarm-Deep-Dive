from dsl import *


def d01_topologies():
    d = D('01-network-topologies', 'Three ways to wire machines together',
          'Docker Swarm needs the third one: a mesh')
    y = d.y0
    for i, (ttl, col) in enumerate([('Client - Server', 'lgray'), ('Hub & spoke', 'lgray'), ('Mesh', 'lgreen')]):
        d.zone(i * 420, y, 380, 350, ttl, col, fs=22, dashed=False)
    # client-server
    px = 0
    cl = [d.box(px + 24, y + 70 + i * 85, 120, 52, f'client {i+1}', 'blue') for i in range(3)]
    sv = d.box(px + 250, y + 150, 110, 70, 'server', 'gray')
    for i, c in enumerate(cl):
        d.link(c, sv, tb=[0.2, 0.5, 0.8][i], heads='->', color='#1971c2')
    # hub & spoke
    px = 420
    hub = d.box(px + 140, y + 160, 100, 60, 'hub', 'gray')
    sp = [d.box(px + 135, y + 60, 110, 46, 'spoke', 'blue'),
          d.box(px + 135, y + 275, 110, 46, 'spoke', 'blue'),
          d.box(px + 14, y + 167, 100, 46, 'spoke', 'blue'),
          d.box(px + 266, y + 167, 100, 46, 'spoke', 'blue')]
    d.link(sp[0], hub, 'b', 't', heads='<->')
    d.link(sp[1], hub, 't', 'b', heads='<->')
    d.link(sp[2], hub, 'r', 'l', heads='<->')
    d.link(sp[3], hub, 'l', 'r', heads='<->')
    # mesh
    px = 840
    A = d.box(px + 40, y + 70, 100, 50, 'node A', 'green')
    B = d.box(px + 240, y + 70, 100, 50, 'node B', 'green')
    Cc = d.box(px + 40, y + 250, 100, 50, 'node C', 'green')
    Dd = d.box(px + 240, y + 250, 100, 50, 'node D', 'green')
    d.link(A, B, heads='<->'); d.link(Cc, Dd, heads='<->')
    d.link(A, Cc, 'b', 't', heads='<->'); d.link(B, Dd, 'b', 't', heads='<->')
    d.arrow([d.anchor(A, 'b', .85), d.anchor(Dd, 't', .15)], heads='<->')
    d.arrow([d.anchor(B, 'b', .15), d.anchor(Cc, 't', .85)], heads='<->')
    cy = y + 365
    d.text(10, cy, 'Clients talk to one\ncentral server.', 17, MUTED)
    d.text(430, cy, 'Spokes only reach each\nother through the hub.', 17, MUTED)
    d.text(850, cy, 'EVERY node reaches EVERY\nother node directly.', 17, '#2f9e44')
    d.note(0, cy + 70, 'Golden rule of Swarm networking: each device must be able to send packets directly to every other device (= they must be "routable").',
           'lyellow', 17, w=1260, h=54)
    return d


def d02_hops():
    d = D('02-packet-path-hops', 'A packet crossing the Internet is a series of hops',
          'Each arrow is one hop. traceroute / tracert shows them.')
    y = d.y0 + 50
    d.zone(-14, y - 46, 360, 200, 'Your home network', 'lblue')
    d.zone(364, y - 46, 560, 200, 'The open Internet', 'lgray')
    d.zone(936, y - 46, 366, 200, "Friend's home network", 'lblue')
    names = [("Your PC", '192.168.1.10', 'blue'), ("Home router", '192.168.1.1', 'yellow'),
             ("ISP gateway", '100.72.0.1', 'orange'), ("Core routers", '...', 'gray'),
             ("Friend's ISP", '...', 'orange'), ("Friend's router", '192.168.x.1', 'yellow'),
             ("Friend's PC", '192.168.x.20', 'blue')]
    ids = []
    for i, (n, a, col) in enumerate(names):
        x = i * 190 + (6 if i < 2 else 0) + (14 if i >= 5 else 0)
        ids.append(d.box(x, y, 146, 70, n, col, fs=17))
        d.ctext(x + 73, y + 82, a, 14, '#495057', MONO)
    for a, b in zip(ids, ids[1:]):
        d.link(a, b, heads='->')
    d.ctext(1 * 190 + 79, y + 104, '(does NAT)', 14, '#e67700')
    d.ctext(5 * 190 + 93, y + 104, '(does NAT)', 14, '#e67700')
    d.arrow([(2 * 190 + 73, y + 128), (2 * 190 + 73, y + 200)], color='#e8590c', heads='->')
    d.note(250, y + 206, "hop 3 is inside 100.64.0.0/10 =\nthe ISP's carrier-grade NAT (CGNAT).\nThe ISP shares one public IP\nbetween many customers.",
           'lorange', 16, w=370, h=104)
    d.note(660, y + 206, 'At EVERY hop the Layer-2 header (MAC addresses) is rebuilt.\nThe Layer-3 header (IP addresses) stays the same\n... unless a NAT rewrites it.\nThe packet can return by a different path.',
           'lyellow', 16, w=640, h=104)
    return d


def d03_osi():
    d = D('03-layers-and-encapsulation', 'Layers: each layer wraps the one above in its own header',
          'Left: the 7-layer model. Right: what a packet actually looks like on the wire.')
    y = d.y0
    layers = [('7  Application', 'HTTP, DNS, SSH', 'lgray'), ('6  Presentation', 'TLS, encodings', 'lgray'),
              ('5  Session', 'connection management', 'lgray'),
              ('4  Transport', 'TCP / UDP + PORTS', 'blue'), ('3  Network', 'IP ADDRESSES + routing', 'yellow'),
              ('2  Data link', 'MAC addresses, one hop', 'green'), ('1  Physical', 'bits on a wire / radio', 'purple')]
    ids = {}
    for i, (n, ex, col) in enumerate(layers):
        ids[n[0]] = d.box(0, y + i * 66, 330, 56, f'{n}\n{ex}', col, fs=16)
    # nested envelope on the right
    ex = 470
    eth = d.box(ex, y + 20, 700, 440, '', 'lgreen', sw=3)
    d.text(ex + 18, y + 28, 'Ethernet frame   [ dst MAC | src MAC | type ]   <- Layer 2', 18, '#2f9e44')
    ip = d.box(ex + 40, y + 90, 620, 330, '', 'lyellow', sw=3)
    d.text(ex + 58, y + 98, 'IP packet   [ src IP | dst IP | TTL ]   <- Layer 3', 18, '#e67700')
    tcp = d.box(ex + 80, y + 160, 540, 220, '', 'lblue', sw=3)
    d.text(ex + 98, y + 168, 'TCP / UDP segment   [ src port | dst port ]   <- Layer 4', 18, '#1971c2')
    d.box(ex + 120, y + 225, 460, 120, 'your data\nGET /index.html HTTP/1.1', 'white', fs=20)
    d.arrow([d.anchor(ids['2'], 'r'), (ex, y + 410)], color='#2f9e44', dashed=True, heads='->')
    d.arrow([d.anchor(ids['3'], 'r'), (ex + 40, y + 340)], color='#e67700', dashed=True, heads='->')
    d.arrow([d.anchor(ids['4'], 'r'), (ex + 80, y + 270)], color='#1971c2', dashed=True, heads='->')
    d.note(0, y + 480, 'Per hop: the Layer-2 header is stripped and rebuilt with new MACs. Layers 3 and 4 stay intact - unless NAT rewrites them.',
           'lyellow', 17, w=1170, h=52)
    return d


def d04_local_vs_remote():
    d = D('04-local-or-remote-delivery', 'How your PC decides: deliver directly, or hand to the router?',
          'Uses the subnet mask. ARP finds the MAC address of the NEXT hop.')
    y = d.y0
    st = d.box(430, y, 330, 60, 'Packet for destination IP', 'blue')
    q = d.box(380, y + 105, 430, 130, '(my IP AND mask)\n= (dest IP AND mask) ?', 'yellow', shape='diamond', fs=18)
    d.link(st, q, 'b', 't')
    # yes branch
    a1 = d.box(40, y + 300, 330, 80, 'LOCAL: ARP for the\ndestination\'s MAC', 'green')
    a2 = d.box(40, y + 440, 330, 80, 'Send the frame straight\nto it (no router)', 'green')
    d.link(q, a1, 'l', 't', via=[(205, y + 170)], label='same subnet', lpos=(215, y + 130), color='#2f9e44')
    d.link(a1, a2, 'b', 't', color='#2f9e44')
    # no branch
    b1 = d.box(820, y + 300, 380, 80, 'REMOTE: use default gateway\n(0.0.0.0/0 via 192.168.1.1)', 'orange')
    b2 = d.box(820, y + 440, 380, 80, 'ARP for the ROUTER\'s MAC\n(not the destination\'s!)', 'orange')
    b3 = d.box(820, y + 580, 380, 80, 'Router forwards to\nits next hop', 'orange')
    d.link(q, b1, 'r', 't', via=[(1010, y + 170)], label='different subnet', lpos=(850, y + 130), color='#e8590c')
    d.link(b1, b2, 'b', 't', color='#e8590c'); d.link(b2, b3, 'b', 't', color='#e8590c')
    d.note(40, y + 600, 'Example: you are 192.168.1.10 / 255.255.255.0\n192.168.1.50  -> same network  -> direct\n192.168.2.50  -> other network -> via gateway',
           'lgray', 16, w=520, h=100)
    return d


def d05_headers_per_hop():
    d = D('05-what-changes-per-hop', 'What changes at each hop, and what does not',
          'IP addresses = where it is going (stays). MAC addresses = who gets it next (changes).')
    y = d.y0 + 10
    hops = [('Hop 1:  PC -> home router', 'PC', 'Router', '192.168.1.10', '8.8.8.8', 'lgreen'),
            ('Hop 2:  home router -> ISP', 'Router', 'ISP', '203.45.67.89', '8.8.8.8', 'lyellow'),
            ('Hop 3:  ISP -> next router', 'ISP', 'Core', '203.45.67.89', '8.8.8.8', 'lgray')]
    for i, (t, a, b, sip, dip, col) in enumerate(hops):
        x = i * 430
        d.zone(x, y, 400, 330, t, col, dashed=False, fs=20)
        d.box(x + 24, y + 56, 352, 100, f'Ethernet (Layer 2)\nsrc MAC: {a}   dst MAC: {b}', 'orange', fs=17)
        ipcol = 'yellow' if i >= 1 else 'green'
        d.box(x + 24, y + 176, 352, 100, f'IP (Layer 3)\nsrc IP: {sip}\ndst IP: {dip}', ipcol, fs=17)
        d.text(x + 24, y + 292, 'MACs rewritten at every hop' if i == 0 else ('NAT rewrote the source IP here' if i == 1 else 'IPs unchanged from here'), 15, '#495057')
    d.note(0, y + 360, 'Home router = NAT: source 192.168.1.10 becomes the public 203.45.67.89 (and the source port is translated too). Without NAT the IP header would stay identical at every hop.',
           'lyellow', 16, w=1260, h=56)
    return d


def d06_nat():
    d = D('06-nat-translation', 'NAT: sharing one public IP, and why unsolicited packets die',
          'The router rewrites the source on the way out and remembers the mapping to undo it on the way back.')
    y = d.y0
    d.zone(0, y, 340, 310, 'Home LAN (private)', 'lblue')
    d.box(24, y + 60, 292, 56, 'PC  192.168.1.10:54321', 'blue', fs=16)
    d.box(24, y + 140, 292, 56, 'Phone  192.168.1.11:49152', 'blue', fs=16)
    d.box(24, y + 220, 292, 56, 'TV  192.168.1.13', 'blue', fs=16)
    d.box(430, y + 30, 400, 270, '', 'yellow', sw=3)
    d.text(450, y + 42, 'Router (NAT)', 20, '#e67700')
    d.text(450, y + 74, 'public IP 203.45.67.89', 16, '#495057')
    d.text(450, y + 118, 'translation table', 16, '#495057')
    d.text(450, y + 146, '192.168.1.10:54321 <-> :61234\n192.168.1.11:49152 <-> :61236\n(+ remote peer, state, timeout)', 15, INK, MONO)
    d.zone(1090, y, 330, 310, 'Internet (public)', 'lgray')
    d.box(1112, y + 70, 286, 70, 'Google\n142.250.80.46:443', 'gray', fs=16)
    d.box(1112, y + 200, 286, 70, 'Stranger 1.2.3.4\nsends to 203.45.67.89:5000', 'red', fs=15)
    # LAN <-> router
    d.arrow([(316, y + 88), (430, y + 88)], color='#1971c2', label='1', lpos=(366, y + 58))
    d.arrow([(430, y + 130), (316, y + 130)], color='#2f9e44', label='4', lpos=(366, y + 138))
    # router <-> internet
    d.arrow([(830, y + 88), (1112, y + 88)], color='#e67700', label='2  src is now 203.45.67.89:61234', lpos=(845, y + 56), lfs=14)
    d.arrow([(1112, y + 122), (830, y + 122)], color='#2f9e44', label='3  reply to 203.45.67.89:61234', lpos=(850, y + 130), lfs=14)
    d.arrow([(1112, y + 235), (860, y + 235)], color='#e03131', label='no table entry for :5000', lpos=(870, y + 203), lfs=14)
    d.x(846, y + 235, 14)
    d.note(0, y + 340, '1 PC sends   2 router swaps in its public IP + a fresh port, records the pair   3 reply arrives at that port   4 router swaps the PC back in.\nA packet for a port with NO entry (red) has no owner inside, so it is dropped.',
           'lgray', 16, w=1420, h=84)
    return d


def d07_nat_types():
    d = D('07-nat-behaviours', 'Four NAT behaviours decide whether two PCs can reach each other directly',
          'Inside 192.168.1.10:5000 has sent a packet to 8.8.8.8:53 and got public mapping 203.45.67.89:61234')
    y = d.y0
    cells = [
        ('Full cone', 'green', 'Anyone on the Internet can send to\n203.45.67.89:61234 and it is forwarded.', 'easiest to traverse'),
        ('Restricted cone', 'green', 'Only the IP we contacted (8.8.8.8, any port)\nmay send back. 1.1.1.1 is blocked.', 'easy'),
        ('Port-restricted cone', 'yellow', 'Only 8.8.8.8 : 53 exactly may send back.\n8.8.8.8:80 and 1.1.1.1:53 are blocked.', 'works with hole punching'),
        ('Symmetric', 'red', 'A DIFFERENT public port per destination:\n8.8.8.8 -> :61234, 1.1.1.1 -> :61235.\nA peer cannot guess it.', 'hole punching fails -> relay (DERP)'),
    ]
    for i, (t, col, body, verdict) in enumerate(cells):
        x = (i % 2) * 640; yy = y + (i // 2) * 250
        d.box(x, yy, 600, 220, '', 'l' + col, sw=2)
        d.text(x + 20, yy + 14, t, 24, C[col][1])
        d.text(x + 20, yy + 62, body, 18, INK)
        d.box(x + 20, yy + 160, 560, 44, verdict, col, fs=17)
    return d


def d08_cgnat():
    d = D('08-cgnat-double-nat', 'CGNAT: the ISP puts YOU behind its NAT too',
          'Two NATs in a row. You control the first one. The second belongs to the ISP.')
    y = d.y0 + 20
    pc = d.box(0, y, 170, 70, 'Your PC\n192.168.1.10', 'blue', fs=17)
    r1 = d.box(260, y, 190, 70, 'Your router\nNAT #1', 'yellow', fs=17)
    isp = d.box(580, y, 230, 70, 'ISP gateway\nNAT #2 (CGNAT)', 'orange', fs=17)
    net = d.box(960, y, 190, 70, 'Internet', 'gray', fs=17)
    d.link(pc, r1); d.link(r1, isp); d.link(isp, net)
    d.text(196, y + 8, 'LAN', 15, MUTED)
    d.ctext(515, y + 78, 'WAN: 100.64.x.x', 15, '#e67700', MONO)
    d.ctext(695, y - 44, 'shared public IP 203.45.67.89', 15, '#e8590c', MONO)
    n1 = d.box(560, y + 190, 130, 50, 'neighbour 1', 'lgray', fs=15)
    n2 = d.box(710, y + 190, 130, 50, 'neighbour 2', 'lgray', fs=15)
    d.arrow([d.anchor(n1, 't'), d.anchor(isp, 'b', .3)], heads='->', color=MUTED)
    d.arrow([d.anchor(n2, 't'), d.anchor(isp, 'b', .7)], heads='->', color=MUTED)
    d.arrow([(960, y + 130), (810, y + 130)], color='#e03131', label='inbound packet', lpos=(850, y + 98), lfs=15)
    d.x(800, y + 130, 14)
    d.note(0, y + 280, 'Port forwarding on YOUR router (NAT #1) is useless: the packet is dropped at the ISP\'s NAT (#2) before it reaches you.\nSo friends behind CGNAT must connect OUTWARD: to a relay, or to each other at the same moment (hole punching).',
           'lred', 17, w=1180, h=84)
    d.note(0, y + 390, 'Spot it: hops in your traceroute (and your router\'s WAN address) inside 100.64.0.0/10. Tailscale ALSO uses 100.64.0.0/10 for its own addresses;\nby default its Linux client drops incoming CGNAT-range packets that are not from Tailscale, so the two do not collide.',
           'lyellow', 16, w=1180, h=76)
    return d


ALL = [d01_topologies, d02_hops, d03_osi, d04_local_vs_remote, d05_headers_per_hop, d06_nat, d07_nat_types, d08_cgnat]
