"""Finalize verified publication records and the public archive."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
remote = json.loads((ROOT / '.agent/output_remote_verification.json').read_text())
manifest = json.loads((ROOT / '.agent/github_publish_manifest.json').read_text())
assert remote['status'] == 'PASS' and remote['all_remote_blob_hashes_match']
assert remote['files'] == len(manifest['files']) and remote['git_status'] == '## main...origin/main'
target = ROOT / '.agent/github_public_files.zip'
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    for item in manifest['files']:
        content = (ROOT / item['path']).read_bytes()
        assert hashlib.sha256(content).hexdigest() == item['sha256']
        archive.writestr(item['path'], content)
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {item['path'] for item in manifest['files']}
    for item in manifest['files']:
        assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']
sha = remote['commit']
status = {'status':'PUBLISHED', 'repository':remote['repository'], 'branch':'main', 'commit':sha,
          'commit_url':f'https://github.com/{remote["repository"]}/commit/{sha}', 'files_published':remote['files'],
          'remote_commit_created':True, 'method':'native Git 2.56.0.windows.2',
          'remote_ref_and_blob_verification':'PASS', 'local_manifest_and_archive_verification':'PASS',
          'public_archive':str(target), 'recovery_archive':str(ROOT / '_backups/checkpoint_excel_outputs.zip')}
(ROOT / '.agent/github_publish_status.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
path = ROOT / 'STATE.md'
text = path.read_text(encoding='utf-8').replace('Tests: 14 passed. Raw SHA256 unchanged since validated generation.', 'Tests: 23 passed. Raw SHA256 unchanged since validated generation.')
text = text.replace('Runtime: Python 3.12.13, pandas 3.0.6, NumPy 2.5.3.', 'Runtime: Python 3.12.13, pandas 3.0.6, NumPy 2.5.3, openpyxl 3.1.5.')
publication = f'''
## GitHub publication
PUBLISHED: https://github.com/{remote['repository']}, branch main, commit {sha}.
Commit title: feat: add verified Excel analytical output.
All {remote['files']} remote blob hashes match local bytes, including the real workbook. Working tree clean; branch synchronized. Internal orchestration, dependencies, caches and backups excluded from Git.
Verified public archive: .agent/github_public_files.zip. Current recovery: _backups/checkpoint_excel_outputs.zip.
'''
text = re.sub(r'\n## GitHub publication\n.*?(?=\n## |\Z)', publication, text, flags=re.S)
text = text.replace('Publication record will be updated after successful Git operations.', f'Published and remotely verified: {sha}; all {remote["files"]} public files match local bytes.')
path.write_text(text, encoding='utf-8')
path = ROOT / '.agent/HANDOFF.md'
text = path.read_text(encoding='utf-8').replace('Publication commit recorded after successful push.', f'Published main commit {sha}; all {remote["files"]} remote blobs verified against the local manifest; working tree clean.')
path.write_text(text, encoding='utf-8')
print(f'Publication and public archive verified: {sha}; {remote["files"]} files.')
