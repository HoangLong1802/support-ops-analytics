"""Record a verified native Git push and refresh recovery artifacts."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '4b4c01b92883b2e0cbfb26e07b06b37a95bf2e70'
REPO = 'https://github.com/HoangLong1802/support-ops-analytics'
manifest = json.loads((ROOT / '.agent/github_publish_manifest.json').read_text(encoding='utf-8'))
files = manifest['files']
assert len(files) == 62
for item in files:
    data = (ROOT / item['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    blob = b'blob ' + str(len(data)).encode('ascii') + b'\0' + data
    assert hashlib.sha1(blob).hexdigest() == item['sha'], item['path']

archive_path = ROOT / '.agent/github_public_files.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for item in files:
        archive.write(ROOT / item['path'], item['path'])
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {item['path'] for item in files}
    for item in files:
        assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']

note = (
    '\n## GitHub publication\n'
    f'PUBLISHED: {REPO}, branch main, commit {COMMIT}.\n'
    'Native Git 2.56.0 pushed successfully. GitHub ref and all 62 remote blob hashes '
    'match the local public-file manifest; working tree clean. Raw CSV bytes preserved.\n'
    'Internal orchestration, caches and backups excluded from Git. '
    'Verified public-only archive: .agent/github_public_files.zip.\n'
    'Publication recovery: _backups/checkpoint_published.zip.\n'
)
for relative in ('STATE.md', '.agent/HANDOFF.md'):
    path = ROOT / relative
    text = path.read_text(encoding='utf-8-sig').split('\n## GitHub publication', 1)[0].rstrip()
    text = text.replace('Git unavailable; ZIP recovery used.', 'Git 2.56.0 available; native Git publication completed; ZIP recovery retained.')
    path.write_text(text + '\n' + note, encoding='utf-8')

status = {
    'status': 'PUBLISHED',
    'repository': 'HoangLong1802/support-ops-analytics',
    'branch': 'main',
    'commit': COMMIT,
    'commit_url': f'{REPO}/commit/{COMMIT}',
    'files_published': len(files),
    'remote_commit_created': True,
    'method': 'native Git 2.56.0.windows.2',
    'remote_ref_and_blob_verification': 'PASS',
    'local_manifest_and_archive_verification': 'PASS',
    'public_archive': str(archive_path),
    'recovery_archive': str(ROOT / '_backups/checkpoint_published.zip'),
}
(ROOT / '.agent/github_publish_status.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
print(f'Publication recorded: {COMMIT}; {len(files)} public files and archive verified.')
