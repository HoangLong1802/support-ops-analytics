"""Compute case-study evidence from the frozen synthetic snapshot."""
import json
import sys
import numpy as np
import pandas as pd
from contract import ROOT, DAYS, ZONE, SNAPSHOT, KEYS, hashes, read_tables, rule_masks, validation_errors
from verified_metrics import summarize, ticket_metrics

def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip()+"\n", encoding="utf-8", newline="\n")


def kpi_document(k):
    """Write one contract row per published KPI, with units and null treatment."""
    from export_excel import KPI_LABELS
    rows=[]
    common="Creation cohort 01/10/2025–30/09/2026; snapshot 01/10/2026 00:00 UTC+7"
    specific={
      "total_tickets":("Quy mô ticket", "COUNT(unique retained ticket_id)", "—", "Tất cả retained tickets", "ticket", "Key thiếu/ambiguous không vào processed"),
      "completed_tickets":("Ticket đã hoàn tất", "COUNT(ticket)", "—", "status resolved/closed", "ticket", "Completed thiếu events bị quarantine"),
      "open_tickets":("Ticket trạng thái open", "COUNT(ticket)", "—", "status open", "ticket", "Không dùng SLA pending làm ticket status"),
      "pending_tickets":("Ticket trạng thái pending", "COUNT(ticket)", "—", "status pending", "ticket", "Không dùng SLA pending làm ticket status"),
      "average_first_response_minutes":("Thời gian đến phản hồi đầu", "SUM(first_response elapsed minutes)", "N observed responses", "first_response_at not null", "minute", "Loại thiếu event; không điền zero"),
      "average_resolution_hours":("Thời gian elapsed đến hoàn tất, gồm waiting", "SUM(resolution elapsed hours)", "N completed observed durations", "completed tickets", "hour", "Loại unresolved; giữ valid long tails"),
      "average_csat":("Mức hài lòng người trả lời", "SUM(valid scores)", "N valid responses", "completed, csat 1–5", "score /5", "Null/invalid không phải zero"),
      "csat_responses":("Số survey hợp lệ", "COUNT(valid CSAT)", "—", "completed, csat 1–5", "response", "Không đếm null/invalid"),
      "csat_response_rate":("Participation trong completed cohort", "N completed valid CSAT", "N completed tickets", "completed", "fraction / %", "Zero denominator → blank; null score không đếm tử số"),
      "reopened_tickets":("Ticket có ghi nhận reopen", "COUNT(ticket)", "—", "reopen_count >0", "ticket", "Không suy đoán FCR"),
      "reopen_rate":("Tỷ lệ ticket từng reopen", "N reopen_count >0", "N retained tickets", "all retained", "fraction / %", "Zero denominator → blank; không phải FCR"),
      "backlog":("Unresolved tại snapshot", "N open + pending", "—", "unresolved", "ticket", "Không suy dựng historical backlog"),
      "backlog_rate":("Tỷ trọng unresolved", "N backlog", "N retained tickets", "all retained", "fraction / %", "Zero denominator → blank"),
      "weekday_weekend_ratio":("Tỷ số average daily demand", "Weekday tickets / weekday calendar days", "Weekend tickets / weekend calendar days", "Calendar đủ 365 ngày theo contract", "ratio", "Giữ zero-ticket days; zero weekend average → blank"),
      "handling_hours":("Effort actual handlers", "SUM(work_log handling_minutes)", "60", "Retained work logs theo work date/handler", "hour", "Không dùng elapsed resolution làm effort"),
      "productive_capacity_hours":("Capacity sau absence/shrinkage", "SUM(scheduled−absence−shrinkage)", "60", "Retained workforce agent/date", "hour", "Không tự điền 9 quarantined workforce days"),
      "utilization":("Effort / productive capacity", "SUM(handling minutes)", "SUM(productive minutes)", "Actual handler/work dates", "fraction / %", "Zero capacity → blank; có thể >100%"),
      "median_team_day_utilization":("Median tỷ lệ từng team-day", "Median(team-day handling / productive)", "—", "Team-day có productive >0", "fraction / %", "Loại zero capacity; khác ratio of sums"),
    }
    for key,value in k.items():
        if key in specific:
            meaning,num,den,filt,unit,null=specific[key]
        elif key.startswith(("median_resolution","p90_resolution","p95_resolution")):
            stat=key.split("_")[0]
            meaning="Phân phối elapsed resolution, gồm waiting"
            num=f"{stat} trên danh sách completed durations; inclusive linear interpolation"
            den="—";filt="completed, observed duration";unit="hour";null="Bỏ unresolved/missing; không bỏ valid long tails"
        elif key.startswith("backlog_over_"):
            hours=key.split("_")[2]
            meaning=f"Unresolved age strictly >{hours}h";num="COUNT(ticket)";den="—";filt=f"unresolved và snapshot age >{hours}h";unit="ticket";null="Nested thresholds, không cộng thành tổng"
        else:
            prefix=key.split("_")[0]
            stage={"fr":"First Response","resolution":"Resolution","overall":"Overall"}[prefix]
            if key.endswith("compliance"):
                meaning=stage+" tuân thủ SLA";num="N MET";den="N MET + N BREACHED";unit="fraction / %";filt="Component eligible";null="PENDING loại riêng; zero denominator → blank"
            elif key.endswith("breach_rate"):
                meaning=stage+" vi phạm SLA";num="N BREACHED";den="N MET + N BREACHED";unit="fraction / %";filt="Component eligible";null="PENDING loại riêng; zero denominator → blank"
            else:
                outcome=key.split("_")[-1]
                meaning=stage+" "+outcome.upper();num="N "+("MET + BREACHED" if outcome=="eligible" else outcome.upper());den="—";unit="ticket";filt=stage+" snapshot outcome";null="Missing event: age >target → breach; age <=target → pending"
        period="Work dates 01/10/2025–30/09/2026" if key in ["handling_hours","productive_capacity_hours","utilization","median_team_day_utilization"] else common
        rows.append(dict(metric=key,label=KPI_LABELS[key],meaning=meaning,numerator=num,denominator=den,
            filters=filt,period=period,unit=unit,null_rule=null,value=value))
    pd.DataFrame(rows).to_csv(ROOT/"data/analytics/kpi_contract.csv",index=False)
    text=["# Định nghĩa KPI / KPI Definitions","",
      "Nguồn thực thi: [verified_metrics.py](../src/verified_metrics.py); [42 giá trị](../data/analytics/verified_kpis.csv) và [machine-readable contract](../data/analytics/kpi_contract.csv). Excel là summary tĩnh được export lại bằng pipeline.","",
      "SLA là cam kết mức dịch vụ theo từng policy; CSAT là điểm hài lòng 1–5. Median là trung vị; P95 là phân vị 95% trên completed durations. Elapsed resolution gồm waiting, khác handling effort. Productive capacity là scheduled time trừ absence và shrinkage (thời gian không xử lý ticket như họp/training). FTE là equivalent full-time capacity, không phải số người cần tuyển.","",
      "Snapshot: 01/10/2026 00:00 Asia/Ho_Chi_Minh = 30/09/2026 17:00 UTC. Events ở/before target là MET; missing event quá deadline là BREACHED, còn lại PENDING. Overall breach khi một component breach; MET khi completed và cả hai MET. PENDING outcome khác ticket status pending.","",
      "| KPI / ý nghĩa | Tử số / phép tính | Mẫu số | Bộ lọc | Thời gian | Đơn vị | Null / chưa đủ điều kiện |",
      "|---|---|---|---|---|---|---|"]
    for r in rows:
        text.append("| "+" | ".join([r["label"]+" — "+r["meaning"],r["numerator"],r["denominator"],r["filters"],r["period"],r["unit"],r["null_rule"]])+" |")
    text+=["","Ticket/date/owner filters là created cohort và final owner. Effort/capacity là work date và actual handler; category không tự filter workforce. Aggregate utilization là ratio of sums, không mean of percentages. Reopen Rate không phải FCR. Backlog fixed snapshot, không historical trend.","",
      "SQL P90/P95 đã dùng inclusive linear interpolation giống pandas và DAX PERCENTILEX.INC. Native MySQL/M/DAX chưa chạy; static source review không phải native validation. Counts so exact, floats rtol=1e-12 và atol=1e-9; display round 2 decimals."]
    write("docs/kpi_definitions.md","\n".join(text))

