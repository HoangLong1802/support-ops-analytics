"""Run the analytical workflow against the supplied source snapshot."""
import argparse
import runpy
import sys
import unittest
from contract import ROOT


def run(script):
    previous = sys.argv
    try:
        sys.argv = [script]
        runpy.run_path(str(ROOT / script), run_name="__main__")
    finally:
        sys.argv = previous


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", nargs="?", default="all",
                        choices=["raw", "quality", "clean", "analytics", "final", "verify", "all"])
    args = parser.parse_args()
    quality = ["src/assess_data_quality.py"]
    cleaning = ["src/clean_data.py", "src/validate_clean_data.py"]
    analytics = ["src/verified_metrics.py", "src/staffing_analysis.py", "src/build_portfolio.py", "src/case_study.py", "src/export_excel.py"]
    stages = {
        "raw": ["tools/synthetic_data_generator.py", "tools/validate_generation.py"],
        "quality": quality,
        "clean": cleaning,
        "analytics": analytics,
        "final": ["src/validate_clean_data.py"] + analytics,
        "verify": ["tools/validate_generation.py", "src/validate_clean_data.py"],
        "all": quality + cleaning + analytics,
    }
    for script in stages[args.stage]:
        run(script)
    if args.stage in {"final", "verify", "all"}:
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.discover(str(ROOT / "tests")))
        if not result.wasSuccessful():
            raise SystemExit(1)
    print("Python workflow complete. MySQL and Power BI require separate native-tool validation.")


if __name__ == "__main__":
    main()
