"""Run ordered portfolio checkpoints and create verified recovery archives."""
import argparse
import json
import runpy
import unittest
import sys
from contract import ROOT
from recovery import backup

def run(script,*args):
    previous = sys.argv
    try:
        sys.argv = [script, *args]
        runpy.run_path(str(ROOT/"src"/script), run_name="__main__")
    finally:
        sys.argv = previous

def state(message):
    (ROOT/"STATE.md").write_text("# Project state\n\n"+message+"\n",encoding="utf-8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["raw","quality","clean","analytics","final","verify"])
    args=parser.parse_args()
    if args.stage=="raw":
        run("generate_dataset.py")
        run("validate_generation.py")
        state("Checkpoint 2 PASS: pristine validation, calibration and reproducibility verified; raw files frozen.")
        backup("checkpoint_01_raw.zip")
    elif args.stage=="quality":
        run("assess_data_quality.py")
        state("Checkpoint 3 PASS: independent raw assessment complete; checksums unchanged.")
        backup("checkpoint_02_quality.zip")
    elif args.stage=="clean":
        run("clean_data.py")
        run("validate_clean_data.py")
        state("Checkpoint 4 PASS: cleaning, dependent quarantine, source-row reconciliation and clean validation complete.")
        backup("checkpoint_03_clean.zip")
    elif args.stage=="analytics":
        run("verified_metrics.py")
        state("Checkpoint 5 PASS: MySQL scripts ready; verified Python KPI export generated. SQL execution status: scripts only.")
        backup("checkpoint_05_sql.zip")
    elif args.stage=="final":
        run("staffing_analysis.py")
        run("build_portfolio.py")
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/"tests")))
        (ROOT/".agent/test_results.json").write_text(json.dumps({"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)}), encoding="utf-8")
        assert result.wasSuccessful(), "Test suite failed"
        run("../.agent/acceptance.py")
        backup("checkpoint_final.zip")
        run("../.agent/finalize.py")
        backup("checkpoint_final.zip")
        backup("checkpoint_final.zip",parent=True)
    elif args.stage=="verify":
        run("validate_generation.py")
        run("validate_clean_data.py")
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/"tests")))
        (ROOT/".agent/test_results.json").write_text(json.dumps({"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)}), encoding="utf-8")
        assert result.wasSuccessful(), "Test suite failed"
        run("../.agent/acceptance.py")

if __name__=="__main__":
    main()



