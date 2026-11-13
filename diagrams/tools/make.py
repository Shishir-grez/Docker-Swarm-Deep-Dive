#!/usr/bin/env python3
"""Regenerate the diagrams.

    cd diagrams/tools
    npm install && node build.mjs        # once: bundles Excalidraw's own library
    python3 make.py                      # all diagrams
    python3 make.py 26 27                # only diagrams whose file name starts with these prefixes

Writes ../excalidraw/*.excalidraw (editable in https://excalidraw.com) and ../svg/*.svg (self-contained, fonts embedded).
"""
import importlib, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dsl import add_bindings, check_layout  # noqa: E402

MODULES = ['part1_reachability', 'part2_tailscale', 'part3_swarm', 'part4_containers',
           'part5_overlay', 'part6_docker_desktop', 'part7_setup']
only = sys.argv[1:]
build = os.path.join(HERE, 'build'); specs = os.path.join(build, 'specs'); out = os.path.join(build, 'out')
for p in (specs, out): os.makedirs(p, exist_ok=True)

diagrams = []
for m in MODULES:
    for fn in importlib.import_module(m).ALL:
        d = fn()
        if only and not any(d.name.startswith(o) for o in only):
            continue
        json.dump(d.spec(), open(os.path.join(specs, d.name + '.json'), 'w'))
        diagrams.append(d)

env = dict(os.environ, OUT=out, PNG=os.environ.get('PNG', '0'))
r = subprocess.run(['node', 'render.cjs', *[os.path.join(specs, d.name + '.json') for d in diagrams]],
                   cwd=HERE, env=env, capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode: print(r.stderr[-800:]); sys.exit(r.returncode)

ex, sv = os.path.join(HERE, '..', 'excalidraw'), os.path.join(HERE, '..', 'svg')
os.makedirs(ex, exist_ok=True); os.makedirs(sv, exist_ok=True)
problems = 0
for d in diagrams:
    p = os.path.join(out, d.name + '.excalidraw')
    add_bindings(p, d.links)
    for issue in check_layout(p):
        problems += 1; print(f'  [{d.name}] {issue}')
    shutil.copy(p, ex); shutil.copy(os.path.join(out, d.name + '.svg'), sv)
print(f'{len(diagrams)} diagram(s) written; layout problems: {problems}')
