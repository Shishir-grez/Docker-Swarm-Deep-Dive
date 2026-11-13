from dsl import *
import math


def d15_swarm_vocab():
    d = D('15-swarm-vocabulary', 'Swarm vocabulary: cluster, node, manager, worker, service, task',
          'You declare what you want (a service). Swarm keeps making it true.')
    y = d.y0
    d.zone(0, y, 800, 470, 'Swarm = a cluster of nodes managed as one', 'lblue', dashed=False, fs=20)
    mg = d.box(24, y + 56, 752, 110, 'MANAGER node\nkeeps the cluster records (Raft), decides what runs where.\nCan also run tasks.', 'purple', fs=17)
    w1 = d.box(24, y + 210, 360, 230, '', 'lgreen')
    w2 = d.box(416, y + 210, 360, 230, '', 'lgreen')
    d.text(40, y + 220, 'WORKER node 1\n(one friend\'s PC)', 17, '#2f9e44')
    d.text(432, y + 220, 'WORKER node 2\n(another PC)', 17, '#2f9e44')
    for i, t in enumerate(['web.1', 'db.1']):
        d.box(50 + i * 160, y + 330, 140, 70, t, 'green', fs=17)
    for i, t in enumerate(['web.2', 'web.3']):
        d.box(442 + i * 160, y + 330, 140, 70, t, 'green', fs=17)
    d.link(mg, w1, 'b', 't', ta=.25, tb=.5, color='#6741d9', label='schedules tasks', lfs=14)
    d.link(mg, w2, 'b', 't', ta=.75, tb=.5, color='#6741d9')
    d.text(850, y + 10, 'You (on a manager):', 18, '#495057')
    cmd = d.box(850, y + 50, 440, 90, 'docker service create \\\n  --name web --replicas 3 nginx', 'lgray', fs=15, font=MONO)
    sv = d.box(850, y + 190, 440, 90, 'SERVICE "web"\ndesired state: 3 copies running', 'yellow', fs=17)
    ts = d.box(850, y + 330, 440, 110, 'TASK = one running copy\n(also called a replica): web.1  web.2  web.3\nSwarm places each on a node', 'green', fs=16)
    d.link(cmd, sv, 'b', 't'); d.link(sv, ts, 'b', 't')
    d.note(0, y + 500, 'If a node dies, the manager notices and starts its tasks elsewhere: that is "desired state". db.1 is a different service with 1 replica.',
           'lyellow', 16, w=1290, h=50)
    return d


def d16_ports():
    d = D('16-swarm-ports-who-talks-to-whom', 'The three ports that make Swarm tick',
          'Every node must reach every other node on these, and ONLY these. Keep them off the public Internet.')
    y = d.y0 + 10
    M = d.box(500, y + 10, 280, 90, 'MANAGER node', 'purple', fs=20)
    W1 = d.box(40, y + 330, 280, 90, 'WORKER node 1', 'green', fs=20)
    W2 = d.box(960, y + 330, 280, 90, 'WORKER node 2', 'green', fs=20)
    ext = d.box(1050, y + 140, 230, 80, 'user / browser\n(outside)', 'gray', fs=17)
    # plain links first (so chips sit on top)
    d.arrow([d.anchor(M, 'b', .25), d.anchor(W1, 't', .75)], color='#868e96', heads='--', sw=4)
    d.arrow([d.anchor(M, 'b', .75), d.anchor(W2, 't', .25)], color='#868e96', heads='--', sw=4)
    d.arrow([d.anchor(W1, 'r', .5), d.anchor(W2, 'l', .5)], color='#868e96', heads='--', sw=4)
    def chip(cx, cy, rows):
        h = 30
        top = cy - len(rows) * h / 2
        for i, (col, t) in enumerate(rows):
            d.box(cx - 125, top + i * h, 250, h - 2, t, col, fs=14, sw=1.5, round=False)
    chip(410, y + 215, [('blue', '2377/tcp  worker -> manager'), ('purple', '7946/tcp+udp  gossip'), ('orange', '4789/udp  VXLAN data')])
    chip(870, y + 215, [('blue', '2377/tcp  worker -> manager'), ('purple', '7946/tcp+udp  gossip'), ('orange', '4789/udp  VXLAN data')])
    chip(640, y + 377, [('purple', '7946/tcp+udp  gossip'), ('orange', '4789/udp  VXLAN data')])
    d.arrow([(1165, y + 220), (1165, y + 330)], color='#2f9e44', heads='->', sw=3)
    d.text(1052, y + 258, 'published port\n(e.g. 8080)', 14, '#2f9e44')
    d.text(0, y + 10, 'blue = control plane (Raft between managers too)\npurple = membership + overlay state (gossip)\norange = container-to-container traffic (VXLAN)\ngreen = the ONLY port meant for outsiders', 15, '#495057')
    d.note(0, y + 460, 'Workers start the 2377 connection to a manager, so a worker behind NAT can join. 7946 and 4789 are symmetric: any node may start them. Tested: a manager listens on 2377/tcp, 7946/tcp+udp and 4789/udp.',
           'lyellow', 15, w=1290, h=60)
    return d


