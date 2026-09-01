# Docker Swarm + Tailscale + WSL2

This repository is a research notebook and long-form writing project about
running Docker Swarm across machines that are connected with Tailscale,
especially when the machines use Windows, WSL2, or Docker Desktop.

The work started from a practical goal: use several friends' computers as a
small personal cloud without renting public servers. The investigation grew
into a set of articles, foundational networking guides, architecture diagrams,
source-backed claim reviews, and scripts for collecting evidence from a real
machine.

This is not an application repository. There is no service to build or deploy
from the root of the repository. The main deliverable is the explanation and
the supporting verification workflow.

## The Question

The project investigates why a multi-node Docker Swarm is straightforward on
ordinary Linux hosts but becomes difficult when the following layers are
combined:

- Docker Swarm control, discovery, and overlay networking
- Tailscale's encrypted routed mesh
- Windows and WSL2 network isolation
- Docker Desktop's managed Linux environment
- Home NAT, CGNAT, and host firewalls

The key networking paths discussed throughout the repository are the usual
Swarm defaults:

| Path | Default transport | Purpose |
| --- | --- | --- |
| Control plane | TCP 2377 | Manager and worker coordination |
| Node discovery | TCP and UDP 7946 | Membership and overlay endpoint information |
| Overlay data plane | UDP 4789 | VXLAN traffic between Swarm nodes |

These are defaults, not immutable protocol constants. Configuration and the
actual network path must be inspected rather than assumed.

## Current Conclusion

The defensible conclusion of the research is narrower than the earliest drafts:

> A default Docker Desktop WSL2/NAT setup is not equivalent to multiple
> directly reachable Linux hosts. It can therefore be a poor environment for a
> multi-node Swarm unless the advertised addresses, control ports, discovery
> traffic, overlay data path, firewall policy, and MTU are deliberately made
> reachable and tested.

Tailscale can provide a secure address and path between nodes. That path may be
direct, peer-relayed, or DERP-relayed. Tailscale solves an important
reachability problem, but it does not automatically make a Docker Desktop
Engine or its VXLAN data path reachable from other machines.

For a real multi-node experiment, the clearer designs explored here are native
Docker Engine on Linux, Docker Engine installed directly inside WSL2, separate
Linux VMs, or cloud VMs. Docker Desktop remains useful for local development
and single-node Swarm learning.

Several older reports and diagrams use stronger language such as "impossible".
The technical review documents why those claims need to be scoped. Read
[`blog_fact_check.md`](blog_fact_check.md) and [`blog_analysis.md`](blog_analysis.md)
before treating the older material as an implementation guide.

## Where To Start

Choose the path that matches your goal:

1. **Understand the whole study plan:** read [`guides/README.md`](guides/README.md).
2. **Read the main story:** read [`blog.md`](blog.md).
3. **Understand NAT and Tailscale:** read [`blog_1.md`](blog_1.md).
4. **Check technical accuracy:** read [`blog_fact_check.md`](blog_fact_check.md), then [`blog_analysis.md`](blog_analysis.md).
5. **Inspect the verification approach:** read [`blog_verification_tests.md`](blog_verification_tests.md), then [`scripts/README.md`](scripts/README.md).
6. **See the architecture visually:** read [`docker_architecture_diagrams.md`](docker_architecture_diagrams.md).

For a shorter learning route, use the guides in this order:

1. [`01_linux_network_namespaces.md`](guides/01_linux_network_namespaces.md)
2. [`02_wsl2_architecture.md`](guides/02_wsl2_architecture.md)
3. [`06_docker_desktop_architecture.md`](guides/06_docker_desktop_architecture.md)
4. [`05_docker_swarm_mode.md`](guides/05_docker_swarm_mode.md)
5. [`03_overlay_networks_vxlan.md`](guides/03_overlay_networks_vxlan.md)
6. [`04_tailscale_fundamentals.md`](guides/04_tailscale_fundamentals.md)
7. [`07_socket_binding.md`](guides/07_socket_binding.md)
8. [`08_vpn_container_integration.md`](guides/08_vpn_container_integration.md)
9. [`09_k3s_alternative.md`](guides/09_k3s_alternative.md)

## Repository Map

| Path | What it contains |
| --- | --- |
| [`blog.md`](blog.md) | Main long-form draft covering reachability, NAT, Swarm ports, containers, overlay networks, VXLAN, Docker Desktop, WSL2, and possible deployment approaches. |
| [`blog_1.md`](blog_1.md) | Companion deep dive into NAT, port forwarding, VPNs, Tailscale connection establishment, DERP relays, TUN interfaces, routing, and CIDR. |
| [`blog_1_check.md`](blog_1_check.md) | Working/check copy of the NAT and Tailscale companion material. |
| [`guides/`](guides/README.md) | Beginner-friendly, hands-on study material for Linux networking, WSL2, VXLAN, Tailscale, Swarm, Docker Desktop, VPN integration, and k3s. |
| [`claims/`](claims/) | Detailed claim inventories, architecture reports, source-based takeaways, and alternate/remixed analysis documents. |
| [`blog_fact_check.md`](blog_fact_check.md) | Line-oriented technical fact check with verdicts, corrections, and links to Docker, Microsoft, Tailscale, WireGuard, Linux, RFC, and Moby sources. |
| [`blog_analysis.md`](blog_analysis.md) | Higher-level editorial and technical assessment of the two blog drafts. |
| [`blog_verification_tests.md`](blog_verification_tests.md) | Purpose, behavior, safety notes, claim-to-test mapping, and validation status for the scripts. |
| [`docker_architecture_diagrams.md`](docker_architecture_diagrams.md) | Mermaid diagrams for native Linux Docker, Docker Desktop, WSL2, port forwarding, Swarm requirements, and packet paths. |
| [`scripts/`](scripts/README.md) | Read-only diagnostics for Windows and Linux plus an opt-in temporary overlay behavior test. |
| [`side_quest_topics.md`](side_quest_topics.md) | Additional concepts and possible deep dives, from container basics to distributed systems and k3s. |
| [`improvements.md`](improvements.md) | Categorized editing backlog and technical corrections to make. |
| [`improvement_sorted.md`](improvement_sorted.md) | The same improvement work organized by its location in the main article. |
| [`clean_encoding.py`](clean_encoding.py) | A small maintenance utility for replacing selected Unicode and mojibake characters in the two main drafts. |

