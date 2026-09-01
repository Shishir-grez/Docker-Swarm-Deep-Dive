# Building a Personal Cloud from Friends' PCs

**Docker Swarm + Tailscale + WSL2 — a from-scratch engineering deep dive.**

Ever wanted your own cloud but didn't want to rent VMs? This blog is a complete
walkthrough of turning a handful of friends' home computers — sitting behind
routers, NAT, and CGNAT — into a single encrypted Docker Swarm cluster using
Tailscale.

It starts with a naive idea ("Docker Swarm is built into Docker, how hard can it
be?") and follows the author's real journey through every wall they hit:
firewalls, NAT, Docker Desktop's internal architecture, VXLAN encapsulation, and
VPN networking. By the end you'll understand *why* the naive approach fails and
have a working, step-by-step recipe for a multi-node cluster over Tailscale.

## Articles

| Article | What it covers |
| --- | --- |
| [**Running Docker Swarm Across Friends' PCs with Tailscale**](Running%20Docker%20Swarm%20Across%20Friends'%20PCs%20with%20Tailscale.md) | The main story: why Swarm, what it needs to work, why Docker Desktop can't provide it, and a full hands-on setup (install, verify, ports, MTU, init, deploy). |
| [**Tailscale & NAT Deep Dive**](tailscale-nat-deep-dive.md) | Companion reference: how NAT really works, port forwarding, hole punching, DERP relays, TUN interfaces, and how Tailscale establishes connections. |

### Main article — what you'll find inside

1. **Why Docker Swarm** — the simplest path to a self-hosted cluster vs. Kubernetes.
2. **The connectivity problem** — why two PCs behind NAT can't just talk to each other.
3. **What Swarm actually needs** — mesh topology, routability, and the three ports that make it tick (`2377` control plane, `7946` gossip, `4789` VXLAN data).
4. **Overlay networks & VXLAN, end to end** — namespaces, veth pairs, bridges, VTEPs, FDB tables, ARP proxying, and a complete packet journey across hosts.
5. **Why Docker Desktop can't form a Swarm** — the three architectural barriers (no routable IP, one-way port forwarding, outbound-only VPNKit).
6. **The solution** — Docker Engine installed directly inside WSL2 + Tailscale.
7. **The full setup** — prerequisites, connectivity checks, firewall rules, MTU tuning, `swarm init`, joining workers, deploying services, and cleanup.

### Companion deep dive — what you'll find inside

- What NAT does to packets, outbound and inbound, with the translation table.
- Full cone vs. restricted vs. symmetric NAT — and why symmetric NAT blocks P2P.
- Port forwarding: how it works, and why CGNAT/double NAT kills it.
- How Tailscale connects: control plane, STUN, UDP hole punching, DERP relays.
- TUN vs. TAP, userspace vs. kernelspace networking, per-peer `/32` routing.

## Suggested reading order

Read the **main article** first for the full story. When it references
Tailscale's internals, jump to the **deep dive** for the details, then return —
the main article links back explicitly.

If you just want a quick reference, the deep dive stands alone as a reference
for NAT and Tailscale networking.

## Who this is for

- Developers who want a free/self-hosted cluster from hardware they already own.
- Anyone running Docker Desktop who's puzzled why Swarm "just doesn't work" across machines.
- People learning Docker networking, VXLAN, or Tailscale who want the internals, not just the commands.

**Prerequisites:** familiarity with the command line. The articles explain the
networking concepts from first principles, so no networking background is required.

## Status

This is a living research-and-writing project. The articles are substantial but
still being revised; treat them as an in-depth technical guide rather than an
officially reviewed runbook. Some earlier claims ("impossible") have been
scoped down through technical review — the current conclusion is that a
default Docker Desktop/WSL2 NAT setup *can* work but only if addresses, ports,
data path, firewall policy, and MTU are deliberately configured and tested. For
the smoothest multi-node setup, the articles recommend native Docker Engine
inside WSL2 (or Linux VMs), which is what the walkthrough uses.

## External references

- [Docker Swarm mode](https://docs.docker.com/engine/swarm/swarm-mode/)
- [Docker Swarm networking](https://docs.docker.com/engine/swarm/networking/)
- [Docker networking on Docker Desktop](https://docs.docker.com/desktop/features/networking/)
- [Microsoft WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Tailscale connection types](https://tailscale.com/docs/reference/connection-types)