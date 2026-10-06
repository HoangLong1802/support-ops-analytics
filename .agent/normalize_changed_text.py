"""Remove CRLF-only whitespace warnings from changed public text, preserving data bytes."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GIT = r'C:\Program Files\Git\cmd\git.exe'
changed = subprocess.check_output([GIT, 'diff', '--name-only'], cwd=ROOT).decode().splitlines()
added = subprocess.check_output([GIT, 'ls-files', '--others', '--exclude-standard'], cwd=ROOT).decode().splitlines()
count = 0
for name in set(changed + added):
    path = (ROOT / name).resolve()
    assert path.is_relative_to(ROOT)
    if name.startswith('data/') or not path.is_file() or path.suffix not in {'.md','.sql','.dax','.py'}:
        continue
    text = path.read_text(encoding='utf-8-sig')
    path.write_bytes(text.encode('utf-8'))
    count += 1
print(f'Normalized {count} changed public text files to LF; no data files touched.')
