from dsl import *


def d09_port_forwarding():
    d = D('09-port-forwarding', 'Port forwarding: a manual hole in your own NAT',
          'Works only if YOU control the outermost NAT and have a reachable public IP.')
    y = d.y0 + 10
    d.zone(560, y - 6, 700, 210, 'Home network', 'lblue')
    cl = d.box(0, y + 60, 230, 76, 'External client\n1.2.3.4', 'gray')
    rt = d.box(600, y + 40, 280, 120, 'Router (NAT)\nrule: public :80\n-> 192.168.1.10:80', 'yellow', fs=17)
    sv = d.box(1010, y + 60, 230, 76, 'Server\n192.168.1.10:80', 'blue')
    d.arrow([(230, y + 98), (600, y + 98)], color='#1971c2', label='connect to 203.45.67.89:80', lpos=(260, y + 64))
    d.arrow([(880, y + 98), (1010, y + 98)], color='#e67700', label='dst rewritten', lpos=(888, y + 64), lfs=14)
    lim = [('One public port\n= ONE inside device', 'lyellow'), ('Exposes that service to\nevery scanner on the Internet', 'lred'),
           ('Public IP changes (dynamic)\n-> you need dynamic DNS', 'lyellow'), ('Useless behind CGNAT /\ndouble NAT', 'lred')]
    d.text(0, y + 240, 'Limits:', 20, '#495057')
    for i, (t, c) in enumerate(lim):
        d.box(i * 320, y + 280, 300, 90, t, c, fs=16)
    return d


def d10_stun_coordination():
    d = D('10-stun-and-coordination', 'Step 1-2 of connecting: find your public address, then introduce the peers',
          'STUN answers "what do I look like from outside?"; the coordination server swaps addresses + keys.')
    y = d.y0
    d.text(0, y, 'Step 1 - ask a STUN server (it sits on the public Internet and sees the post-NAT source)', 19, '#1971c2')
    a = d.box(0, y + 50, 250, 80, 'Device A\n192.168.1.5', 'blue')
    nat = d.box(380, y + 60, 130, 60, 'NAT', 'yellow')
    st = d.box(790, y + 50, 260, 80, 'STUN server\n(public IP)', 'gray')
    d.arrow([(250, y + 78), (380, y + 78)], color='#1971c2')
    d.arrow([(510, y + 78), (790, y + 78)], color='#1971c2', label='UDP: "what is my address?"', lpos=(540, y + 44), lfs=15)
    d.arrow([(790, y + 108), (510, y + 108)], color='#2f9e44', label='"you are 203.45.67.89:41234"', lpos=(530, y + 114), lfs=15)
    d.arrow([(380, y + 108), (250, y + 108)], color='#2f9e44')
    y2 = y + 230
    d.text(0, y2, 'Step 2 - share it through the coordination (control) server over HTTPS 443', 19, '#6741d9')
    a2 = d.box(0, y2 + 80, 230, 80, 'Device A\nkey abc12', 'blue')
    cs = d.box(470, y2 + 60, 300, 120, 'Coordination server\n(never sees your traffic)', 'purple')
    b2 = d.box(1010, y2 + 80, 230, 80, 'Device B\nkey def45', 'blue')
    d.arrow([(230, y2 + 98), (470, y2 + 98)], color='#1971c2', label='A: my endpoints + key', lpos=(244, y2 + 64), lfs=14)
    d.arrow([(470, y2 + 142), (230, y2 + 142)], color='#6741d9', label='B is at 198.23.45.123:38472', lpos=(244, y2 + 148), lfs=14)
    d.arrow([(1010, y2 + 98), (770, y2 + 98)], color='#1971c2', label='B: my endpoints + key', lpos=(790, y2 + 64), lfs=14)
    d.arrow([(770, y2 + 142), (1010, y2 + 142)], color='#6741d9', label='A is at 203.45.67.89:41234', lpos=(785, y2 + 148), lfs=14)
    return d


