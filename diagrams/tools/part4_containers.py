from dsl import *


def d20_container_vs_vm():
    d = D('20-containers-vs-vms', 'A container is not a small VM: it shares the host kernel',
          'Isolation comes from kernel features (namespaces + cgroups), not from a second operating system.')
    y = d.y0
    d.zone(0, y, 620, 440, 'Virtual machines', 'lblue', dashed=False, fs=22)
    d.box(30, y + 380, 560, 44, 'Hardware', 'gray', fs=16)
    d.box(30, y + 320, 560, 50, 'Hypervisor (Hyper-V, KVM, ...)', 'purple', fs=16)
    for i in range(2):
        x = 30 + i * 285
        d.box(x, y + 200, 275, 110, 'Guest OS\n(its OWN kernel)', 'orange', fs=16)
        d.box(x, y + 120, 275, 70, f'App {i+1}', 'green', fs=16)
    d.text(30, y + 64, 'Each VM boots a full operating system.\nHeavy: GBs of RAM, boots in seconds-minutes.', 15, '#495057')
    d.zone(670, y, 620, 440, 'Containers', 'lgreen', dashed=False, fs=22)
    d.box(700, y + 380, 560, 44, 'Hardware', 'gray', fs=16)
    d.box(700, y + 320, 560, 50, 'ONE host kernel (Linux): namespaces + cgroups', 'purple', fs=16)
    d.box(700, y + 250, 560, 60, 'Container runtime (containerd / runc)', 'blue', fs=16)
    for i in range(3):
        d.box(700 + i * 190, y + 130, 180, 110, f'Container {i+1}\napp + libs\n(no kernel)', 'green', fs=15)
    d.text(700, y + 64, 'Containers are ordinary processes with a restricted view.\nLight: MBs of RAM, start in milliseconds.', 15, '#495057')
    d.note(0, y + 470, 'Docker Desktop on Windows/macOS runs a small Linux VM so that Linux containers have a Linux kernel to share. (Windows also has its own separate "Windows containers".)',
           'lyellow', 16, w=1290, h=54)
    return d


