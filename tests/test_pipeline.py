import json
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"tools"))
from contract import COLUMNS, KEYS, PAIRS, SNAPSHOT, SANITY, read_tables, hashes, timestamps, rule_masks, validation_errors, conflict_mask
from synthetic_data_generator import simulate, inject_defects, fingerprints
from assess_data_quality import assess
from clean_data import clean
from verified_metrics import summarize, ticket_metrics, workforce_metrics
from staffing_analysis import estimate

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=read_tables()
        cls.processed=read_tables("processed")
        cls.cleaned,cls.quarantine,cls.audit=clean(cls.raw)
        cls.manifest=json.loads((ROOT/"data/analytics/generation_metadata.json").read_text())

    def test_generation_reproducibility_and_pristine_contract(self):
        first=simulate(self.manifest["parameters"])
        second=simulate(self.manifest["parameters"])
        self.assertEqual(fingerprints(first),fingerprints(second))
        self.assertFalse(validation_errors(first))
        self.assertEqual(len(first["tickets"]),15000)
        self.assertTrue(first["tickets"].created_at.is_monotonic_increasing)
        raw,_=inject_defects(first)
        self.assertEqual(fingerprints(raw),hashes())
        for key,(lo,hi) in SANITY.items():
            self.assertGreaterEqual(summarize(first)[key],lo,key)
            self.assertLessEqual(summarize(first)[key],hi,key)

    def test_category_pair_validation(self):
        self.assertTrue(all(pair in PAIRS for pair in zip(self.processed["tickets"].category,self.processed["tickets"].subcategory)))
        broken={n:f.copy() for n,f in self.processed.items()}
        broken["tickets"].loc[0,["category","subcategory"]]=["technical_support","payment_failed"]
        self.assertTrue(rule_masks(broken)["tickets"]["invalid_hierarchy"].iloc[0])

    def test_sla_deadline_boundaries_and_missing_events(self):
        rows=[]
        def row(age,response=None,resolution=None):
            created=SNAPSHOT-pd.Timedelta(minutes=age)
            rows.append({"ticket_id":f"X{len(rows)}","policy_id":"X","status":"closed" if resolution is not None else "open",
                "created_at":created,"first_response_at":created+pd.Timedelta(minutes=response) if response is not None else pd.NaT,
                "resolved_at":created+pd.Timedelta(minutes=resolution) if resolution is not None else pd.NaT})
        row(200,10,100)
        row(200,10+1/60,100)
        row(200,5,100+1/60)
        row(10)
        row(11)
        row(100,5)
        row(101,5)
        row(1)
        policies=pd.DataFrame([{"policy_id":"X","first_response_target_minutes":10,"resolution_target_minutes":100}])
        measured=ticket_metrics(pd.DataFrame(rows),policies)
        expected=[
            ("MET","MET","MET"),("BREACHED","MET","BREACHED"),("MET","BREACHED","BREACHED"),
            ("PENDING","PENDING","PENDING"),("BREACHED","PENDING","BREACHED"),
            ("MET","PENDING","PENDING"),("MET","BREACHED","BREACHED"),("PENDING","PENDING","PENDING"),
        ]
        self.assertEqual(list(zip(measured.fr_sla_outcome,measured.resolution_sla_outcome,measured.overall_sla_outcome)),expected)

    def test_future_events_and_completed_lifecycle_are_rejected(self):
        broken={n:f.copy() for n,f in self.processed.items()}
        ix=broken["tickets"].index[broken["tickets"].status.isin(["resolved","closed"])][0]
        broken["tickets"].loc[ix,"resolved_at"]="2026-10-02T00:00:00Z"
        self.assertTrue(rule_masks(broken)["tickets"]["resolution_order"].loc[ix])
        broken["tickets"].loc[ix,"first_response_at"]=np.nan
        self.assertTrue(rule_masks(broken)["tickets"]["completed_missing_fields"].loc[ix])

    def test_exact_and_conflicting_duplicates_do_not_select_winners(self):
        frame=pd.DataFrame({"ticket_id":["A","A","B","B"],"customer_type":["standard","standard","standard","vip"]})
        self.assertEqual(frame.duplicated().tolist(),[False,True,False,False])
        self.assertEqual(conflict_mask(frame,["ticket_id"]).tolist(),[False,False,True,True])
        q=self.quarantine["tickets"]
        ambiguous=q.loc[q.quarantine_reason.eq("conflicting_key")]
        self.assertEqual(ambiguous.groupby("ticket_id").size().unique().tolist(),[2])
        self.assertFalse(ambiguous.ticket_id.isin(self.cleaned["tickets"].ticket_id).any())

    def test_independent_assessment_and_overlap_union(self):
        before=hashes()
        rules,issues,profiles=assess(self.raw)
        self.assertEqual(before,hashes())
        issues_map={(i["dataset"],i["issue"]):i for i in issues}
        self.assertEqual(issues_map[("tickets","channel_format")]["count"],120)
        self.assertFalse(rules["ticket_work_logs"]["duplicate_entry"].any(), "Exact copies must not create a conflicting grain diagnosis")
        masks=rules["ticket_work_logs"]
        union=pd.DataFrame(masks).any(axis=1).sum()
        summed=sum(mask.sum() for mask in masks.values())
        self.assertLess(union,summed)
        observed=next(p["unique_affected_rows"] for p in profiles if p["dataset"]=="ticket_work_logs")
        self.assertEqual(observed,union)

    def test_safe_transformations_and_source_reconciliation(self):
        self.assertEqual(self.audit["transformations"]["channel_normalized"],120)
        self.assertEqual(self.audit["transformations"]["category_restored"],60)
        self.assertEqual(self.audit["transformations"]["invalid_csat_set_null"],23)
        for name in COLUMNS:
            self.assertEqual(len(self.raw[name]),len(self.cleaned[name])+len(self.quarantine[name])+self.audit["exact_copies_removed"][name])
            pd.testing.assert_frame_equal(self.processed[name],self.cleaned[name].reset_index(drop=True),check_dtype=False)
        for name in ["tickets","ticket_work_logs","workforce_daily"]:
            self.assertTrue(self.quarantine[name]["_source_row"].is_unique)
            self.assertTrue(self.quarantine[name].quarantine_reason.notna().all())

    def test_quarantine_preserves_original_fields_and_dependent_links(self):
        for name in ["tickets","ticket_work_logs","workforce_daily"]:
            q=self.quarantine[name]
            for _,row in q.iterrows():
                original=self.raw[name].loc[int(row["_source_row"])-2,COLUMNS[name]]
                for col in COLUMNS[name]:
                    self.assertTrue((pd.isna(original[col]) and pd.isna(row[col])) or original[col]==row[col],f"{name}.{col}")
        removed_pairs=set(zip(self.quarantine["workforce_daily"].agent_id,self.quarantine["workforce_daily"].work_date))
        kept_pairs=set(zip(self.cleaned["ticket_work_logs"].agent_id,self.cleaned["ticket_work_logs"].work_date))
        self.assertFalse(removed_pairs & kept_pairs)
        reasons=self.quarantine["ticket_work_logs"].quarantine_reason
        self.assertTrue(reasons.str.contains("missing_workforce").any())

    def test_clean_foreign_keys_and_all_contract_rules(self):
        self.assertEqual(validation_errors(self.processed),[])
        self.assertTrue(self.processed["tickets"].ticket_id.is_unique)
        self.assertTrue(self.processed["ticket_work_logs"].work_log_id.is_unique)
        self.assertFalse(self.processed["workforce_daily"].duplicated(KEYS["workforce_daily"]).any())

    def test_productive_utilization_above_one_and_zero_capacity(self):
        data={n:f.copy() for n,f in self.processed.items()}
        logs=data["ticket_work_logs"]
        first=logs.iloc[0]
        ix=data["workforce_daily"].index[(data["workforce_daily"].agent_id==first.agent_id) & (data["workforce_daily"].work_date==first.work_date)][0]
        data["workforce_daily"].loc[ix,"shrinkage_minutes"]=data["workforce_daily"].loc[ix,"scheduled_minutes"]-data["workforce_daily"].loc[ix,"absence_minutes"]-1
        self.assertFalse(rule_masks(data)["workforce_daily"]["invalid_capacity"].any())
        w=workforce_metrics(data)
        self.assertGreater(w.loc[ix,"utilization"],1)
        zeros=w.productive_minutes.eq(0)
        self.assertTrue(zeros.any())
        self.assertTrue(w.loc[zeros,"utilization"].isna().all())

    def test_work_logs_obey_lifecycle_hire_and_physical_attendance(self):
        rules=rule_masks(self.processed)["ticket_work_logs"]
        for rule in ["outside_lifecycle","before_hire","missing_workforce","exceeds_attendance","invalid_handling"]:
            self.assertFalse(rules[rule].any(),rule)
        broken={n:f.copy() for n,f in self.processed.items()}
        broken["ticket_work_logs"].loc[0,"handling_minutes"]=10000
        self.assertTrue(rule_masks(broken)["ticket_work_logs"]["exceeds_attendance"].iloc[0])

    def test_legitimate_long_resolutions_are_retained(self):
        t=self.cleaned["tickets"]
        duration=(timestamps(t.resolved_at)-timestamps(t.created_at)).dt.total_seconds()/86400
        self.assertTrue(duration.gt(200).any())
        self.assertFalse(self.quarantine["tickets"].quarantine_reason.str.contains("outlier|duration").any())

    def test_kpi_export_denominators_and_outcome_partitions(self):
        actual=summarize(self.processed)
        saved=pd.read_csv(ROOT/"data/analytics/verified_kpis.csv").set_index("metric").value
        for metric,value in actual.items():
            self.assertTrue(np.isclose(saved[metric],value,equal_nan=True),metric)
        for prefix in ["fr","resolution","overall"]:
            total=sum(actual[f"{prefix}_sla_{outcome}"] for outcome in ["met","breached","pending"])
            self.assertEqual(total,actual["total_tickets"])
            self.assertAlmostEqual(actual[f"{prefix}_sla_compliance"],actual[f"{prefix}_sla_met"]/actual[f"{prefix}_sla_eligible"])
        self.assertAlmostEqual(actual["csat_response_rate"],actual["csat_responses"]/actual["completed_tickets"])
        self.assertEqual(actual["backlog"],actual["open_tickets"]+actual["pending_tickets"])

    def test_staffing_forecasts_exclude_current_and_future_days(self):
        output=estimate(self.processed)
        for _,group in output.groupby(["team","weekday"]):
            self.assertTrue(group.forecast_handling_minutes.iloc[:4].isna().all())
            self.assertAlmostEqual(group.forecast_handling_minutes.iloc[4],group.handling_minutes.iloc[:4].mean())
        changed={n:f.copy() for n,f in self.processed.items()}
        last_date=changed["ticket_work_logs"].work_date.max()
        changed["ticket_work_logs"].loc[changed["ticket_work_logs"].work_date==last_date,"handling_minutes"]*=2
        revised=estimate(changed)
        pd.testing.assert_series_equal(output.forecast_handling_minutes,revised.forecast_handling_minutes)

if __name__=="__main__":
    unittest.main()



