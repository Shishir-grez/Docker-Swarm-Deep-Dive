# Diagrams

41 hand-drawn style diagrams for the two articles, made with Excalidraw's own library: **26 redraw existing visuals** (ASCII art and Mermaid) and **15 are new**, covering places where the text had no visual or the vocabulary was never explained.

| Folder | What it is |
| --- | --- |
| [`excalidraw/`](excalidraw) | **Editable source.** Open at <https://excalidraw.com> (menu > Open, or drag the file in). Arrows stay attached to boxes when you move them. |
| [`svg/`](svg) | **Embeddable.** Self-contained (the hand-drawn font is embedded), renders in GitHub Markdown. |
| [`tools/`](tools) | The generator the files were made with. Optional; see [Regenerating](#regenerating). |

Embed one in an article:

```markdown
![Same host: containers are wired to a bridge](diagrams/svg/22-containers-on-one-host.svg)
```

Need a PNG for another platform? In excalidraw.com: open the file, **Export image**, choose PNG (2x).

## Read this first: the diagrams follow the corrected facts

Where the current article text and reality disagree, the diagrams show reality (checked on **Docker 29.9.2, Linux 6.18, single-node swarm**, plus upstream source and docs). If you place a diagram, update the surrounding text to match:

- same-host containers **can** talk by default (`docker0`): diagrams 22, 23
- VXLAN device and bridge are `vxlan0` / `br0` inside a per-network namespace, not on the host; no `nolearning` (flags are `proxy l2miss l3miss`): 27, 28
- VNIs: ingress 4096, user overlays 4097, 4098, ...: 25, 31
- overlay MTU does not adapt (stays 1450); correct inner MTU over Tailscale is 1280 - 50 = 1230, set with `--opt com.docker.network.driver.mtu=1280`: 38
- Swarm Raft defaults: heartbeat 1 s, election after ~10 s: 17
- Tailscale starts on DERP and upgrades to direct; WireGuard is userspace on a kernel TUN: 12, 13, 14
- cloud firewalls see only the outer WireGuard packet; filter on `tailscale0`: 39
- Docker Desktop: only Docker's own documented facts are drawn as facts; the Swarm-node verdict is shown as an **untested hypothesis**: 32, 33, 34

**Not verified:** cross-host behaviour (real FDB entries, gossip timing), Docker Desktop internals on Windows, and Tailscale/WSL2 runtime. Diagrams touching those say so on the canvas.

## Index

Line numbers refer to the articles as of commit `e24f057`; they will move once you edit.

### Part 1 - Reachability: hops, NAT, CGNAT

| # | Diagram | Shows | Placement in the articles | Kind |
| --- | --- | --- | --- | --- |
| 01 | [`01-network-topologies`](svg/01-network-topologies.svg) ([edit](excalidraw/01-network-topologies.excalidraw)) | Client-server vs hub-and-spoke vs mesh | Replaces the Mermaid graph, main L56-72 | redrawn |
| 02 | [`02-packet-path-hops`](svg/02-packet-path-hops.svg) ([edit](excalidraw/02-packet-path-hops.excalidraw)) | Your PC to a friend's PC as a chain of hops, with the CGNAT hop called out | Replaces the Mermaid graph, main L100-120; ties to the traceroute at L124-142 | redrawn + new callout |
| 03 | [`03-layers-and-encapsulation`](svg/03-layers-and-encapsulation.svg) ([edit](excalidraw/03-layers-and-encapsulation.excalidraw)) | The 7 layers next to the nested Ethernet / IP / TCP envelope | Replaces Mermaid OSI main L150-176 and the three ASCII boxes L243-256, L279-296, L310-333 | redrawn |
| 04 | [`04-local-or-remote-delivery`](svg/04-local-or-remote-delivery.svg) ([edit](excalidraw/04-local-or-remote-delivery.excalidraw)) | Subnet-mask decision: deliver directly (ARP the destination) or via the gateway (ARP the router) | Illustrates main L428-493 (text and collapsibles only today) | new |
| 05 | [`05-what-changes-per-hop`](svg/05-what-changes-per-hop.svg) ([edit](excalidraw/05-what-changes-per-hop.excalidraw)) | IP stays, MACs change at every hop, NAT rewrites the source | Illustrates main L495-515 | new |
| 06 | [`06-nat-translation`](svg/06-nat-translation.svg) ([edit](excalidraw/06-nat-translation.excalidraw)) | NAT table, outbound rewrite, return path, and the unsolicited packet that dies | Replaces ASCII main L598-607 and deep dive L40-131, L188-215, Mermaid L339-381 | redrawn |
| 07 | [`07-nat-behaviours`](svg/07-nat-behaviours.svg) ([edit](excalidraw/07-nat-behaviours.excalidraw)) | Full cone / restricted / port-restricted / symmetric | Replaces ASCII deep dive L143-186 | redrawn |
| 08 | [`08-cgnat-double-nat`](svg/08-cgnat-double-nat.svg) ([edit](excalidraw/08-cgnat-double-nat.excalidraw)) | Two NATs in a row; why port forwarding is useless; the 100.64.0.0/10 overlap with Tailscale | Illustrates deep dive L227-233, L315-320 | new |

### Part 2 - How Tailscale connects

| # | Diagram | Shows | Placement in the articles | Kind |
| --- | --- | --- | --- | --- |
| 09 | [`09-port-forwarding`](svg/09-port-forwarding.svg) ([edit](excalidraw/09-port-forwarding.excalidraw)) | A static rule in your own NAT, and its four limits | Replaces ASCII deep dive L299-313 | redrawn |
| 10 | [`10-stun-and-coordination`](svg/10-stun-and-coordination.svg) ([edit](excalidraw/10-stun-and-coordination.excalidraw)) | Step 1 STUN (find my public address), step 2 coordination server (swap endpoints + keys) | Replaces ASCII deep dive L448-467, L473-494 | redrawn |
| 11 | [`11-hole-punching`](svg/11-hole-punching.svg) ([edit](excalidraw/11-hole-punching.excalidraw)) | Sequence: both sides send first, both NATs open a door (disco ping/pong) | Replaces ASCII deep dive L513-536 (corrected: probes are disco pings, not WireGuard handshakes) | redrawn + corrected |
| 12 | [`12-tailscale-connection-lifecycle`](svg/12-tailscale-connection-lifecycle.svg) ([edit](excalidraw/12-tailscale-connection-lifecycle.excalidraw)) | Relay first (DERP bootstrap), probe in parallel, upgrade to direct, retry every minute | Replaces the 4-phase list deep dive L410-420 and the 'NOW' timeline L896-919 | new + corrected |
| 13 | [`13-derp-relay`](svg/13-derp-relay.svg) ([edit](excalidraw/13-derp-relay.excalidraw)) | DERP forwards ciphertext by destination public key; outbound HTTPS only | Replaces ASCII deep dive L572-596 and L962-992 | redrawn + corrected |
| 14 | [`14-tailscale-packet-path-tun`](svg/14-tailscale-packet-path-tun.svg) ([edit](excalidraw/14-tailscale-packet-path-tun.excalidraw)) | TUN device + userspace WireGuard (normal mode) vs userspace-networking mode | Replaces ASCII deep dive L649-672 (corrected: WireGuard is userspace in both) | redrawn + corrected |

### Part 3 - Swarm basics

| # | Diagram | Shows | Placement in the articles | Kind |
| --- | --- | --- | --- | --- |
| 15 | [`15-swarm-vocabulary`](svg/15-swarm-vocabulary.svg) ([edit](excalidraw/15-swarm-vocabulary.excalidraw)) | Cluster, node, manager, worker, service, task/replica, desired state | Primer to insert before main L48 (the missing definitions) | new |
| 16 | [`16-swarm-ports-who-talks-to-whom`](svg/16-swarm-ports-who-talks-to-whom.svg) ([edit](excalidraw/16-swarm-ports-who-talks-to-whom.excalidraw)) | 2377 / 7946 / 4789 and the published port, per link | Illustrates the port tables, main L626-755 | new |
| 17 | [`17-raft-quorum`](svg/17-raft-quorum.svg) ([edit](excalidraw/17-raft-quorum.excalidraw)) | Leader / followers, Swarm's real timing, quorum table | Illustrates main L667-683, L747 | new + corrected |
| 18 | [`18-gossip-fan-out`](svg/18-gossip-fan-out.svg) ([edit](excalidraw/18-gossip-fan-out.excalidraw)) | Epidemic spread in O(log N) rounds | Replaces ASCII main L1204-1256 (the old example was a chain) | redrawn + corrected |
| 19 | [`19-ingress-routing-mesh`](svg/19-ingress-routing-mesh.svg) ([edit](excalidraw/19-ingress-routing-mesh.excalidraw)) | Any node accepts the published port and forwards over VXLAN | Illustrates main L703-714 | new |

### Part 4 - Containers and overlay networks

| # | Diagram | Shows | Placement in the articles | Kind |
| --- | --- | --- | --- | --- |
| 20 | [`20-containers-vs-vms`](svg/20-containers-vs-vms.svg) ([edit](excalidraw/20-containers-vs-vms.excalidraw)) | Shared kernel vs a kernel per VM | New foundation (was on your improvement roadmap) | new |
| 21 | [`21-namespaces-and-cgroups`](svg/21-namespaces-and-cgroups.svg) ([edit](excalidraw/21-namespaces-and-cgroups.excalidraw)) | Namespaces (view) + cgroups (budget) + OverlayFS | Replaces ASCII main L787-970 | redrawn |
| 22 | [`22-containers-on-one-host`](svg/22-containers-on-one-host.svg) ([edit](excalidraw/22-containers-on-one-host.excalidraw)) | veth pairs to docker0, NAT out. Same-host containers CAN talk | Replaces main L982-999 (corrected) | redrawn + corrected |
| 23 | [`23-containers-on-two-hosts`](svg/23-containers-on-two-hosts.svg) ([edit](excalidraw/23-containers-on-two-hosts.excalidraw)) | Why the same trick fails across hosts (no route, same IPs, NAT) | Replaces ASCII main L1005-1023 | redrawn |
| 24 | [`24-overlay-vs-underlay`](svg/24-overlay-vs-underlay.svg) ([edit](excalidraw/24-overlay-vs-underlay.excalidraw)) | Virtual LAN over the real network | Illustrates main L1029-1050 | new |
| 25 | [`25-what-swarm-init-creates`](svg/25-what-swarm-init-creates.svg) ([edit](excalidraw/25-what-swarm-init-creates.excalidraw)) | CA + Raft, ports, ingress (VNI 4096), docker_gwbridge; container eth0 + eth1 | Replaces ASCII main L1066-1091 and L1101-1118 | redrawn + corrected |
| 26 | [`26-vxlan-encapsulation`](svg/26-vxlan-encapsulation.svg) ([edit](excalidraw/26-vxlan-encapsulation.excalidraw)) | MAC-in-UDP before/after, with the 50-byte MTU cost | Replaces ASCII main L1332-1375 | redrawn |
| 27 | [`27-overlay-anatomy-inside-a-host`](svg/27-overlay-anatomy-inside-a-host.svg) ([edit](excalidraw/27-overlay-anatomy-inside-a-host.excalidraw)) | Container netns / overlay netns (br0, vxlan0) / host netns, real names | Replaces main L1391-1421 and L1720-1738 (corrected: names, namespaces, flags) | redrawn + corrected |
| 28 | [`28-how-the-vtep-knows-where-containers-are`](svg/28-how-the-vtep-knows-where-containers-are.svg) ([edit](excalidraw/28-how-the-vtep-knows-where-containers-are.excalidraw)) | Peer DB fills FDB + neighbour tables; ARP proxy answers locally | Replaces main L1433-1485 (nolearning), L1518-1591, L1617-1636 | redrawn + corrected |
| 29 | [`29-packet-journey-container-to-container`](svg/29-packet-journey-container-to-container.svg) ([edit](excalidraw/29-packet-journey-container-to-container.excalidraw)) | The 10-step journey across two hosts | Replaces the 13 ASCII steps main L1646-1940 | redrawn |
| 30 | [`30-same-host-vs-cross-host-overlay`](svg/30-same-host-vs-cross-host-overlay.svg) ([edit](excalidraw/30-same-host-vs-cross-host-overlay.excalidraw)) | Same host skips VXLAN (tested); cross host uses it | Replaces ASCII main L2001-2013 | redrawn |
| 31 | [`31-vni-keeps-overlays-apart`](svg/31-vni-keeps-overlays-apart.svg) ([edit](excalidraw/31-vni-keeps-overlays-apart.excalidraw)) | VNI check: deliver / deliver / discard | Replaces ASCII main L1319-1324 (corrected VNI numbers) | redrawn + corrected |

### Part 5 - Docker Desktop and WSL2 (documented vs hypothesis)

| # | Diagram | Shows | Placement in the articles | Kind |
| --- | --- | --- | --- | --- |
| 32 | [`32-docker-desktop-what-the-docs-say`](svg/32-docker-desktop-what-the-docs-say.svg) ([edit](excalidraw/32-docker-desktop-what-the-docs-say.excalidraw)) | Only what Docker's docs state: host processes, AF_VSOCK channel, VM, docker0 | Replaces main L2156-2200 and the process diagram L2327-2366 | redrawn (documented only) |
| 33 | [`33-docker-desktop-egress-and-published-ports`](svg/33-docker-desktop-egress-and-published-ports.svg) ([edit](excalidraw/33-docker-desktop-egress-and-published-ports.excalidraw)) | Outbound and published-port paths through the host process | Replaces ASCII main L2436-2447, L2560-2606, L2718-2746 | redrawn (documented only) |
| 34 | [`34-docker-desktop-as-a-swarm-node-documented-vs-hypothesis`](svg/34-docker-desktop-as-a-swarm-node-documented-vs-hypothesis.svg) ([edit](excalidraw/34-docker-desktop-as-a-swarm-node-documented-vs-hypothesis.excalidraw)) | Facts (green) and untested hypotheses (red), plus the experiment that would settle it | Replaces the 'IMPOSSIBLE' verdicts, main L3247-3336 | new |
| 35 | [`35-wsl2-architecture`](svg/35-wsl2-architecture.svg) ([edit](excalidraw/35-wsl2-architecture.excalidraw)) | One WSL2 VM and kernel, several distros; NAT vs mirrored; systemd; coexistence warning | Replaces ASCII main L2156-2200 | redrawn |
| 36 | [`36-proxy-types`](svg/36-proxy-types.svg) ([edit](excalidraw/36-proxy-types.excalidraw)) | Forward / reverse / transparent proxy, and NAT as a non-proxy | Replaces ASCII main L2775-2850 | redrawn + corrected |

### Part 6 - The setup and the hands-on path

| # | Diagram | Shows | Placement in the articles | Kind |
| --- | --- | --- | --- | --- |
| 37 | [`37-the-solution-docker-engine-plus-tailscale-in-wsl2`](svg/37-the-solution-docker-engine-plus-tailscale-in-wsl2.svg) ([edit](excalidraw/37-the-solution-docker-engine-plus-tailscale-in-wsl2.excalidraw)) | Three PCs, WSL2 Ubuntu each, direct tunnels and a DERP-relayed pair | Overview for main section 5; replaces ASCII L3358-3364 | new |
| 38 | [`38-mtu-budget-container-to-wire`](svg/38-mtu-budget-container-to-wire.svg) ([edit](excalidraw/38-mtu-budget-container-to-wire.excalidraw)) | To-scale bars: 1450 default overflows 1280; with the option 1230 + 50 = 1280, + WireGuard 1360 < 1500 | Replaces the MTU budget main L3508-3517 (corrected) | redrawn + corrected |
| 39 | [`39-where-to-filter-swarm-ports`](svg/39-where-to-filter-swarm-ports.svg) ([edit](excalidraw/39-where-to-filter-swarm-ports.excalidraw)) | The cloud firewall sees only the outer packet; filter on tailscale0 in the host | Illustrates main L3464-3495 (corrected) | new + corrected |
| 40 | [`40-hands-on-flow`](svg/40-hands-on-flow.svg) ([edit](excalidraw/40-hands-on-flow.excalidraw)) | Steps 5A-5H, each with its check | Overview for main section 5 (corrected order) | new |
| 41 | [`41-concept-ladder-reading-map`](svg/41-concept-ladder-reading-map.svg) ([edit](excalidraw/41-concept-ladder-reading-map.excalidraw)) | Ten rungs, each answering the question the last leaves open | Reading map for the README | new |

## Existing visuals deliberately not redrawn

- `nolearning` flow (main L1470-1483): incorrect, replaced by diagram 28.
- VPNKit packet-reconstruction steps and shared-memory pointers (main L2905-3043, L3199-3243): not documented anywhere I could check; diagram 32/33 show only what Docker's docs state.
- TUN vs TAP comparison and the app/OS/Tailscale/network sequence (deep dive L610-630, L934-952): text is clear without a figure; diagram 14 covers the packet path.
- Small inline ASCII (routing-table rows, `ip` output, MAC table lines): code blocks are the right format.

## Regenerating

Only needed if you want to change a diagram *as code*; for ordinary edits use excalidraw.com.

```bash
cd diagrams/tools
npm install            # pinned: excalidraw 0.18.1, react 18, esbuild, playwright
npx playwright install chromium   # once, if you have no Chromium
node build.mjs         # bundles Excalidraw's library
python3 make.py        # all diagrams   (or: python3 make.py 26 27)
node validate.cjs ../excalidraw/*.excalidraw   # confirm every file loads in Excalidraw
```

Output goes to `excalidraw/` and `svg/`. Each run re-rolls the hand-drawn jitter (Excalidraw seeds shapes randomly), so regenerated SVGs differ byte-for-byte from the committed ones while looking the same. Diagrams are defined in `tools/part*.py` with a small DSL in `tools/dsl.py` (boxes, arrows, zones, notes).

## Gallery

### Part 1 - Reachability: hops, NAT, CGNAT

<img src="svg/01-network-topologies.svg" alt="Client-server vs hub-and-spoke vs mesh" width="900">

<img src="svg/02-packet-path-hops.svg" alt="Your PC to a friend's PC as a chain of hops, with the CGNAT hop called out" width="900">

<img src="svg/03-layers-and-encapsulation.svg" alt="The 7 layers next to the nested Ethernet / IP / TCP envelope" width="900">

<img src="svg/04-local-or-remote-delivery.svg" alt="Subnet-mask decision: deliver directly (ARP the destination) or via the gateway (ARP the router)" width="900">

<img src="svg/05-what-changes-per-hop.svg" alt="IP stays, MACs change at every hop, NAT rewrites the source" width="900">

<img src="svg/06-nat-translation.svg" alt="NAT table, outbound rewrite, return path, and the unsolicited packet that dies" width="900">

<img src="svg/07-nat-behaviours.svg" alt="Full cone / restricted / port-restricted / symmetric" width="900">

<img src="svg/08-cgnat-double-nat.svg" alt="Two NATs in a row; why port forwarding is useless; the 100.64.0.0/10 overlap with Tailscale" width="900">

### Part 2 - How Tailscale connects

<img src="svg/09-port-forwarding.svg" alt="A static rule in your own NAT, and its four limits" width="900">

<img src="svg/10-stun-and-coordination.svg" alt="Step 1 STUN (find my public address), step 2 coordination server (swap endpoints + keys)" width="900">

<img src="svg/11-hole-punching.svg" alt="Sequence: both sides send first, both NATs open a door (disco ping/pong)" width="900">

<img src="svg/12-tailscale-connection-lifecycle.svg" alt="Relay first (DERP bootstrap), probe in parallel, upgrade to direct, retry every minute" width="900">

<img src="svg/13-derp-relay.svg" alt="DERP forwards ciphertext by destination public key; outbound HTTPS only" width="900">

<img src="svg/14-tailscale-packet-path-tun.svg" alt="TUN device + userspace WireGuard (normal mode) vs userspace-networking mode" width="900">

### Part 3 - Swarm basics

<img src="svg/15-swarm-vocabulary.svg" alt="Cluster, node, manager, worker, service, task/replica, desired state" width="900">

<img src="svg/16-swarm-ports-who-talks-to-whom.svg" alt="2377 / 7946 / 4789 and the published port, per link" width="900">

<img src="svg/17-raft-quorum.svg" alt="Leader / followers, Swarm's real timing, quorum table" width="900">

<img src="svg/18-gossip-fan-out.svg" alt="Epidemic spread in O(log N) rounds" width="900">

<img src="svg/19-ingress-routing-mesh.svg" alt="Any node accepts the published port and forwards over VXLAN" width="900">

### Part 4 - Containers and overlay networks

<img src="svg/20-containers-vs-vms.svg" alt="Shared kernel vs a kernel per VM" width="900">

<img src="svg/21-namespaces-and-cgroups.svg" alt="Namespaces (view) + cgroups (budget) + OverlayFS" width="900">

<img src="svg/22-containers-on-one-host.svg" alt="veth pairs to docker0, NAT out. Same-host containers CAN talk" width="900">

<img src="svg/23-containers-on-two-hosts.svg" alt="Why the same trick fails across hosts (no route, same IPs, NAT)" width="900">

<img src="svg/24-overlay-vs-underlay.svg" alt="Virtual LAN over the real network" width="900">

<img src="svg/25-what-swarm-init-creates.svg" alt="CA + Raft, ports, ingress (VNI 4096), docker_gwbridge; container eth0 + eth1" width="900">

<img src="svg/26-vxlan-encapsulation.svg" alt="MAC-in-UDP before/after, with the 50-byte MTU cost" width="900">

<img src="svg/27-overlay-anatomy-inside-a-host.svg" alt="Container netns / overlay netns (br0, vxlan0) / host netns, real names" width="900">

<img src="svg/28-how-the-vtep-knows-where-containers-are.svg" alt="Peer DB fills FDB + neighbour tables; ARP proxy answers locally" width="900">

<img src="svg/29-packet-journey-container-to-container.svg" alt="The 10-step journey across two hosts" width="900">

<img src="svg/30-same-host-vs-cross-host-overlay.svg" alt="Same host skips VXLAN (tested); cross host uses it" width="900">

<img src="svg/31-vni-keeps-overlays-apart.svg" alt="VNI check: deliver / deliver / discard" width="900">

### Part 5 - Docker Desktop and WSL2 (documented vs hypothesis)

<img src="svg/32-docker-desktop-what-the-docs-say.svg" alt="Only what Docker's docs state: host processes, AF_VSOCK channel, VM, docker0" width="900">

<img src="svg/33-docker-desktop-egress-and-published-ports.svg" alt="Outbound and published-port paths through the host process" width="900">

<img src="svg/34-docker-desktop-as-a-swarm-node-documented-vs-hypothesis.svg" alt="Facts (green) and untested hypotheses (red), plus the experiment that would settle it" width="900">

<img src="svg/35-wsl2-architecture.svg" alt="One WSL2 VM and kernel, several distros; NAT vs mirrored; systemd; coexistence warning" width="900">

<img src="svg/36-proxy-types.svg" alt="Forward / reverse / transparent proxy, and NAT as a non-proxy" width="900">

### Part 6 - The setup and the hands-on path

<img src="svg/37-the-solution-docker-engine-plus-tailscale-in-wsl2.svg" alt="Three PCs, WSL2 Ubuntu each, direct tunnels and a DERP-relayed pair" width="900">

<img src="svg/38-mtu-budget-container-to-wire.svg" alt="To-scale bars: 1450 default overflows 1280; with the option 1230 + 50 = 1280, + WireGuard 1360 < 1500" width="900">

<img src="svg/39-where-to-filter-swarm-ports.svg" alt="The cloud firewall sees only the outer packet; filter on tailscale0 in the host" width="900">

<img src="svg/40-hands-on-flow.svg" alt="Steps 5A-5H, each with its check" width="900">

<img src="svg/41-concept-ladder-reading-map.svg" alt="Ten rungs, each answering the question the last leaves open" width="900">