def d21_namespaces():
    d = D('21-namespaces-and-cgroups', 'What a container really is: a process + namespaces (view) + cgroups (budget)',
          'Namespaces change what a process can SEE. cgroups limit what it can USE.')
    y = d.y0
    ns = [('PID', 'process IDs:\nnginx is PID 1\ninside, PID 2048 on host'), ('NET', 'interfaces, IPs, routes,\nfirewall rules, ports'),
          ('MNT', 'filesystem mounts:\nits own root "/"'), ('UTS', 'hostname'),
          ('IPC', 'shared memory,\nmessage queues'), ('USER', 'root inside can be an\nunprivileged UID outside'),
          ('CGROUP', 'view of the cgroup tree')]
    d.text(0, y, 'Linux namespaces (7 of the 8 kinds):', 20, '#1971c2')
    for i, (n, t) in enumerate(ns):
        x = (i % 4) * 320; yy = y + 40 + (i // 4) * 150
        d.box(x, yy, 300, 130, '', 'lblue')
        d.text(x + 16, yy + 10, n, 22, '#1971c2')
        d.text(x + 16, yy + 48, t, 15, INK)
    cg = d.box(960, y + 190, 300, 130, '', 'lyellow')
    d.text(976, y + 200, 'cgroups', 22, '#e67700')
    d.text(976, y + 238, 'limits + accounting:\nCPU 1 core, RAM 512 MB,\nI/O 10 MB/s', 15, INK)
    d.box(0, y + 350, 620, 80, 'OverlayFS: image layers + a writable top layer\n(each container gets its own root filesystem)', 'lpurple', fs=15)
    d.box(660, y + 350, 600, 80, 'docker run nginx  ->  new namespaces + cgroup\n+ filesystem, then start the process inside them', 'lgreen', fs=15)
    d.note(0, y + 460, 'Because NET is a namespace, a new container starts with NO network at all. Docker then connects it (veth + bridge, next diagram).',
           'lyellow', 16, w=1290, h=50)
    return d


def d22_same_host_bridge():
    d = D('22-containers-on-one-host', 'Same host: containers are wired to a bridge, so they CAN talk',
          'Tested: 172.17.0.2 pings 172.17.0.3 (separate network namespaces, default bridge).')
    y = d.y0
    d.zone(0, y, 1290, 400, 'One Docker host  (192.168.1.10)', 'lgray', dashed=False, fs=20)
    d.zone(30, y + 60, 280, 150, 'netns: container 1', 'lblue', fs=16)
    d.zone(980, y + 60, 280, 150, 'netns: container 2', 'lblue', fs=16)
    c1 = d.box(60, y + 110, 220, 70, 'eth0 172.17.0.2', 'blue', fs=17)
    c2 = d.box(1010, y + 110, 220, 70, 'eth0 172.17.0.3', 'blue', fs=17)
    br = d.box(480, y + 110, 330, 70, 'docker0 bridge  172.17.0.1\n(a virtual switch)', 'green', fs=17)
    d.link(c1, br, color='#2f9e44', heads='<->', label='veth pair', lfs=14)
    d.link(br, c2, color='#2f9e44', heads='<->', label='veth pair', lfs=14)
    nat = d.box(480, y + 260, 330, 60, 'NAT (masquerade)', 'yellow', fs=17)
    eth = d.box(480, y + 340, 330, 44, 'host eth0 -> Internet', 'gray', fs=16)
    d.link(br, nat, 'b', 't', color='#e67700'); d.link(nat, eth, 'b', 't', color='#e67700')
    d.text(830, y + 270, 'traffic to the outside leaves\nas the HOST\'s address', 15, '#e67700')
    d.note(0, y + 425, 'Each end of a veth pair is an interface: one end inside the container namespace, one on the bridge. Frames entering one end exit the other, like a virtual cable.',
           'lyellow', 16, w=1290, h=54)
    return d


def d23_cross_host_problem():
    d = D('23-containers-on-two-hosts', 'Two hosts: now the same trick fails',
          'docker0 exists only inside each machine, and both machines use the same addresses.')
    y = d.y0
    for i, (host, ip) in enumerate([('Machine A', '192.168.1.10'), ('Machine B', '192.168.1.20')]):
        x = i * 760
        d.zone(x, y, 530, 270, f'{host}  ({ip})', 'lblue', dashed=False, fs=19)
        d.box(x + 30, y + 70, 220, 70, 'Container\n172.17.0.2', 'blue', fs=17)
        d.box(x + 290, y + 70, 210, 70, 'docker0\n172.17.0.0/16', 'green', fs=17)
        d.arrow([(x + 250, y + 105), (x + 290, y + 105)], heads='<->')
        d.box(x + 30, y + 190, 470, 56, 'host NIC ' + ip, 'gray', fs=16)
    d.ctext(645, y + 105, '???', 54, '#e03131')
    d.arrow([(530, y + 218), (760, y + 218)], color='#868e96', heads='<->', dashed=True)
    d.text(560, y + 230, 'physical network', 14, MUTED)
    probs = [('1  No route', 'Container 1 has no path to a container on another host: docker0 is local to each machine.'),
             ('2  Same addresses', 'Both containers may be 172.17.0.2. Which one is meant?'),
             ('3  Hidden behind NAT', 'Each container sits behind its own host\'s NAT, so nobody can start a connection to it.')]
    for i, (t, b) in enumerate(probs):
        d.box(i * 436, y + 320, 420, 130, f'{t}\n{b}', 'lred', fs=15)
    d.note(0, y + 480, 'We want containers on different hosts to talk as if they were on ONE switch. That is what an overlay network provides.',
           'lyellow', 17, w=1290, h=48)
    return d


def d24_overlay_underlay():
    d = D('24-overlay-vs-underlay', 'Overlay network: a virtual LAN built on top of the real network',
          'Containers use overlay addresses; the hosts carry the packets over the underlay.')
    y = d.y0
    d.zone(0, y, 1290, 220, 'OVERLAY  10.0.1.0/24  (virtual: one big switch spanning both hosts)', 'lgreen', dashed=False, fs=19)
    c1 = d.box(120, y + 70, 220, 90, 'Container-1\n10.0.1.5', 'green', fs=18)
    c2 = d.box(950, y + 70, 220, 90, 'Container-2\n10.0.1.7', 'green', fs=18)
    d.arrow([(340, y + 115), (950, y + 115)], color='#2f9e44', heads='<->', sw=3, label='"same LAN": ordinary Ethernet + IP between them', lpos=(420, y + 76))
    d.zone(0, y + 290, 1290, 230, '', 'lblue', dashed=False)
    d.text(500, y + 298, 'UNDERLAY  the real network (here: your Tailscale addresses)', 19, '#1971c2')
    h1 = d.box(120, y + 360, 220, 90, 'Host A\n100.101.102.103', 'blue', fs=17)
    h2 = d.box(950, y + 360, 220, 90, 'Host B\n100.101.102.104', 'blue', fs=17)
    d.arrow([(340, y + 405), (950, y + 405)], color='#1971c2', heads='<->', sw=3, label='UDP packets between the hosts', lpos=(500, y + 366))
    d.arrow([(230, y + 160), (230, y + 360)], color='#e8590c', dashed=True, label='wrapped (VXLAN)', lpos=(244, y + 240), lfs=15)
    d.arrow([(1060, y + 360), (1060, y + 160)], color='#e8590c', dashed=True, label='unwrapped', lpos=(1076, y + 240), lfs=15)
    d.note(0, y + 550, 'Analogy: the underlay is the road network; the overlay is the postal addressing scheme. A letter uses the postal address (overlay) but physically travels on roads (underlay).',
           'lyellow', 16, w=1290, h=54)
    return d


def d25_swarm_init():
    d = D('25-what-swarm-init-creates', 'What `docker swarm init` sets up on a node',
          'Verified on Docker 29.9.2: ingress VNI 4096 (10.0.0.0/24); gwbridge 172.18.0.0/16; user overlays 4097, 4098, ...')
    y = d.y0
    items = [('Swarm identity', 'swarm ID, a root CA + certificates (mutual TLS between nodes), Raft database', 'purple'),
             ('Listening ports', '2377/tcp   7946/tcp+udp   4789/udp', 'orange'),
             ('"ingress" overlay network', 'VNI 4096, subnet 10.0.0.0/24 (routing mesh)', 'green'),
             ('"docker_gwbridge" bridge', 'subnet 172.18.0.0/16: the way out to the world', 'blue')]
    for i, (t, b, c) in enumerate(items):
        d.box(0, y + i * 112, 560, 96, f'{t}\n{b}', c, fs=16)
    d.zone(640, y, 650, 450, 'A container attached to an overlay network', 'lgray', dashed=False, fs=18)
    ct = d.box(880, y + 60, 190, 90, 'container', 'green', fs=18)
    e0 = d.box(680, y + 190, 250, 66, 'eth0  10.0.1.x  mtu 1450', 'green', fs=15)
    e1 = d.box(1010, y + 190, 250, 66, 'eth1  172.18.0.x  mtu 1500', 'blue', fs=15)
    d.link(ct, e0, 'b', 't', ta=.2, color='#2f9e44'); d.link(ct, e1, 'b', 't', ta=.8, color='#1971c2')
    ov = d.box(680, y + 310, 250, 90, 'overlay network\n(east-west: to other\ncontainers, any host)', 'lgreen', fs=15)
    gw = d.box(1010, y + 310, 250, 90, 'docker_gwbridge + NAT\n(north-south: Internet,\nexternal services)', 'lblue', fs=15)
    d.link(e0, ov, 'b', 't', color='#2f9e44'); d.link(e1, gw, 'b', 't', color='#1971c2')
    d.note(0, y + 480, 'Troubleshooting hint: if containers reach each other over the overlay but not the Internet, look at the docker_gwbridge/NAT path or net.ipv4.ip_forward.',
           'lyellow', 16, w=1290, h=50)
    return d


def d26_vxlan():
    d = D('26-vxlan-encapsulation', 'VXLAN: wrap the container\'s whole Ethernet frame inside a UDP packet',
          'MAC-in-UDP. The underlay only ever sees ordinary UDP between two hosts.')
    y = d.y0
    d.text(0, y, 'Before  (what the container sends):', 19, '#2f9e44')
    parts = [('Ethernet 14\nMAC c1->c2', 'green', 120), ('IP 20\n10.0.1.5->10.0.1.7', 'yellow', 210), ('TCP 20\nport 80', 'blue', 130), ('payload: GET /api/data', 'white', 300)]
    x = 0
    for t, c, w in parts:
        d.box(x, y + 40, w, 80, t, c, fs=14, round=False); x += w
    y2 = y + 220
    d.text(0, y2, 'After  (what leaves the host, via the VTEP):', 19, '#e8590c')
    pre = [('Outer Eth 14\n(not in MTU)', 'gray', 140), ('Outer IP 20\nhostA->hostB', 'orange', 150), ('UDP 8\nport 4789', 'orange', 110), ('VXLAN 8\nVNI', 'purple', 110)]
    x = 0
    for t, c, w in pre:
        d.box(x, y2 + 40, w, 80, t, c, fs=14, round=False); x += w
    x0 = x
    for t, c, w in parts:
        d.box(x, y2 + 40, w, 80, t, c, fs=14, round=False, dashed=True); x += w
    d.text(x0 + 4, y2 + 128, 'the ORIGINAL frame, untouched', 15, '#2f9e44')
    bx1, bx2 = 140, x0 + 120
    d.arrow([(bx1, y2 + 168), (bx2, y2 + 168)], color='#e8590c', heads='<->')
    d.arrow([(bx1, y2 + 168), (bx1, y2 + 124)], color='#e8590c', heads='--')
    d.arrow([(bx2, y2 + 168), (bx2, y2 + 124)], color='#e8590c', heads='--')
    d.ctext((bx1 + bx2) / 2, y2 + 178, 'counts against the MTU: outer IP 20 + UDP 8 + VXLAN 8 + inner Eth 14 = 50 bytes', 15, '#e8590c')
    d.note(0, y2 + 240, 'VNI = a 24-bit network ID (about 16 million networks, versus 4096 for VLANs). VTEP = the VXLAN Tunnel Endpoint that wraps and unwraps; in Swarm each host\'s kernel is the VTEP.\nUDP source port varies per flow (entropy for load balancing); destination port is 4789.',
           'lyellow', 15, w=1260, h=76)
    return d


ALL = [d20_container_vs_vm, d21_namespaces, d22_same_host_bridge, d23_cross_host_problem, d24_overlay_underlay, d25_swarm_init, d26_vxlan]
