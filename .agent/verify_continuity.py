"""Read-only checks for the saved cross-machine continuity checkpoint."""
import ast
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "AGENTS.md", "STATE.md", ".agent/HANDOFF.md", ".agent/HUMAN_REVIEW.md",
    ".agent/current_plan.md", ".agent/README.md", "README.md", "requirements.txt",
    "src/run_pipeline.py", "tests/test_pipeline.py", "tests/test_outputs.py",
    "tools/synthetic_data_generator.py", "tools/validate_generation.py",
    "powerbi/data_model.md", "powerbi/measures.dax", "powerbi/dashboard_spec.md",
    "powerbi/processed_queries.pq", "output/customer_support_analysis.xlsx",
}
DISPOSABLE = {
    ".venv", "venv", "env", "python_packages", "__pycache__", ".pytest_cache",
    ".ipynb_checkpoints", ".vscode", ".idea", "_backups", "build", "dist", ".cache",
}
SECRET_PATTERNS = {
    "GitHub token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b",
    "API token": rb"\bsk-[A-Za-z0-9_-]{20,}\b",
    "AWS access key": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "Slack token": rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
    "Private key": rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # Include not-yet-staged candidates so this check also works before a commit.
    paths = sorted(set(git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
                       .decode("utf-8").rstrip("\0").split("\0")))
    require(REQUIRED.issubset(paths), f"Missing required Git artifacts: {sorted(REQUIRED - set(paths))}")
    findings = []
    credential_candidates = []
    for name in paths:
        path = ROOT / name
        parts = set(Path(name).parts)
        require(not parts.intersection(DISPOSABLE), f"Disposable artifact included: {name}")
        require(path.suffix.lower() not in {".zip", ".pyc", ".pyo", ".key", ".pem"},
                f"Sensitive or duplicate archive artifact included: {name}")
        require(not (path.name.startswith((".env", "credentials", "secrets"))),
                f"Sensitive artifact included: {name}")
        if path.suffix.lower() in {".xlsx", ".pbix", ".png"}:
            continue
        content = path.read_bytes()
        for label, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, content):
                findings.append({"path": name, "format": label})
        if re.search(rb"(?i)\b(?:password|api_key|access_token|client_secret)\s*[:=]\s*['\"][^'\"\r\n]+['\"]", content):
            credential_candidates.append(name)
        if path.suffix == ".py":
            ast.parse(content.decode("utf-8-sig"), filename=name)
    require(not findings, f"Recognizable secret formats found (values withheld): {findings}")
    require(not credential_candidates,
            f"Review possible literal credentials before publishing (values withheld): {credential_candidates}")

    generation = json.loads((ROOT / "data/analytics/generation_metadata.json").read_text())
    expected_raw = {f"data/raw/{name}.csv": value for name, value in generation["hashes"].items()}
    require(set(expected_raw) == {p for p in paths if p.startswith("data/raw/")}, "Raw schema/file set changed")
    for name, expected in expected_raw.items():
        require(sha256(ROOT / name) == expected, f"Frozen raw checksum changed: {name}")
    baseline = json.loads((ROOT / ".agent/output_baseline.json").read_text())
    data_paths = {name for name in paths if name.startswith("data/")}
    require(data_paths == set(baseline["data_hashes"]), "Saved checkpoint data artifact set changed")
    for name, expected in baseline["data_hashes"].items():
        require(sha256(ROOT / name) == expected, f"Saved checkpoint data checksum changed: {name}")

    validation = json.loads((ROOT / ".agent/output_validation.json").read_text())
    workbook = ROOT / "output/customer_support_analysis.xlsx"
    require(sha256(workbook) == validation["workbook_sha256"], "Saved checkpoint workbook checksum changed")
    with zipfile.ZipFile(workbook) as archive:
        require(archive.testzip() is None, "Workbook ZIP integrity failed")
        tree = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = [node.attrib["name"] for node in tree.findall("{*}sheets/{*}sheet")]
        charts = sum(bool(re.fullmatch(r"xl/charts/chart\d+\.xml", name)) for name in archive.namelist())
        require(sheets == validation["sheets"] and charts == validation["charts"], "Workbook contents changed")

    continuity = ["AGENTS.md", "STATE.md", ".agent/HANDOFF.md", ".agent/HUMAN_REVIEW.md", ".agent/current_plan.md"]
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"],
                             cwd=ROOT, input="\0".join(continuity).encode() + b"\0", capture_output=True)
    require(ignored.returncode == 1 and not ignored.stdout, "Continuity files must not be ignored")
    disposable_probes = [".agent/python_packages/package.py", "_backups/checkpoint.zip", ".agent/archive.zip",
                         ".venv/pyvenv.cfg", ".env", ".env.local", "credentials.json", "secrets.json",
                         "private.key", "private.pem", ".vscode/settings.json", "__pycache__/cache.pyc"]
    ignored = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"],
                             cwd=ROOT, input="\0".join(disposable_probes).encode() + b"\0", capture_output=True)
    require(ignored.returncode == 0 and set(ignored.stdout.decode().rstrip("\0").split("\0")) == set(disposable_probes),
            "Disposable or sensitive probes are not all ignored")
    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    require(not re.search(r"\.agent/|STATE\.md|AGENTS\.md|_backups", readme), "Recruiter README exposes internal navigation")
    print(json.dumps({"status": "PASS", "git_artifact_candidates": len(paths),
                      "raw_hashes_matched": len(expected_raw), "data_artifact_hashes_matched": len(data_paths),
                      "workbook_sha256": sha256(workbook), "workbook_sheets": len(sheets), "workbook_charts": charts,
                      "recognizable_secret_findings": len(findings), "literal_credential_candidates": len(credential_candidates),
                      "ignore_rules": "PASS", "python_syntax": "PASS", "readme_internal_navigation": "ABSENT",
                      "native_m_dax_sql": "NOT EXECUTED"}, indent=2))


if __name__ == "__main__":
    main()
