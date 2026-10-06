"""Record confirmed publication and verify a byte-preserving public archive."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
remote = json.loads((ROOT / '.agent/remote_refinement_verification.json').read_text())
manifest = json.loads((ROOT / '.agent/github_publish_manifest.json').read_text())
assert remote['status'] == 'PASS' and remote['files'] == len(manifest['files'])
assert remote['all_remote_blob_hashes_match']
assert remote['local_git_status'] == '## main...origin/main'
archive_path = ROOT / '.agent/github_public_files.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
    for item in manifest['files']:
        path = ROOT / item['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        archive.write(path, item['path'])
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {f['path'] for f in manifest['files']}
    for item in manifest['files']:
        assert hashlib.sha256(archive.read(item['path'])).hexdigest() == item['sha256']

sha = remote['commit']
status = {
    'status':'PUBLISHED', 'repository':remote['repository'], 'branch':'main',
    'commit':sha, 'commit_url':f'https://github.com/{remote["repository"]}/commit/{sha}',
    'files_published':remote['files'], 'remote_commit_created':True,
    'method':'native Git 2.56.0.windows.2', 'remote_ref_and_blob_verification':'PASS',
    'local_manifest_and_archive_verification':'PASS',
    'public_archive':str(archive_path), 'recovery_archive':str(ROOT / '_backups/recruiter_ready.zip'),
}
(ROOT / '.agent/github_publish_status.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
path = ROOT / 'STATE.md'
text = path.read_text(encoding='utf-8').split('\n## GitHub publication',1)[0].rstrip()
text += f'''

## Portfolio refinement
Status: PASS. Audit, presentation/code refinement, full workflow/tests and preservation checks complete.
README: 897 words; five numbered analytical documents, KPI reference and lineage updated. Generation/validation tools moved to tools; SQL organized by business purpose; analytical logic and KPI definitions preserved.
14 tests passed. Clean/generation validation, links, syntax, public trace, SQL preservation and Git whitespace checks passed. All data artifact bytes, raw SHA256 values, counts and KPIs unchanged.
Power BI model/DAX/specification ready; actual PBIX, screenshots and native SQL/DAX validation remain manual. See .agent/HANDOFF.md and .agent/HUMAN_REVIEW.md.
Recovery: _backups/recruiter_ready.zip; before refinement: _backups/checkpoint_before_refinement.zip. Earlier final/published/rejected-build archives preserved.

## GitHub publication
PUBLISHED: https://github.com/{remote['repository']}, branch main, commit {sha}.
Commit title: refactor: recruiter-focused analytics portfolio.
All {remote['files']} remote blob hashes match the byte-preserving local manifest; Git working tree clean and branch synchronized. Internal orchestration, caches and backups excluded.
Verified public-only archive: .agent/github_public_files.zip.
'''
path.write_text(text, encoding='utf-8')
path = ROOT / '.agent/HANDOFF.md'
text = path.read_text(encoding='utf-8').replace(
    '_backups/recruiter_ready.zip; commit title: refactor: recruiter-focused analytics portfolio.',
    f'_backups/recruiter_ready.zip; published main commit {sha}. Commit title: refactor: recruiter-focused analytics portfolio. All {remote["files"]} remote blobs verified against local files; working tree clean.')
path.write_text(text, encoding='utf-8')
print(f'Publication recorded and public archive verified: {sha}; {remote["files"]} files.')
