"""Independent expected values plus live production comparisons."""
import sys
import unittest
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from independent_validation import build, MANUAL, rows, calendar_demand, START, instant, LOCAL
from contract import read_tables
from verified_metrics import ticket_metrics, summarize

class IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build()
        cls.data = read_tables("processed")

    def test_frozen_hand_calculations_against_live_pipeline(self):
        raw = [r for r in rows("data/raw/tickets.csv") if r["ticket_id"] in MANUAL]
        actual = ticket_metrics(pd.DataFrame(raw).replace("", None), self.data["sla_policies"])
        for _,r in actual.iterrows():
            expected = MANUAL[r.ticket_id]
            self.assertEqual((r.fr_sla_outcome,r.resolution_sla_outcome,r.overall_sla_outcome),expected[2])
            if pd.notna(r.first_response_at):
                self.assertAlmostEqual(r.first_response_minutes*60,expected[0])
            if pd.notna(r.resolved_at):
                self.assertAlmostEqual(r.resolution_minutes*60,expected[1])
        self.assertEqual(len(actual),5)
        self.assertEqual(actual.completed.sum(),2)
        self.assertEqual((actual.fr_sla_outcome == "MET").sum(),4)
        self.assertEqual((actual.fr_sla_outcome == "PENDING").sum(),1)
        for field in ("resolution_sla_outcome","overall_sla_outcome"):
            self.assertEqual(tuple((actual[field] == x).sum() for x in ("MET","BREACHED","PENDING")),(1,2,2))
        scores = pd.to_numeric(actual.csat_score)
        self.assertEqual(scores.count(),1)
        self.assertEqual(scores.mean(),4)
        self.assertEqual(scores.count()/actual.completed.sum(),0.5)

    def test_independent_full_aggregate_against_live_pipeline(self):
        actual = summarize(self.data)
        for k,v in self.receipt["kpi_expected"].items():
            self.assertAlmostEqual(actual[k],v,places=9,msg=k)

    def test_join_counterexample_and_safe_grain(self):
        j = self.receipt["join_risk"]
        self.assertEqual(j["left_join_ticket_rows"],17931)
        self.assertEqual(j["excess_ticket_count"],3157)
        self.assertEqual(j["naive_resolution_breaches"],4483)
        self.assertEqual(j["correct_resolution_breaches"],3514)
        logs = self.data["ticket_work_logs"]
        t = self.data["tickets"]
        naive = t.merge(logs,on="ticket_id",how="left")
        safe = t.merge(logs.groupby("ticket_id").handling_minutes.sum(),on="ticket_id",how="left",validate="one_to_one")
        self.assertEqual(len(naive),17931)
        self.assertEqual(len(safe),14774)
        self.assertEqual(safe.handling_minutes.sum(),1211023)
        self.assertEqual(len(ticket_metrics(t,self.data["sla_policies"])),14774)

    def test_calendar_zero_day_perturbation_against_live_pipeline(self):
        data = {n:f.copy() for n,f in self.data.items()}
        data["tickets"] = data["tickets"][data["tickets"].created_at.map(
            lambda v: instant(v).astimezone(LOCAL).date()!=START)].copy()
        oracle = calendar_demand(data["tickets"].to_dict("records"))
        # First coverage day is Wednesday. It stays in weekday denominator after removal.
        self.assertEqual(oracle["Weekday"]["calendar_days"],261)
        self.assertEqual(oracle["Weekday"]["zero_ticket_days"],1)
        expected = oracle["Weekday"]["average_daily_tickets"]/oracle["Weekend"]["average_daily_tickets"]
        self.assertAlmostEqual(summarize(data)["weekday_weekend_ratio"],expected,places=12)

    def test_all_existing_bi_cohorts_independent(self):
        self.assertEqual(len(self.receipt["bi_cohort_checks"]),41)
        self.assertTrue(all(all(abs(v)<1e-9 for v in c["differences"].values())
                            for c in self.receipt["bi_cohort_checks"]))

    def test_missing_completed_resolution_is_excluded(self):
        r = self.receipt["invalid_missing_data_sample"]
        self.assertEqual(r["ticket_id"],"TKT000161")
        self.assertEqual(r["resolved_at"],"")
        self.assertNotIn(r["ticket_id"],set(self.data["tickets"].ticket_id))

if __name__ == "__main__":
    unittest.main()
