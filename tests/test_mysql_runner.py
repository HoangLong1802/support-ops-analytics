"""Safety and comparator tests; these do not execute MySQL."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from run_mysql import prepared, ORDER, reconcile
from independent_validation import build
class MySQLRunnerTests(unittest.TestCase):
    def test_only_fresh_project_namespace_can_be_prepared(self):
        for invalid in ("mysql","customer_support_analytics","support_ops_verify_x;DROP DATABASE mysql",
                        "support_ops_verify_X","support_ops_verify_"+"x"*64):
            with self.assertRaises(ValueError):
                prepared(ORDER[0],invalid)
        for script in ORDER:
            text=prepared(script,"support_ops_verify_unit_fixture")
            self.assertNotIn("customer_support_analytics",text)
            self.assertNotIn("__PROJECT_ROOT__",text)
            self.assertNotIn("DROP DATABASE",text.upper())
            self.assertNotIn("TRUNCATE",text.upper())
            self.assertIn("support_ops_verify_unit_fixture",text)
    def test_reconciliation_detects_wrong_or_missing_results(self):
        r=build()
        keys=["total_tickets"]+[f"{p}_sla_{o}" for p in ("fr","resolution","overall")
                               for o in ("met","breached","pending")]
        outputs={"counts":"\n".join(f"{k}\t{r['kpi_expected'][k]}" for k in keys),
                 "categories":"\n".join("\t".join(str(c[k]) for k in (
                     "category","tickets","resolution_eligible","resolution_breaches")) for c in r["category_expected"]),
                 "demand":"\n".join(name+"\t"+"\t".join(str(d[k]) for k in (
                     "tickets","calendar_days","zero_ticket_days","average_daily_tickets"))
                     for name,d in r["daily_demand"].items())}
        self.assertEqual(reconcile(outputs)["status"],"PASS")
        wrong={**outputs,"counts":outputs["counts"].replace("total_tickets\t14774","total_tickets\t14775")}
        self.assertEqual(reconcile(wrong)["status"],"FAIL")
        missing={**outputs,"demand":outputs["demand"].splitlines()[0]}
        self.assertEqual(reconcile(missing)["status"],"FAIL")
        duplicate={**outputs,"counts":outputs["counts"].replace("fr_sla_pending\t1","resolution_sla_pending\t17")}
        self.assertEqual(reconcile(duplicate)["status"],"FAIL")
if __name__=="__main__":
    unittest.main()