def d11_hole_punching():
    d = D('11-hole-punching', 'UDP hole punching: both sides send first, so both NATs open a door',
          'Each NAT only admits replies to something its own side sent out.')
    y = d.y0 + 10
    xs = [110, 450, 850, 1190]
    names = ['Device A', 'Router A (NAT)', 'Router B (NAT)', 'Device B']
    cols = ['blue', 'yellow', 'yellow', 'blue']
    for x, n, c in zip(xs, names, cols):
        d.box(x - 85, y, 170, 52, n, c, fs=16)
        d.arrow([(x, y + 52), (x, y + 560)], color='#adb5bd', heads='--', dashed=True, sw=1.5)
    def msg(y_, x1, x2, t, col, lx=None, drop=False):
        d.arrow([(x1, y_), (x2, y_)], color=col, label=t, lfs=14, lpos=lx)
        if drop: d.x(x2 - 10, y_, 13)
    # step 1
    msg(y + 110, xs[0], xs[1], '1  ping to B\'s public endpoint', '#1971c2', lx=(xs[0] + 8, y + 80))
    d.note(xs[1] - 150, y + 130, 'creates mapping: A may now\nreceive from B\'s address', 'lyellow', 14, w=300, h=54)
    msg(y + 220, xs[1], xs[2], '', '#1971c2')
    d.ctext((xs[1] + xs[2]) / 2, y + 190, 'forwarded to B\'s router ...', 14, '#1971c2')
    d.x(xs[2] - 10, y + 220, 13)
    d.note(xs[2] - 150, y + 235, 'dropped: no mapping yet\n(B has not sent to A)', 'lred', 14, w=300, h=54)
    # step 2
    msg(y + 340, xs[3], xs[2], '2  ping to A\'s public endpoint', '#e8590c', lx=(xs[2] + 20, y + 310))
    d.note(xs[2] + 24, y + 355, 'creates mapping: B may now\nreceive from A\'s address', 'lyellow', 14, w=290, h=54)
    msg(y + 420, xs[2], xs[1], 'passes: matches A\'s mapping', '#e8590c', lx=(xs[1] + 100, y + 390))
    msg(y + 460, xs[1], xs[0], 'delivered to A', '#e8590c', lx=(xs[0] + 90, y + 430))
    # step 3
    msg(y + 510, xs[0], xs[3], '3  pong / data: both NATs now have a door - direct path', '#2f9e44', lx=(xs[0] + 250, y + 478))
    d.note(0, y + 590, 'In Tailscale the "ping/pong" are small "disco" messages sent to every candidate endpoint, and a CallMeMaybe message (relayed via DERP) makes the peer start probing too. WireGuard traffic switches to the first path that answers.',
           'lgray', 15, w=1290, h=60)
    return d


def d12_lifecycle():
    d = D('12-tailscale-connection-lifecycle', 'How a Tailscale connection really starts: relay first, then upgrade',
          'Not "try direct, then fall back": DERP is the bootstrap path while direct paths are probed.')
    y = d.y0 + 10
    steps = [('1  Control plane', 'netmap: peer\'s key,\nendpoints, home DERP', 'purple'),
             ('2  Talk via DERP', 'first packets flow at once\nthrough the peer\'s relay', 'orange'),
             ('3  Probe directly', 'CallMeMaybe (via DERP) +\ndisco Pings to each candidate:\nSTUN, LAN, IPv6, port-mapped', 'blue'),
             ('4  Switch', 'first Pong back =\nuse that direct UDP path', 'green'),
             ('5  Keep it alive', 'ping best path every 3 s while active;\nstop after 45 s idle', 'teal')]
    ids = []
    for i, (t, b, c) in enumerate(steps):
        ids.append(d.box(i * 262, y, 240, 160, f'{t}\n\n{b}', c, fs=15))
    for a, b in zip(ids, ids[1:]):
        d.link(a, b)
    ly = y + 240
    d.text(0, ly - 40, 'Which path carries the packets over time:', 18, '#495057')
    d.box(0, ly, 1290, 44, '', 'lgray', sw=1)
    d.box(0, ly, 560, 44, 'via DERP relay (bootstrap)', 'orange', fs=16)
    d.box(560, ly, 730, 44, 'DERP stays available as the fallback', 'lorange', fs=16, dashed=True)
    d.box(560, ly + 70, 730, 44, 'direct UDP (peer to peer)', 'green', fs=16)
    d.arrow([(560, ly + 44), (560, ly + 70)], color='#2f9e44')
    d.text(0, ly + 80, 'time ------------>', 16, MUTED)
    d.note(0, ly + 150, 'Every minute Tailscale tries again for a better direct path. If NO path ever answers (hard NAT on both sides, UDP blocked),\ntraffic simply stays on DERP: slower, but it works. `tailscale status` shows "active; direct <addr>" or "active; relay <region>".',
           'lyellow', 16, w=1290, h=76)
    return d