### Guide Status

The guide index also mentions planned guides for iptables/NAT, native Docker
Engine, and distributed systems. The corresponding files are not currently in
this checkout, so those links in `guides/README.md` should be treated as
roadmap items rather than completed documents.

## Verification Workflow

The repository separates observation from active testing.

### Read-only diagnostics

The diagnostic scripts inspect the current machine and do not provision a
cluster. They collect available information about:

- Docker Engine and Swarm state
- Nodes, managers, services, and overlay networks
- `ingress` and `docker_gwbridge`
- Linux routes, policy rules, listeners, VXLAN links, FDB entries, and bridges
- Windows listeners, adapters, WSL state, and firewall profiles
- Tailscale status, addresses, `netcheck`, and path-aware `tailscale ping`
- Optional TCP reachability to a peer on ports 2377 and 7946

On Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-blog-claims.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-blog-claims.ps1 -Distro Ubuntu-22.04 -Peer 100.64.1.2
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-blog-claims.ps1 -Distro Ubuntu-22.04 -OutputPath .\verification.txt
```

On Linux or in WSL:

```bash
bash scripts/verify-blog-claims.sh
bash scripts/verify-blog-claims.sh --peer 100.64.1.2
bash scripts/verify-blog-claims.sh --peer peer.example.ts.net --output verification.txt
```

The scripts skip unavailable commands where possible and record command
failures rather than treating one missing tool as a complete test failure.

### Active overlay behavior test

[`test-swarm-overlay.sh`](scripts/test-swarm-overlay.sh) requires a reachable
Swarm manager. It temporarily creates:

- One overlay network
- One BusyBox HTTP server service
- One BusyBox client service

The client must resolve the server by Docker service name and receive the exact
body `swarm-overlay-ok`.

Run a local or single-node test:

```bash
bash scripts/test-swarm-overlay.sh
```

Request placement on two distinct nodes:

```bash
bash scripts/test-swarm-overlay.sh --server-node manager1 --client-node worker1
```

The script removes its temporary services and network with an exit trap. It
does not run `docker system prune` and does not intentionally remove unrelated
Docker resources.

## What The Tests Do Not Prove

A successful command or local listener is only evidence about the current
machine and path. The scripts do not prove all of the following:

- Every Swarm port is reachable end to end
- UDP 7946, UDP 4789, or UDP 41641 works across the complete path
- A Tailscale connection is direct rather than relayed
- A selected MTU works for every packet size
- A router or ISP will permit the same traffic in another topology
- Future Swarm replicas will be placed on the same nodes
- Docker overlay encryption was enabled

Use `tailscale ping`, `tailscale netcheck`, packet capture, and a real
cross-node service test when those questions matter. Review diagnostic output
before sharing it because it may contain IP addresses, hostnames, listeners,
firewall rules, and peer information.

Do not run the active overlay test against a production Swarm without approval
and a maintenance window.

## Current State

- The repository contains substantial educational drafts and supporting guides.
- The claims review and technical analysis identify where the drafts are sound,
  conditional, outdated, or too strong.
- The diagnostic scripts have been checked for Bash syntax, PowerShell parsing,
  usage/help behavior, and whitespace errors.
- The active overlay test was not executed in the documented environment because
  there was no active, reachable Swarm manager.
- The articles still need revision before they should be treated as a polished
  technical runbook.

## Scope And Non-goals

This repository is intended to explain and validate a networking problem. It
does not currently provide:

- A production-ready Swarm deployment
- Infrastructure provisioning for hosts, firewalls, or Tailscale
- A Compose or Stack file for a particular application
- Automated proof that every Docker Desktop or WSL2 version behaves identically

The commands and diagrams are educational or diagnostic. Version, networking
mode, firewall policy, topology, and measured path should be recorded before
turning them into deployment instructions.

## Useful External Documentation

- [Docker Swarm mode](https://docs.docker.com/engine/swarm/swarm-mode/)
- [Docker Swarm networking](https://docs.docker.com/engine/swarm/networking/)
- [Docker networking on Docker Desktop](https://docs.docker.com/desktop/features/networking/)
- [Microsoft WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Tailscale connection types](https://tailscale.com/docs/reference/connection-types)
- [Tailscale firewall ports](https://tailscale.com/kb/1082/firewall-ports)
