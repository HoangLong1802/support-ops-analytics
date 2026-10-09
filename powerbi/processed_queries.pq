// Each named block is a separate blank query in Power Query Advanced Editor.
// Set ProjectFolder to your repository root; helper queries have Enable load off.

// Query: ProjectFolder
"D:\Project\DA\support-ops-analytics"

// Query: ReadProcessed
(name as text, types as list) as table =>
let
    Csv = Csv.Document(File.Contents(ProjectFolder & "\data\processed\" & name & "_clean.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, types, "en-US")
in
    Typed

// Query: dim_agents
ReadProcessed("agents", {{"agent_id", type text}, {"team", type text}, {"hire_date", type date}})

// Query: dim_sla_policies
ReadProcessed("sla_policies", {{"policy_id", type text}, {"channel", type text}, {"priority", type text},
    {"first_response_target_minutes", Int64.Type}, {"resolution_target_minutes", Int64.Type}})

// Query: fact_tickets
let
    Snapshot = #datetimezone(2026, 9, 30, 17, 0, 0, 0, 0),
    Outcome = (event as nullable datetimezone, created as datetimezone, target as number) as text =>
        if event = null then
            (if Duration.TotalMinutes(Snapshot - created) > target then "BREACHED" else "PENDING")
        else if Duration.TotalMinutes(event - created) <= target then "MET" else "BREACHED",
    Source = ReadProcessed("tickets", {{"ticket_id", type text}, {"assigned_agent_id", type text},
        {"policy_id", type text}, {"channel", type text}, {"priority", type text}, {"customer_type", type text},
        {"category", type text}, {"subcategory", type text}, {"created_at", type datetimezone},
        {"first_response_at", type nullable datetimezone}, {"resolved_at", type nullable datetimezone},
        {"status", type text}, {"reopen_count", Int64.Type}, {"csat_score", type nullable number}}),
    JoinPolicy = Table.NestedJoin(Source, {"policy_id"}, dim_sla_policies, {"policy_id"}, "policy", JoinKind.LeftOuter),
    Targets = Table.ExpandTableColumn(JoinPolicy, "policy", {"first_response_target_minutes", "resolution_target_minutes"}),
    Completed = Table.AddColumn(Targets, "completed", each List.Contains({"resolved", "closed"}, [status]), type logical),
    Response = Table.AddColumn(Completed, "first_response_minutes", each
        if [first_response_at] = null then null else Duration.TotalMinutes([first_response_at] - [created_at]), type nullable number),
    Resolution = Table.AddColumn(Response, "resolution_minutes", each
        if [resolved_at] = null then null else Duration.TotalMinutes([resolved_at] - [created_at]), type nullable number),
    LocalCreated = Table.AddColumn(Resolution, "local_created", each
        DateTimeZone.RemoveZone(DateTimeZone.SwitchZone([created_at], 7)), type datetime),
    LocalDate = Table.AddColumn(LocalCreated, "local_created_date", each Date.From([local_created]), type date),
    LocalHour = Table.AddColumn(LocalDate, "local_created_hour", each Time.Hour(Time.From([local_created])), Int64.Type),
    Weekday = Table.AddColumn(LocalHour, "local_created_weekday", each Date.DayOfWeek([local_created_date], Day.Monday), Int64.Type),
    CategoryKey = Table.AddColumn(Weekday, "category_key", each [category] & "|" & [subcategory], type text),
    FR = Table.AddColumn(CategoryKey, "fr_sla_outcome", each Outcome([first_response_at], [created_at], [first_response_target_minutes]), type text),
    RS = Table.AddColumn(FR, "resolution_sla_outcome", each Outcome([resolved_at], [created_at], [resolution_target_minutes]), type text),
    Overall = Table.AddColumn(RS, "overall_sla_outcome", each
        if [fr_sla_outcome] = "BREACHED" or [resolution_sla_outcome] = "BREACHED" then "BREACHED"
        else if [completed] and [fr_sla_outcome] = "MET" and [resolution_sla_outcome] = "MET" then "MET"
        else "PENDING", type text),
    Age = Table.AddColumn(Overall, "backlog_age_minutes", each
        if [completed] then null else Duration.TotalMinutes(Snapshot - [created_at]), type nullable number),
    // Keep stored instants as UTC Date/Time after deriving local reporting attributes.
    UTC = Table.TransformColumns(Age, {
        {"created_at", each DateTimeZone.RemoveZone(DateTimeZone.SwitchZone(_, 0)), type datetime},
        {"first_response_at", each if _ = null then null else DateTimeZone.RemoveZone(DateTimeZone.SwitchZone(_, 0)), type nullable datetime},
        {"resolved_at", each if _ = null then null else DateTimeZone.RemoveZone(DateTimeZone.SwitchZone(_, 0)), type nullable datetime}})
in
    UTC

// Query: dim_categories
Table.Distinct(Table.SelectColumns(fact_tickets, {"category_key", "category", "subcategory"}))

// Query: fact_work_logs
ReadProcessed("ticket_work_logs", {{"work_log_id", type text}, {"ticket_id", type text},
    {"agent_id", type text}, {"work_date", type date}, {"handling_minutes", Int64.Type}})

// Query: fact_workforce_daily
let
    Source = ReadProcessed("workforce_daily", {{"agent_id", type text}, {"work_date", type date},
        {"scheduled_minutes", Int64.Type}, {"absence_minutes", Int64.Type}, {"shrinkage_minutes", Int64.Type}}),
    Productive = Table.AddColumn(Source, "productive_minutes", each
        [scheduled_minutes] - [absence_minutes] - [shrinkage_minutes], Int64.Type),
    Attendance = Table.AddColumn(Productive, "physical_attendance_minutes", each
        [scheduled_minutes] - [absence_minutes], Int64.Type)
in
    Attendance

// Query: dim_date
let
    Dates = List.Dates(#date(2025, 10, 1), 365, #duration(1, 0, 0, 0)),
    Source = Table.FromList(Dates, Splitter.SplitByNothing(), {"date_key"}),
    Typed = Table.TransformColumnTypes(Source, {{"date_key", type date}}),
    Year = Table.AddColumn(Typed, "calendar_year", each Date.Year([date_key]), Int64.Type),
    Month = Table.AddColumn(Year, "calendar_month", each Date.Month([date_key]), Int64.Type),
    MonthStart = Table.AddColumn(Month, "month_start", each Date.StartOfMonth([date_key]), type date),
    Weekday = Table.AddColumn(MonthStart, "weekday_number", each Date.DayOfWeek([date_key], Day.Monday), Int64.Type),
    Name = Table.AddColumn(Weekday, "weekday_name", each Date.DayOfWeekName([date_key], "en-US"), type text),
    Weekend = Table.AddColumn(Name, "is_weekend", each [weekday_number] >= 5, type logical)
in
    Weekend
