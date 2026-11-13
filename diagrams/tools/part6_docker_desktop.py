from dsl import *

DOC = 'Docker docs'


def d32_docker_desktop_documented():
    d = D('32-docker-desktop-what-the-docs-say', 'Docker Desktop (Windows): only what Docker\'s own docs state',
          'Green = stated in Docker\'s docs. Process names differ between doc pages and versions: verify on yours.')
    y = d.y0
    d.zone(0, y, 580, 400, 'Windows host', 'lgray', dashed=False, fs=20)
    d.box(30, y + 56, 520, 96, 'com.docker.backend.exe\nnetwork proxy + port forwarding; host file-\nsharing server, runs as the Docker Desktop user', 'green', fs=15)
    d.box(30, y + 172, 520, 86, 'com.docker.vpnkit(.exe)   user-space network process\ninherits firewall, VPN and HTTP-proxy settings of the user', 'green', fs=15)
    d.box(30, y + 278, 520, 86, 'com.docker.service   privileged helper\n(only in all-users installs; not used per-user)', 'green', fs=15)
    d.zone(880, y, 410, 400, 'Linux VM', 'lgray', dashed=False, fs=20)
    d.text(896, y + 36, 'WSL 2: the "docker-desktop" distribution\nHyper-V:  DockerDesktopVM', 14, '#495057')
    d.box(910, y + 100, 350, 60, 'Docker Engine', 'green', fs=17)
    d.box(910, y + 180, 350, 60, 'docker0 bridge', 'green', fs=17)
    d.box(910, y + 260, 350, 60, 'NAT adapter, typically 192.168.65.3', 'green', fs=14)
    d.box(910, y + 335, 350, 50, 'containers (e.g. 172.17.0.2)', 'green', fs=15)
    d.arrow([(580, y + 200), (880, y + 200)], color='#6741d9', heads='<->', sw=4)
    d.ctext(730, y + 124, 'AF_VSOCK\nhypervisor sockets\n(shared memory)', 15, '#6741d9')
    d.ctext(730, y + 216, 'not a network\nswitch or interface', 14, '#6741d9')
    d.note(0, y + 430, 'Also documented: there is no docker0 on the host; Docker Desktop cannot route traffic to Linux containers (you cannot ping them), and per-container IPs are not reachable from the host.\nSources: Docker docs: desktop/features/networking, networking-how-tos, faqs/platform, windows-permission-requirements (read 2026-11-13).',
           'lyellow', 15, w=1290, h=76)
    return d


def d33_egress_and_ports():
    d = D('33-docker-desktop-egress-and-published-ports', 'Docker Desktop: how traffic leaves, and how published ports come in',
          'Both directions go through a host-side process; the VM itself is never directly addressable from outside.')
    y = d.y0
    d.text(0, y, 'Outbound: a container reaches the Internet', 20, '#1971c2')
    out = [('container\n172.17.0.2', 'green'), ('docker0 + NAT\n192.168.65.3', 'blue'), ('shared-memory\nchannel', 'purple'), ('host process\n(backend / vpnkit)', 'yellow'), ('Internet', 'gray')]
    ids = [d.box(i * 262, y + 44, 220, 80, t, c, fs=15) for i, (t, c) in enumerate(out)]
    for a, b in zip(ids, ids[1:]): d.link(a, b, color='#1971c2')
    d.text(0, y + 136, 'The host process opens ordinary TCP/IP sockets, so firewalls, VPNs and proxies see traffic coming from IT, not from a VM.', 15, '#495057')
    y2 = y + 230
    d.text(0, y2, 'Inbound: a published port  (docker run -p 8080:80 nginx)', 20, '#2f9e44')
    inn = [('browser\nlocalhost:8080', 'gray'), ('host process\nlistens on :8080', 'yellow'), ('shared-memory\nchannel', 'purple'), ('VM routes to\n172.17.0.2:80', 'blue'), ('container\nnginx', 'green')]
    ids2 = [d.box(i * 262, y2 + 44, 220, 80, t, c, fs=15) for i, (t, c) in enumerate(inn)]
    for a, b in zip(ids2, ids2[1:]): d.link(a, b, color='#2f9e44')
    d.note(0, y2 + 170, 'Documented: this path exists for PUBLISHED container ports. Whether the same mechanism can expose the Engine\'s own ports (2377, 7946, 4789) to other machines is not documented, and is the open question of the next diagram.',
           'lyellow', 16, w=1290, h=70)
    return d


