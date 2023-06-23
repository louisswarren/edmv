#!/usr/bin/env python3

import os
import shlex
import subprocess
import sys
import tempfile
import uuid

def default_editor(path):
    editor = os.environ.get('EDITOR', 'vi')
    cmd = editor + ' ' + shlex.quote(path)
    return subprocess.call(cmd, shell=True)

def run_editor(contents, editor):
    """Co-routine for editing a temporary file. Trims trailing newline."""
    with tempfile.NamedTemporaryFile('w+', suffix='.tmp') as f:
        f.write(contents)
        f.flush()
        while True:
            if editor(f.name):
                return
            f.seek(0)
            doc = f.read()
            if not doc.replace('\n', ''):
                return
            if doc[-1] == '\n':
                doc = doc[:-1]
            yield doc

def validate_names(sources, dests):
    eprint = lambda *args: print(*args, file=sys.stderr)

    if len(dests) != len(sources):
        eprint(f"Got {len(dests)} new paths (expected {len(sources)}).")
        return False

    if (paths := [s for s, d in zip(sources, dests) if not d]):
        eprint("Cannot rename to empty path:")
        eprint("\n".join(paths))
        return False

    if (paths := {d for i, d in enumerate(dests) if d in dests[i+1:]}):
        eprint(f"Paths must all be unique:")
        eprint("\n".join(paths))
        return False

    if (paths := [d for d in dests if os.path.exists(d) and d not in sources]):
        eprint("Path already exists already:\n" + "\n".join(paths))
        return False

    return True

def prompt_abort():
    while (choice := input("Re-edit? [Y/n] ")).lower() not in 'yn':
        continue
    return choice == 'n'

def get_destinations(sources, editor):
    """Returns a list of destinations, or None if the user aborts."""
    source_doc = '\n'.join(src.replace('\n', '\0') for src in sources)
    for contents in run_editor(source_doc, editor):
        dests = [line.replace('\0', '\n') for line in contents.split('\n')]
        if validate_names(sources, dests):
            return dests
        if prompt_abort():
            break

def edmv(sources, editor = default_editor, mv = os.rename):
    dests = get_destinations(sources, editor)
    if not dests:
        return False

    undo_stack = []
    decycle_queue = []
    try:
        for s, d in zip(sources, dests):
            if s == d:
                continue
            if d in sources:
                u = str(uuid.uuid4())
                tmp = f"{d}.{u}.edmv"
                decycle_queue.append((tmp, d))
                d = tmp
            if os.path.exists(d):
                raise Exception(f"{d} already exists")
            mv(s, d)
            undo_stack.append((s, d))
        for s, d in decycle_queue:
            if os.path.exists(d):
                raise Exception(f"{d} already exists")
            mv(s, d)
            undo_stack.append((s, d))
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        if undo_stack:
            print("Undoing...", file=sys.stderr)
        while undo_stack:
            s, d = undo_stack.pop()
            mv(d, s)
        return False

    return True

if __name__ == '__main__':
    args = sys.argv[1:] or sorted(os.listdir())
    if any(not os.path.exists(s) for s in args):
        print("Error: path does not exist", file=sys.stderr)
        sys.exit(1)

    if not edmv(args):
        sys.exit(1)
