from dsl import *


def d37_solution_stack():
    d = D('37-the-solution-docker-engine-plus-tailscale-in-wsl2', 'The setup this guide builds: Docker Engine + Tailscale inside each WSL2 Ubuntu',
          'Swarm traffic rides inside Tailscale\'s encrypted tunnels, so NATs and CGNAT stop mattering.')
    y = d.y0
    cs = d.box(465, y, 360, 60, 'Tailscale coordination server\n(introductions only, never your traffic)', 'purple', fs=14)
    roles = [('MANAGER', 'purple'), ('worker', 'green'), ('worker', 'green')]
    ts = []
    for i in range(3):
        x = i * 465
        d.zone(x, y + 110, 360, 280, f"Friend {i+1}'s PC (Windows)", 'lgray', dashed=False, fs=17)
        d.zone(x + 18, y + 150, 324, 222, 'WSL 2 Ubuntu', 'lblue', dashed=False, fs=16)
        d.box(x + 40, y + 190, 280, 60, f'Docker Engine  (swarm {roles[i][0]})', roles[i][1], fs=15)
        ts.append(d.box(x + 40, y + 280, 280, 60, 'tailscale0  100.x.y.z', 'teal', fs=16))
        d.arrow([(x + 180, y + 110), (645, y + 60)], color='#6741d9', heads='--', dashed=True, sw=1.5)
    d.arrow([d.anchor(ts[0], 'r'), d.anchor(ts[1], 'l')], color='#2f9e44', heads='<->', sw=3)
    d.arrow([d.anchor(ts[1], 'r'), d.anchor(ts[2], 'l')], color='#2f9e44', heads='<->', sw=3)
    d.ctext(412, y + 330, 'direct', 14, '#2f9e44'); d.ctext(877, y + 330, 'direct', 14, '#2f9e44')
    dr = d.box(520, y + 440, 250, 56, 'DERP relay', 'orange', fs=16)
    d.arrow([(180, y + 340), (180, y + 468), (520, y + 468)], color='#e8590c', heads='--', dashed=True, sw=2.5)
    d.arrow([(770, y + 468), (1110, y + 468), (1110, y + 340)], color='#e8590c', heads='->', dashed=True, sw=2.5)
    d.text(200, y + 408, 'Friend 1 <-> Friend 3 (hard NAT on both sides): relayed through DERP, still end-to-end encrypted.', 14, '#e8590c')
    d.note(0, y + 530, 'docker swarm init --advertise-addr $(tailscale ip -4)     (on the manager)\ndocker swarm join --token <token> <manager tailscale IP>:2377     (on each worker)',
           'lgray', 15, w=1290, h=66)
    return d


def d38_mtu():
    d = D('38-mtu-budget-container-to-wire', 'The MTU budget: why Docker needs the MTU option over Tailscale',
          'Bar widths are to scale (1 px = 1.4 bytes). Tested: Docker defaults the overlay to 1450 regardless of the underlay.')
    y = d.y0
    sc = 1 / 1.4
    def X(b): return b * sc
    # reference lines
    for lbl, b, col in [('tailscale0 MTU 1280', 1280, '#0c8599'), ('physical link 1500', 1500, '#495057')]:
        d.arrow([(X(b), y + 44), (X(b), y + 340)], color=col, heads='--', dashed=True, sw=2)
        d.ctext(X(b), y + 20, lbl, 15, col)
    # row A
    d.text(0, y + 66, 'A  Docker default (no option): overlay MTU 1450', 18, '#e03131')
    d.box(0, y + 100, X(1450), 56, 'container packet up to 1450', 'red', fs=15, round=False)
    d.box(X(1450), y + 100, X(50), 56, '', 'purple', round=False)
    d.text(0, y + 160, '1450 + 50 = 1500 > 1280: TOO BIG for tailscale0', 15, '#e03131')
    # row B
    d.text(0, y + 200, 'B  With --opt com.docker.network.driver.mtu=1280: overlay MTU 1230', 18, '#2f9e44')
    d.box(0, y + 236, X(1230), 56, 'container packet up to 1230', 'green', fs=15, round=False)
    d.box(X(1230), y + 236, X(50), 56, '', 'purple', round=False)
    d.box(X(1280), y + 236, X(80), 56, '', 'teal', round=False)
    d.text(0, y + 298, '1230 + 50 = 1280 fits tailscale0;  + WireGuard/UDP/IP (up to 80) = 1360 < 1500: OK', 15, '#2f9e44')
    d.legend(0, y + 350, [('purple', 'VXLAN overhead 50 = inner Eth 14 + VXLAN 8 + UDP 8 + outer IP 20'), ('teal', 'WireGuard overhead (up to 80): added BELOW tailscale0, so it is not subtracted from 1280')], fs=14)
    d.note(0, y + 430, 'Rule of thumb: inner MTU = tailscale0 MTU - 50.  Docker subtracts the 50 itself, so pass the UNDERLAY value (1280): `docker network create -d overlay --opt com.docker.network.driver.mtu=1280 ...`\n(Passing 1230 gives 1180.)  The default `ingress` network needs the same option.',
           'lyellow', 15, w=1290, h=70)
    return d