def d13_derp():
    d = D('13-derp-relay', 'DERP: a relay that forwards encrypted packets by public key',
          'Both devices connect OUTWARD over HTTPS (TCP 443), so no inbound hole is needed.')
    y = d.y0 + 30
    d.ctext(645, y - 4, 'relays also talk to each other', 14, '#e8590c')
    a = d.box(0, y + 50, 200, 90, 'Device A\n(behind NAT)', 'blue')
    b = d.box(1090, y + 50, 200, 90, 'Device B\n(behind NAT)', 'blue')
    r1 = d.box(340, y + 30, 270, 100, 'DERP server\nA\'s nearest ("home")', 'orange')
    r2 = d.box(680, y + 30, 270, 100, 'DERP server\nB\'s nearest ("home")', 'orange')
    d.link(a, r1, 'r', 'l', color='#1971c2')
    d.link(b, r2, 'l', 'r', color='#1971c2')
    d.link(r1, r2, 'r', 'l', heads='<->', color='#e8590c')
    d.text(0, y + 150, 'outbound HTTPS 443,\nupgraded to DERP', 14, '#1971c2')
    d.text(1010, y + 150, 'outbound HTTPS 443,\nupgraded to DERP', 14, '#1971c2')
    d.zone(0, y + 220, 1290, 150, '', 'lgray', dashed=False)
    d.text(18, y + 230, 'What travels  A -> relay -> B:', 17, '#495057')
    d.box(30, y + 270, 190, 70, 'dst: B\'s public key', 'yellow', fs=15)
    d.box(240, y + 270, 560, 70, 'WireGuard ciphertext (encrypted with B\'s key)', 'purple', fs=16)
    d.note(830, y + 260, 'The relay reads only the destination key.\nIt cannot decrypt the payload.', 'lgreen', 15, w=440, h=90)
    d.note(0, y + 400, 'DERP is also the bootstrap path (traffic starts here while direct paths are probed) and the fallback when direct fails.\nTo a firewall it looks like ordinary HTTPS (an HTTP Upgrade, which "looks exactly like WebSockets" per Tailscale\'s source).',
           'lyellow', 15, w=1290, h=74)
    return d


def d14_userspace_vs_tun():
    d = D('14-tailscale-packet-path-tun', 'Where Tailscale\'s packets go: the TUN device and userspace WireGuard',
          'Swarm needs the normal mode, because it needs a real tailscale0 interface.')
    y = d.y0
    d.zone(0, y, 1290, 270, 'Normal mode (what this guide uses)', 'lgreen', dashed=False, fs=20)
    d.zone(300, y + 40, 770, 160, 'kernel', 'lgray', fs=15)
    d.zone(470, y + 60, 230, 125, '', 'lpurple', fs=15)
    app = d.box(18, y + 90, 150, 70, 'App /\ndockerd', 'blue', fs=16)
    k1 = d.box(318, y + 92, 130, 66, 'TCP/IP stack\n+ routes', 'gray', fs=15)
    tun = d.box(484, y + 78, 200, 40, 'tailscale0 (TUN)', 'teal', fs=15)
    d.text(484, y + 127, 'userspace: tailscaled\nWireGuard encrypts here', 14, '#6741d9')
    sock = d.box(720, y + 92, 130, 66, 'UDP socket', 'purple', fs=15)
    nic = d.box(880, y + 92, 170, 66, 'kernel UDP/IP\n-> NIC', 'gray', fs=15)
    d.link(app, k1); d.link(k1, tun, 'r', 'l', ta=.4, tb=.5); d.link(sock, nic)
    d.arrow([(684, y + 98), (720, y + 112)], color=INK)
    d.text(318, y + 222, 'plaintext IP packet goes INTO the TUN device; encrypted UDP comes OUT through an ordinary socket', 15, '#495057')
    y2 = y + 300
    d.zone(0, y2, 1290, 200, 'userspace-networking mode  (tailscaled --tun=userspace-networking)', 'lred', dashed=False, fs=20)
    a2 = d.box(18, y2 + 70, 190, 70, 'App configured to\nuse tailscaled\'s proxy', 'blue', fs=15)
    t2 = d.box(330, y2 + 70, 280, 70, 'tailscaled\n(proxy + WireGuard)', 'purple', fs=15)
    s2 = d.box(740, y2 + 70, 150, 70, 'UDP socket\n-> NIC', 'gray', fs=15)
    d.link(a2, t2); d.link(t2, s2)
    d.text(930, y2 + 62, 'NO tailscale0 interface: the OS cannot route\nnormal traffic into Tailscale. Meant for places\nwithout /dev/net/tun. Not suitable for Swarm.', 15, '#e03131')
    d.note(0, y2 + 235, 'In both modes WireGuard runs in USERSPACE (Tailscale uses its own wireguard-go fork). It is not the in-kernel WireGuard module.',
           'lyellow', 16, w=1290, h=50)
    return d


ALL = [d09_port_forwarding, d10_stun_coordination, d11_hole_punching, d12_lifecycle, d13_derp, d14_userspace_vs_tun]
