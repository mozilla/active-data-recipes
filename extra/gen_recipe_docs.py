import os
import shutil
import subprocess
import tempfile
from pathlib import Path

here = Path(__file__).parent.resolve()
repo_dir = here.parent
docs_dir = repo_dir / 'docs'
recipe_dirs = [p for p in repo_dir.glob('*recipes') if p.is_dir()]


def transform(path):
    mod = path.stem

    with open(path, 'r') as fh:
        contents = fh.read()

    contents = (contents
        .replace(":undoc-members:", ":no-undoc-members:")
        .replace(" module", "")
        .replace("\\_", "_")
    )

    contents = contents.splitlines()
    contents = contents[:2] + contents[5:]
    contents = [l for l in contents if ":show-inheritance:" not in l]
    contents = [l[len(mod) + 1:] if l.startswith(mod + '.') else l for l in contents]
    contents = [l[len(mod) + len('module') + 2:] if l.startswith('-') else l for l in contents]

    with open(path, 'w') as fh:
        fh.write('\n'.join(contents))


with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    for recipe_dir in recipe_dirs:
        cmd = ['sphinx-apidoc', '-o', tmpdir, recipe_dir]
        subprocess.check_call(cmd)

        path = tmpdir / (recipe_dir.name + '.rst')
        transform(path)

    for file_name in tmpdir.glob('*.rst'):
        shutil.copy(file_name, docs_dir)
