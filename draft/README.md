# Draft v2 of the articles

Rebuilt versions of the two articles with the diagrams from [`../diagrams/`](../diagrams) placed where they belong, each followed by a "how to read the diagram" walkthrough. The originals in the repository root are untouched.

| Draft | Replaces | Diagrams |
| --- | --- | --- |
| [`swarm-across-friends-pcs-with-tailscale.md`](swarm-across-friends-pcs-with-tailscale.md) | `Running Docker Swarm Across Friends' PCs with Tailscale.md` | 01-05, 15-41 |
| [`tailscale-nat-deep-dive.md`](tailscale-nat-deep-dive.md) | `tailscale-nat-deep-dive.md` | 06-14 |

All 41 diagrams are used exactly once.

**Same flow, with these changes** (full list at the end of the main draft, under "Change notes"):

- Added a "Swarm in 90 seconds" primer, a concept-ladder reading map and a glossary; merged duplicated explanations; removed chat-preamble leftovers.
- Applied the technical corrections (same-host container networking, VXLAN device names and flags, VNIs, MTU, Raft timing, firewall placement, Tailscale's userspace WireGuard and relay-first behaviour, WSL systemd, test order, cleanup).
- Docker Desktop internals reduced to what Docker documents. The "impossible" verdict is now a labelled hypothesis with an experiment to settle it; "Observed on version ____" placeholders mark what you can fill in from a real machine.

Section numbers in the drafts are new (the main draft runs 1 to 15); cross-references inside each draft use them.