def main():
    before=hashes()
    data=read_tables("processed")
    raw=read_tables("raw")
    if validation_errors(data):
        raise ValueError(validation_errors(data))
    k=summarize(data)
    kpi_document(k)
    t=ticket_metrics(data["tickets"],data["sla_policies"])
    daily=t.groupby("local_created_date").size().reindex(DAYS,fill_value=0)
    daytypes=[]
    for label, mask in [("Weekday",DAYS.dayofweek<5),("Weekend",DAYS.dayofweek>=5)]:
        g=daily.loc[mask]
        daytypes.append(dict(day_type=label,tickets=int(g.sum()),calendar_days=len(g),
            zero_ticket_days=int(g.eq(0).sum()),average_daily_tickets=float(g.mean())))
    pd.DataFrame(daytypes).to_csv(ROOT/"data/analytics/demand_day_type.csv",index=False)
    cats=[]
    for category,g in t.groupby("category"):
        eligible=int(g.resolution_sla_outcome.ne("PENDING").sum())
        breach=int(g.resolution_sla_outcome.eq("BREACHED").sum())
        cats.append(dict(category=category,tickets=len(g),ticket_share=len(g)/len(t),
            resolution_eligible=eligible,resolution_breaches=breach,
            resolution_breach_share=breach/k["resolution_sla_breached"],
            resolution_breach_rate=breach/eligible if eligible else None))
    pd.DataFrame(cats).to_csv(ROOT/"data/analytics/category_service_summary.csv",index=False)
    tech=next(x for x in cats if x["category"]=="technical_support")
    weekday,weekend=daytypes
    claims=dict(raw_datasets=len(raw),cleaned_tickets=len(t),technical=tech,demand_day_type=daytypes,
        weekday_weekend_total_ratio=weekday["tickets"]/weekend["tickets"],
        weekday_weekend_average_ratio=k["weekday_weekend_ratio"],
        zero_ticket_days=int(daily.eq(0).sum()),
        backlog_resolution_breaches=int((~t.completed & t.resolution_sla_outcome.eq("BREACHED")).sum()),
        snapshot_local=str(SNAPSHOT.tz_convert(ZONE)),data_type="synthetic",kpis=k,
        runtime=dict(python=sys.version.split()[0],pandas=pd.__version__,numpy=np.__version__))
    write("data/analytics/case_study_claims.json",json.dumps(claims,ensure_ascii=False,indent=2))
    joined=data["tickets"].merge(data["sla_policies"],on="policy_id",how="left",validate="many_to_one",suffixes=("","_policy"))
    owned=data["tickets"].merge(data["agents"],left_on="assigned_agent_id",right_on="agent_id",how="left",validate="many_to_one")
    assert len(t)==len(joined)==len(owned)
    assert joined.first_response_target_minutes.notna().all()
    assert owned.loc[owned.assigned_agent_id.notna(),"agent_id"].notna().all()
    audit=json.loads((ROOT/"data/analytics/cleaning_audit.json").read_text())
    lines=["# Chất lượng dữ liệu / Data Quality","",
        "Dữ liệu mô phỏng, kỳ 01/10/2025–30/09/2026 theo Asia/Ho_Chi_Minh. Raw giữ nguyên. Missing hợp lệ được giữ theo lifecycle, không điền timestamp hoặc CSAT bằng mean/zero.","",
        "## Grain và reconciliation","",
        "| Dataset | Key / grain | Raw | Exact copies removed | Quarantine | Processed |",
        "|---|---|---:|---:|---:|---:|"]
    for name in raw:
        n,dup,q,p=(audit[x][name] for x in ["raw","exact_copies_removed","quarantined","processed"])
        assert n==dup+q+p
        lines.append(f"| {name} | {', '.join(KEYS[name])} | {n:,} | {dup:,} | {q:,} | {p:,} |")
    lines+=["","Mỗi raw row đi vào retained, redundant copy hoặc quarantine. Transformations không phải nhóm cộng thêm; 203 ticket được sửa một hoặc nhiều trường.","",
        "## Kiểm tra và cách xử lý","",
        "| Kiểm tra | Kết quả / số dòng ảnh hưởng | Cách xử lý | Vấn đề còn lại |","|---|---|---|---|"]
    choices={
        "exact_duplicate":("Bỏ bản sao nguyên vẹn, giữ một observation","Tách khỏi conflicting versions"),
        "conflicting_key":("Quarantine tất cả phiên bản ambiguous","Không có update timestamp để chọn winner"),
        "missing_hierarchy":("Phục hồi category nếu subcategory xác định duy nhất; còn lại quarantine","60 restored category, 60 ambiguous rows"),
        "channel_format":("Trim và lowercase","120 ticket được chuẩn hóa"),
        "invalid_csat":("Đặt score ngoài 1–5 thành null; giữ ticket","23 score không tham gia CSAT")}
    for name,rules in rule_masks(raw).items():
        for rule,mask in rules.items():
            active=mask if rule in ["exact_duplicate","conflicting_key"] else mask & ~rules["exact_duplicate"] & ~rules["conflicting_key"]
            count=int(active.sum())
            if count:
                treatment,left=choices.get(rule,("Quarantine nếu vi phạm contract; kiểm tra downstream logs","Reason counts có thể chồng lấp; distinct totals ở reconciliation"))
                lines.append(f"| {name}.{rule} | {count:,} source rows | {treatment} | {left} |")
    violations=sum(int(m.sum()) for rules in rule_masks(data).values() for m in rules.values())
    lines += [
        f"| Processed schema/types/domains/time/FKs/capacity | {violations} violations | Validate contract trên retained data | Không chứng minh tính đại diện của simulation |",
        f"| Ticket → policy join | {len(t):,} trước / {len(joined):,} sau; 0 missing targets | many_to_one, left join | Không join raw logs vào ticket counts |",
        f"| Ticket → owner join | {len(t):,} trước / {len(owned):,} sau; 0 unknown non-null owner | Giữ legitimate null owners cho unresolved cases | Final owner khác actual handler |",
        f"| Calendar coverage | {len(DAYS)} ngày; {int(daily.eq(0).sum())} zero-ticket days | Calendar từ simulation contract; giữ ngày zero trong denominator | Sau quarantine thiếu 9 workforce agent-days |",
        "","## Missing values","","| Trường | Raw missing cells | Cách xử lý |","|---|---:|---|"]
    for name,frame in raw.items():
        for col,n in frame.isna().sum().items():
            if n:
                action="Cho phép thiếu khi chưa có event/survey; kiểm tra theo status" if col in ["assigned_agent_id","first_response_at","resolved_at","csat_score"] else "Áp dụng missing_required / missing_hierarchy"
                lines.append(f"| {name}.{col} | {int(n):,} | {action} |")
    lines+=["","## Ảnh hưởng và vấn đề còn lại","",
        "Completed tickets phải có owner, response và resolution. Unresolved tickets không được có resolution hoặc CSAT. Không suy dựng lịch sử trạng thái từ snapshot hiện tại.",
        "","Quarantine: 256 ticket, 341 work log, 9 workforce row. Log reason counts là 295 unknown_ticket, 46 missing_workforce và 27 invalid_handling; chồng lấp nên không cộng thành distinct rows. Raw chỉ có 65 unknown_ticket, phần tăng sau cleaning do parent tickets bị loại.",
        "","Giữ logically valid long durations; mean resolution vì vậy lớn hơn median. Quarantine làm đổi case mix và capacity quan sát. Null CSAT không phải score 0; nonresponse giới hạn diễn giải. Kiểm tra tự động không đánh giá được mức simulation đại diện doanh nghiệp.",
        "","Bằng chứng: [contract](../src/contract.py), [cleaner](../src/clean_data.py), [quality audit](../data/analytics/quality_audit.json), [cleaning audit](../data/analytics/cleaning_audit.json), [quarantine](../data/quarantine/)."]
    write("docs/data_quality_report.md","\n".join(lines))
    write("docs/02_data_quality.md","# Chất lượng dữ liệu / Data Quality\n\n[Báo cáo đầy đủ](data_quality_report.md) ghi grain, missing, duplicate, chronology, domains, references, join checks và cách xử lý.")
    # Reference outputs are for native Desktop comparison, not native validation.
    checks=[]
    scopes=[("All",pd.Series(True,index=t.index))]
    scopes += [(f"category={v}",t.category.eq(v)) for v in sorted(t.category.unique())]
    scopes += [(f"priority={v}",t.priority.eq(v)) for v in sorted(t.priority.unique())]
    scopes += [(f"owner={v}",t.assigned_agent_id.eq(v)) for v in sorted(data["agents"].agent_id)]
    scopes += [("owner=unassigned",t.assigned_agent_id.isna())]
    months=t.local_created_date.dt.to_period("M").astype(str)
    scopes += [(f"month={v}",months.eq(v)) for v in sorted(months.unique())]
    for label,mask in scopes:
        g=t.loc[mask]
        checks.append(dict(scope=label,tickets=len(g),completed=int(g.completed.sum()),backlog=int((~g.completed).sum()),
            resolution_met=int(g.resolution_sla_outcome.eq("MET").sum()),
            resolution_breached=int(g.resolution_sla_outcome.eq("BREACHED").sum()),
            resolution_pending=int(g.resolution_sla_outcome.eq("PENDING").sum()),
            csat_responses=int(g.csat_score.count()),
            average_csat=float(g.csat_score.mean()) if g.csat_score.count() else None))
    write("powerbi/acceptance_reference.json",json.dumps(checks,ensure_ascii=False,indent=2))
    # Editorial templates contain metric tokens so reruns cannot keep stale findings.
    values=dict(k)
    values.update({"technical_tickets":tech["tickets"],"technical_eligible":tech["resolution_eligible"],
        "technical_breaches":tech["resolution_breaches"],"technical_ticket_share":tech["ticket_share"],
        "technical_breach_share":tech["resolution_breach_share"],"technical_breach_rate":tech["resolution_breach_rate"],
        "weekday_tickets":weekday["tickets"],"weekday_days":weekday["calendar_days"],"weekday_average":weekday["average_daily_tickets"],
        "weekend_tickets":weekend["tickets"],"weekend_days":weekend["calendar_days"],"weekend_average":weekend["average_daily_tickets"],
        "total_demand_ratio":claims["weekday_weekend_total_ratio"],"backlog_resolution_breaches":claims["backlog_resolution_breaches"],
        "zero_ticket_days":claims["zero_ticket_days"]})
    for src,dst in [("README.md","README.md"),("findings.md","docs/05_business_insights.md"),
                    ("case_study.md","docs/portfolio_case_study.md"),("claims.md","docs/claim_verification.md")]:
        text=(ROOT/"docs/templates"/src).read_text(encoding="utf-8")
        for key,value in values.items():
            for fmt in [",",".2f",".2%",".0f"]:
                text=text.replace("{{"+key+":"+fmt+"}}",format(value,fmt))
        import re
        if re.search(r"\{\{[^}]+\}\}",text):
            raise ValueError(f"Unresolved metric token in {src}")
        write(dst,text)
    assert hashes()==before
    print(json.dumps({"technical":tech,"day_types":daytypes,"join_counts":[len(t),len(joined),len(owned)],"raw_unchanged":True},indent=2))

if __name__=="__main__":
    main()