def d34_swarm_hypothesis():
    d = D('34-docker-desktop-as-a-swarm-node-documented-vs-hypothesis', 'Docker Desktop as a Swarm node: what is documented, what is a hypothesis',
          'Not tested. The point of this diagram is to keep facts and guesses visibly apart.')
    y = d.y0
    rn = d.box(0, y + 60, 250, 90, 'other swarm node\n(manager or worker)', 'blue', fs=16)
    hs = d.box(420, y + 60, 280, 90, 'Windows host\n192.168.1.100', 'gray', fs=16)
    vm = d.box(860, y + 20, 430, 170, '', 'lgray', dashed=True)
    d.text(878, y + 28, 'Docker Desktop VM  (private NAT address)', 16, '#495057')
    d.box(880, y + 70, 390, 50, 'Engine listens: 2377  7946  4789', 'green', fs=15)
    d.box(880, y + 128, 390, 46, 'swarm node would live here', 'lgray', fs=14, dashed=True)
    d.arrow([(250, y + 105), (420, y + 105)], color='#1971c2', heads='->', sw=3, label='connect to 2377', lfs=14)
    d.arrow([(700, y + 105), (860, y + 105)], color='#e03131', heads='->', dashed=True, sw=3)
    d.x(780, y + 105, 15)
    d.text(440, y + 166, 'forwarded to the Engine?  (hypothesis: no rule by default)', 14, '#e03131')
    d.text(0, y + 220, 'Documented (green):', 19, '#2f9e44')
    docs = ['The VM has a private NAT address (typically 192.168.65.3); per-container IPs are not reachable from the host.',
            'Inbound traffic reaches the VM through a host-side process that forwards PUBLISHED container ports.',
            'Docker Desktop\'s docs assume a Swarm can be active on it (changing its internal IP ranges requires leaving any active Swarm).']
    for i, t in enumerate(docs):
        d.box(0, y + 256 + i * 70, 1290, 60, t, 'lgreen', fs=15, sw=1.5)
    d.text(0, y + 480, 'Hypotheses (red, UNTESTED):', 19, '#e03131')
    hyp = ['H1  Nothing forwards 2377 / 7946 / 4789 to the Engine in the default setup, so other nodes cannot reach it.',
           'H2  The user-space proxy re-originates flows, which could change the outer source IP of VXLAN packets and confuse the VTEP.',
           'H3  WSL mirrored networking (or netsh portproxy to the WSL VM) might make it work; MTU and firewall rules would still need care.']
    for i, t in enumerate(hyp):
        d.box(0, y + 516 + i * 70, 1290, 60, t, 'lred', fs=15, dashed=True, sw=1.5)
    d.note(0, y + 740, 'Experiment to settle it: Docker Desktop + WSL2 mirrored mode, `docker swarm init --advertise-addr <host LAN IP>`, join from a Linux box, then test 2377/7946/4789, then an overlay ping. Record Docker Desktop and WSL versions with the result.',
           'lyellow', 15, w=1290, h=70)
    return d


def d35_wsl2():
    d = D('35-wsl2-architecture', 'WSL 2: one lightweight VM, one Linux kernel, several isolated distributions',
          'What this guide relies on: a normal Ubuntu distribution with its own Docker Engine and Tailscale.')
    y = d.y0
    d.zone(0, y, 1290, 460, 'Windows machine', 'lgray', dashed=False, fs=20)
    d.box(30, y + 380, 1230, 56, 'Hyper-V hypervisor (Windows itself runs on top of it)', 'purple', fs=16)
    d.zone(30, y + 56, 1230, 300, 'WSL 2 utility VM   (one Microsoft-built Linux kernel, shared)', 'lblue', fs=18)
    ub = d.zone(60, y + 110, 560, 220, 'Ubuntu distribution  (yours)', 'lgreen', dashed=False, fs=17)
    d.box(84, y + 160, 250, 70, 'Docker Engine\n(installed with apt)', 'green', fs=15)
    d.box(350, y + 160, 250, 70, 'tailscaled\ntailscale0  100.x.y.z', 'teal', fs=15)
    d.box(84, y + 250, 516, 56, 'systemd (enable it: /etc/wsl.conf  [boot] systemd=true)', 'yellow', fs=14)
    d.zone(660, y + 110, 570, 220, '"docker-desktop" distribution  (Docker Desktop\'s own)', 'lorange', dashed=False, fs=17)
    d.box(684, y + 160, 520, 60, 'Docker Desktop\'s Engine (managed by Docker Desktop)', 'orange', fs=15)
    d.text(684, y + 236, 'Docker docs: isolated from other distros the way any two\ndistros are; interacts only if WSL integration is enabled.', 14, '#495057')
    d.note(0, y + 490, 'Networking (Microsoft docs): the default mode is NAT: the VM has its own virtual adapter and IP behind Windows (so Tailscale in WSL is behind that NAT too). "mirrored" mode shares the host\'s interfaces; "bridged" is deprecated since WSL 2.4.5.\nDocker\'s WSL docs warn that running Docker Desktop and a separate Engine inside WSL can conflict: disable Desktop\'s WSL integration for this distro.',
           'lyellow', 15, w=1290, h=84)
    return d


def d36_proxies():
    d = D('36-proxy-types', 'Proxies, and why NAT is not one',
          'A proxy terminates your connection and opens a new one on your behalf. NAT only rewrites headers.')
    y = d.y0
    cells = [('Forward proxy', 'Client knows about it (browser / OS setting).', [('client', 'blue'), ('proxy', 'yellow'), ('Internet', 'gray')], 'lblue'),
             ('Reverse proxy', 'Client thinks it IS the server (load balancing, TLS).', [('Internet', 'gray'), ('proxy', 'yellow'), ('backend 1..3', 'green')], 'lgreen'),
             ('Transparent proxy', 'Traffic is intercepted; nobody configured anything.', [('user PC', 'blue'), ('router\n(intercepts)', 'yellow'), ('Internet', 'gray')], 'lyellow'),
             ('NAT / PAT  (NOT a proxy)', 'Rewrites addresses and ports in flight; the connection stays end to end.', [('LAN', 'blue'), ('router\n(rewrites)', 'orange'), ('Internet', 'gray')], 'lorange')]
    for i, (t, sub, ch, col) in enumerate(cells):
        x = (i % 2) * 650; yy = y + (i // 2) * 270
        d.zone(x, yy, 630, 250, '', col, dashed=False)
        d.text(x + 16, yy + 12, t, 22, C[col][1]); d.text(x + 16, yy + 50, sub, 15, '#495057')
        ids = [d.box(x + 24 + j * 200, yy + 120, 160, 80, tt, cc, fs=15) for j, (tt, cc) in enumerate(ch)]
        for a, b in zip(ids, ids[1:]): d.link(a, b, color=C[col][1])
    return d


ALL = [d32_docker_desktop_documented, d33_egress_and_ports, d34_swarm_hypothesis, d35_wsl2, d36_proxies]
