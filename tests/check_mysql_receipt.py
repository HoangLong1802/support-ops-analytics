"""CI gate: fail unless the MySQL run reconciled and database/validation.sql found no violations."""
import json
import re
import sys
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "output" / "mysql"
receipt = json.loads((out / "execution_receipt.json").read_text(encoding="utf-8"))
errors = []
if receipt["status"] != "EXECUTED_RECONCILED":
    errors.append("receipt status " + receipt["status"])
if not receipt["server_version"].startswith("8.4"):
    errors.append("server is not MySQL 8.4: " + receipt["server_version"])

text = (out / "validation.txt").read_text(encoding="utf-8")
# Zero-row checks print nothing; only the 4 summary queries may produce tables.
tables = len(re.findall(r"^\+-", text, re.M)) // 3
if tables != 4:
    errors.append(f"validation.sql returned {tables} result tables, expected 4 (extra rows = violations)")
matches = re.findall(r"\|\s*(?:agents|policies|categories|dates|tickets|work_logs|workforce)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d)\s*\|", text)
if len(matches) != 7 or set(matches) != {"1"}:
    errors.append("row-count check failed: " + str(matches))
rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*$", text, re.M)
if not rows or any(len({*r}) != 1 for r in rows):
    errors.append("join grain check failed: " + str(rows))
if len(receipt["reconciliation"]["differences"]) != 33:
    errors.append("expected 33 reconciled values")

print("\n".join(errors) or "MySQL receipt checks passed")
sys.exit(1 if errors else 0)