def d39_firewall():
    d = D('39-where-to-filter-swarm-ports', 'Where to filter Swarm ports when peers connect over Tailscale',
          'The cloud (VPC) firewall only ever sees the OUTER encrypted packets. Filter on tailscale0 inside the machine.')
    y = d.y0 + 10
    peer = d.box(0, y + 60, 190, 80, 'peer PC', 'blue', fs=17)
    vpc = d.box(260, y + 20, 270, 160, 'Cloud VPC firewall\nsees: UDP from the peer\'s\nPUBLIC IP, encrypted.\nA rule for 100.64.0.0/10\nnever matches.', 'lred', fs=14)
    nic = d.box(590, y + 60, 150, 80, 'VM NIC', 'gray', fs=16)
    td = d.box(790, y + 60, 160, 80, 'tailscaled\ndecrypts', 'teal', fs=15)
    uf = d.box(1000, y + 20, 290, 160, 'host firewall (ufw)\nsees: src 100.x, dst 2377/tcp\nufw allow in on tailscale0\nto any port 2377 proto tcp', 'lgreen', fs=14)
    d.link(peer, vpc, color='#e8590c')
    d.link(vpc, nic, color='#e8590c'); d.link(nic, td, color='#e8590c'); d.link(td, uf, color='#2f9e44')
    d.text(0, y + 196, 'outer packet (what the cloud sees): src = the peer\'s PUBLIC IP, UDP 41641 or DERP over TCP 443, encrypted', 15, '#e8590c')
    d.text(0, y + 220, 'inner packet (what ufw sees after decryption): src 100.x.y.z, dst 2377/tcp', 15, '#2f9e44')
    d.box(0, y + 270, 620, 110, 'Do NOT open 2377 / 7946 / 4789 in the cloud firewall.\nOptional: allow inbound UDP 41641 so Tailscale can connect directly.', 'lyellow', fs=15)
    d.box(670, y + 270, 620, 110, 'DO restrict them in the host firewall to tailscale0:\nplain `ufw allow 2377/tcp` opens the port on EVERY interface.', 'lgreen', fs=15)
    return d


def d40_hands_on():
    d = D('40-hands-on-flow', 'The hands-on path, with a check after every step',
          'Corrected sequence (see the numbered sections 5A-5H of the guide).')
    y = d.y0
    steps = [('5A  Install', 'Docker Engine + Tailscale in WSL2 Ubuntu.\nCheck: systemctl is-system-running\n(enable systemd; turn off Desktop WSL integration)', 'blue'),
             ('5B  Connect', 'sudo tailscale up;  tailscale ip -4\nping the other PCs, then\ntailscale status  (idle = ping first)', 'teal'),
             ('5C  Firewall', 'ufw allow in on tailscale0 to any\nport 2377/tcp, 7946/tcp+udp, 4789/udp\n(nothing in the cloud VPC)', 'yellow'),
             ('5D  MTU', 'create overlays with\n--opt com.docker.network.driver.mtu=1280\nCheck: eth0 mtu = 1230 in a container', 'orange'),
             ('5E  Init', 'docker swarm init\n  --advertise-addr $(tailscale ip -4)\nCheck: docker node inspect self', 'purple'),
             ('5F  Join', 'docker swarm join --token ...\n  <manager 100.x>:2377\nCheck: docker node ls  (Ready/Active)', 'purple'),
             ('5G  Test', 'Test 1: web-test on 8080\ndocker service rm web-test\nTest 2: overlay + service discovery', 'green'),
             ('5H  Clean up', 'docker service rm ...; network rm ...\ndocker swarm leave\n(NOT prune -a --volumes)', 'red')]
    for i, (t, b, c) in enumerate(steps):
        x = (i % 4) * 325; yy = y + (i // 4) * 215
        d.box(x, yy, 300, 185, f'{t}\n\n{b}', c, fs=14)
    return d


def d41_ladder():
    d = D('41-concept-ladder-reading-map', 'The concept ladder: each rung answers the question the last one leaves open',
          'A suggested order for a reader with zero prerequisites.')
    y = d.y0
    rungs = [('1  Packet, address, port, protocol', 'How does data find a program?', 'blue'),
             ('2  Network, router, route, hop', 'How does it cross networks?', 'blue'),
             ('3  Private addresses, NAT, IPv6, CGNAT', 'Why can\'t my friend reach me?', 'blue'),
             ('4  Port-forward / relay / VPN -> tunnel', 'How can two NATed PCs talk?  (define "encapsulation" here)', 'blue'),
             ('5  Tailscale: STUN, hole punching, DERP, TUN, MTU', 'Now every PC has a reachable address.', 'teal'),
             ('6  Containers: namespaces, cgroups, veth, bridge', 'How do two containers on ONE host talk?', 'green'),
             ('7  Cluster: node, manager, worker, service, task, ports', 'How do containers on DIFFERENT hosts talk?', 'green'),
             ('8  Overlay + VXLAN: VTEP, FDB, ARP proxy, MTU', 'What exactly would Docker Desktop have to provide?', 'purple'),
             ('9  Docker Desktop / WSL2: documented vs hypothesis', 'So which setup works?', 'orange'),
             ('10  Hands-on + verification script', 'Does it really work? Prove it.', 'red')]
    ids = []
    for i, (t, q, c) in enumerate(rungs):
        col, row = divmod(i, 5)
        x = col * 660; yy = y + row * 118
        ids.append(d.box(x, yy, 620, 96, f'{t}\n{q}', c, fs=16))
    for i in range(4): d.link(ids[i], ids[i + 1], 'b', 't')
    for i in range(5, 9): d.link(ids[i], ids[i + 1], 'b', 't')
    d.arrow([d.anchor(ids[4], 'r'), (640, d.geo[ids[4]][1] + 48), (640, y + 48), d.anchor(ids[5], 'l')], color='#868e96', heads='->', dashed=True)
    d.text(0, y + 610, 'Left: reachability (the networking you need before any container).   Right: containers, Swarm, the overlay, then the real setup.', 15, MUTED)
    return d


ALL = [d37_solution_stack, d38_mtu, d39_firewall, d40_hands_on, d41_ladder]