def d17_raft():
    d = D('17-raft-quorum', 'Managers agree using Raft: a majority (quorum) must be reachable',
          'Swarm defaults (docker info): heartbeat every 1 s; election after 10 missed ticks (~10 s).')
    y = d.y0 + 10
    L = d.box(220, y, 240, 90, 'LEADER\nall writes go here', 'purple', fs=17)
    F1 = d.box(0, y + 220, 240, 90, 'follower', 'lpurple', fs=17)
    F2 = d.box(440, y + 220, 240, 90, 'follower', 'lpurple', fs=17)
    d.link(L, F1, 'b', 't', ta=.2, tb=.5, color='#6741d9', label='heartbeat 1 s', lfs=14, lpos=(60, y + 150))
    d.link(L, F2, 'b', 't', ta=.8, tb=.5, color='#6741d9')
    d.note(0, y + 350, 'No heartbeat for ~10 s (Election Tick 10) -> a follower calls an election; a new leader needs votes from a majority.\nWithout a majority the cluster stops accepting changes (this prevents "split brain").',
           'lyellow', 15, w=700, h=84)
    d.text(780, y, 'Managers   quorum   failures tolerated', 18, '#495057')
    rows = [('1', '1', '0', 'lgray'), ('3', '2', '1', 'lgreen'), ('4', '3', '1', 'lyellow'), ('5', '3', '2', 'lgreen'), ('7', '4', '3', 'lgreen')]
    for i, (m, q, f, c) in enumerate(rows):
        yy = y + 40 + i * 66
        d.box(780, yy, 120, 54, m, c, fs=20); d.box(910, yy, 120, 54, q, c, fs=20); d.box(1040, yy, 120, 54, f, c, fs=20)
    d.note(780, y + 380, 'quorum = floor(N/2) + 1.   4 managers tolerate no more failures than 3,\nso use an ODD number: 3, 5 or 7.', 'lorange', 15, w=480, h=70)
    return d


def d18_gossip():
    d = D('18-gossip-fan-out', 'Gossip: each node tells a few random peers, so news spreads in O(log N) rounds',
          'Example with 8 nodes. Orange = knows the news (a new container started on node 1).')
    y = d.y0 + 10
    R = 95
    def circle(cx, cy, informed, edges, title):
        d.ctext(cx, y, title, 20, '#495057')
        pos = []
        for k in range(8):
            ang = -math.pi / 2 + k * 2 * math.pi / 8
            pos.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
        ids = []
        for k, (px, py) in enumerate(pos):
            ids.append(d.box(px - 22, py - 22, 44, 44, str(k + 1), 'orange' if k in informed else 'lgray', fs=17, shape='ellipse', sw=2))
        for a, b in edges:
            (ax, ay), (bx, by) = pos[a], pos[b]
            L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
            d.arrow([(ax + ux * 26, ay + uy * 26), (bx - ux * 26, by - uy * 26)], color='#e8590c', heads='->', sw=2)
    circle(215, y + 190, {0}, [], 'round 0: node 1 knows')
    circle(645, y + 190, {0, 2, 5}, [(0, 2), (0, 5)], 'round 1: it tells 2 random peers')
    circle(1075, y + 190, {0, 2, 5, 1, 3, 4, 6}, [(0, 1), (2, 3), (2, 4), (5, 6), (5, 4)], 'round 2: 3 nodes tell 2 each')
    d.note(0, y + 360, 'Round 3: the last node hears it. Each round roughly multiplies the informed nodes, so N nodes need about log N rounds (exact timing depends on cluster size and gossip interval).\nThe news here is: "container MAC/IP X lives on host Y", which each node needs to forward overlay traffic. Packets may be lost: another peer repeats the news, which is why UDP is fine.',
           'lyellow', 15, w=1290, h=84)
    return d


def d19_routing_mesh():
    d = D('19-ingress-routing-mesh', 'Routing mesh: any node accepts the published port, even with no replica',
          'Service "web" published on 8080 with 2 replicas on nodes 1 and 2.')
    y = d.y0 + 20
    ex = d.box(0, y + 120, 200, 80, 'user / browser', 'gray', fs=17)
    n3 = d.box(330, y + 70, 330, 190, '', 'lblue', sw=3)
    d.text(350, y + 78, 'node-3  (no web replica)', 18, '#1971c2')
    d.box(350, y + 120, 290, 56, 'iptables: catch :8080', 'blue', fs=15)
    d.box(350, y + 190, 290, 56, 'IPVS: pick a replica', 'blue', fs=15)
    n1 = d.box(900, y, 360, 130, '', 'lgreen', sw=3)
    d.text(920, y + 8, 'node-1', 18, '#2f9e44'); d.box(920, y + 50, 150, 56, 'web.1', 'green', fs=17)
    n2 = d.box(900, y + 190, 360, 130, '', 'lgreen', sw=3)
    d.text(920, y + 198, 'node-2', 18, '#2f9e44'); d.box(920, y + 240, 150, 56, 'web.2', 'green', fs=17)
    d.arrow([(200, y + 160), (330, y + 160)], color='#2f9e44', label=':8080', lpos=(236, y + 128), lfs=15)
    d.arrow([(660, y + 180), (900, y + 80)], color='#e8590c', label='VXLAN (ingress network,\nUDP 4789)', lpos=(690, y + 80), lfs=14)
    d.arrow([(660, y + 220), (900, y + 250)], color='#e8590c', dashed=True)
    d.note(0, y + 350, 'The ingress overlay network exists on every node, so the node that received the request forwards it over VXLAN to whichever node holds a healthy replica.\nIngress is the only channel meant for outsiders; keep 2377, 7946 and 4789 reachable only by swarm nodes.',
           'lyellow', 15, w=1290, h=74)
    return d


ALL = [d15_swarm_vocab, d16_ports, d17_raft, d18_gossip, d19_routing_mesh]
