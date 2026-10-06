"""Prepare a byte-preserving manifest of public portfolio artifacts."""
import argparse
import base64
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOTS = {"data", "src", "tools", "database", "sql", "powerbi", "docs", "images", "tests", "output"}
PUBLIC_FILES = {".gitattributes", ".gitignore", "README.md", "requirements.txt"}
EXCLUDED = {"__pycache__", ".venv", ".ipynb_checkpoints"}


def prepare():
    generation = json.loads((ROOT / "data/analytics/generation_metadata.json").read_text(encoding="utf-8-sig"))
    for name, expected in generation["hashes"].items():
        assert hashlib.sha256((ROOT / "data/raw" / f"{name}.csv").read_bytes()).hexdigest() == expected
    tests = json.loads((ROOT / ".agent/test_results.json").read_text(encoding="utf-8-sig"))
    assert tests["failures"] == tests["errors"] == 0
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.as_posix() not in PUBLIC_FILES and relative.parts[0] not in PUBLIC_ROOTS:
            continue
        if any(part in EXCLUDED for part in relative.parts) or path.suffix in {".zip", ".pyc", ".log"}:
            continue
        content = path.read_bytes()
        if path.suffix == ".xlsx":
            with zipfile.ZipFile(path) as workbook:
                assert workbook.testzip() is None
                assert "xl/workbook.xml" in workbook.namelist()
        else:
            content.decode("utf-8")
        blob_sha = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        files.append({"path": relative.as_posix(), "bytes": len(content), "sha": blob_sha, "sha256": hashlib.sha256(content).hexdigest()})
    manifest = {"repository": "HoangLong1802/support-ops-analytics", "tests": tests, "files": files}
    (ROOT / ".agent/github_publish_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest))


def chunk(path, offset, count):
    relative = Path(path)
    assert not relative.is_absolute() and ".." not in relative.parts
    target = (ROOT / relative).resolve()
    assert target.is_relative_to(ROOT)
    with target.open("rb") as stream:
        stream.seek(offset)
        content = stream.read(count)
    print(json.dumps({"offset": offset, "bytes": len(content), "base64": base64.b64encode(content).decode("ascii")}))


def package():
    manifest = json.loads((ROOT / ".agent/github_publish_manifest.json").read_text(encoding="utf-8"))
    target = ROOT / ".agent/github_public_files.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in manifest["files"]:
            content = (ROOT / entry["path"]).read_bytes()
            assert hashlib.sha256(content).hexdigest() == entry["sha256"], entry["path"]
            archive.writestr(entry["path"], content)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert sorted(archive.namelist()) == sorted(entry["path"] for entry in manifest["files"])
    # Packaging establishes archive integrity, not Git authentication or push status.
    # Leave publication records and current continuity documents untouched.
    print(json.dumps({"archive": str(target), "files": len(manifest["files"]), "bytes": target.stat().st_size, "integrity": "PASS"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--count", type=int, default=36000)
    args = parser.parse_args()
    if args.package:
        package()
    elif args.small:
        manifest = json.loads((ROOT / ".agent/github_publish_manifest.json").read_text(encoding="utf-8"))
        output = [{"path": entry["path"], "base64": base64.b64encode((ROOT / entry["path"]).read_bytes()).decode("ascii")} for entry in manifest["files"] if entry["bytes"] <= 131070]
        print(json.dumps(output))
    elif args.path:
        chunk(args.path, args.offset, args.count)
    else:
        prepare()
