"""Create self-contained recovery archives without caches or nested backups."""
from pathlib import Path
import argparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.venv', '__pycache__', '.ipynb_checkpoints', '.git', '_backups'}

def backup(name):
    target = ROOT / '_backups' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(ROOT).parts) and p.suffix not in {'.zip', '.pyc', '.log'})
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None, 'Backup checksum failure'
        assert 'STATE.md' in archive.namelist(), 'Backup is missing recovery state'
    print(f'Backup verified: {target} ({len(paths)} files, {target.stat().st_size:,} bytes)')
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    backup(args.name)
