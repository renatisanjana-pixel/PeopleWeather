import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="People Pulse | Customer Success",
    page_icon="🟣",
    layout="wide"
)

MIN_RESPONDENTS = 5

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 3rem;}

[data-testid="stMetric"]{
    background:#ffffff;
    border:1px solid #ececf2;
    padding:12px 14px;
    border-radius:14px;
}
[data-testid="stMetricLabel"]{font-size:.86rem;}
[data-testid="stMetricValue"]{font-size:1.9rem;}

.pp-header{
    padding:22px 26px;
    border-radius:18px;
    background:linear-gradient(120deg,#4C1D95,#7C3AED,#A855F7);
    color:white;
    margin-bottom:12px;
}
.pp-header h1{margin:0;font-size:34px;}
.pp-header p{margin:7px 0 0;opacity:.94;line-height:1.45;}

.privacy{
    display:inline-block;
    padding:7px 12px;
    border-radius:18px;
    background:#F3E8FF;
    color:#6B21A8;
    font-weight:600;
    font-size:13px;
    margin-bottom:8px;
}
.ai-good{
    padding:16px 18px;
    background:#F0FDF4;
    border-left:5px solid #22C55E;
    border-radius:12px;
    margin:8px 0;
}
.ai-watch{
    padding:16px 18px;
    background:#FFF7ED;
    border-left:5px solid #F97316;
    border-radius:12px;
    margin:8px 0;
}

/* Keep multi-select chips contained inside the filter box */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    max-height: 95px;
    overflow-y: auto;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    max-width: 135px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# QUARTER MAP
# ============================================================
QUARTER_MONTHS = {
    "Q1FY26": pd.date_range("2025-04-01", "2025-06-01", freq="MS").tolist(),
    "Q2FY26": pd.date_range("2025-07-01", "2025-09-01", freq="MS").tolist(),
    "Q3FY26": pd.date_range("2025-10-01", "2025-12-01", freq="MS").tolist(),
    "Q4FY26": pd.date_range("2026-01-01", "2026-03-01", freq="MS").tolist(),
    "Q1FY27": pd.date_range("2026-04-01", "2026-06-01", freq="MS").tolist(),
    "Q2FY27": pd.date_range("2026-07-01", "2026-09-01", freq="MS").tolist(),
    "Q3FY27": pd.date_range("2026-10-01", "2026-12-01", freq="MS").tolist(),
}


# ============================================================
# SYNTHETIC DATA
# ============================================================
@st.cache_data
def generate_data():
    rng = np.random.default_rng(42)
    n = 620
    months = pd.date_range("2025-04-01", "2026-12-01", freq="MS")

    employees = pd.DataFrame({
        "employee_id": [f"E{i:03d}" for i in range(1, n + 1)]
    })

    divisions = (
        ["Enterprise CS"] * 180 +
        ["Mid-Market CS"] * 143 +
        ["SMB CS"] * 112 +
        ["Customer Support"] * 105 +
        ["CS Operations"] * 80
    )
    rng.shuffle(divisions)
    employees["division"] = divisions

    employees["city"] = rng.choice(
        ["Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune"],
        n, p=[0.42, 0.18, 0.15, 0.15, 0.10]
    )
    employees["job_level"] = rng.choice(
        ["L1", "L2", "L3", "L4"], n, p=[0.25, 0.35, 0.25, 0.15]
    )
    employees["tenure"] = rng.choice(
        ["<1 year", "1–2 years", "2–4 years", "4+ years"],
        n, p=[0.16, 0.24, 0.35, 0.25]
    )
    employees["performance"] = rng.choice(
        ["Developing", "Strong", "Exceptional"],
        n, p=[0.10, 0.68, 0.22]
    )
    employees["talent"] = rng.choice(
        ["Core Talent", "High Potential", "Top Talent"],
        n, p=[0.72, 0.18, 0.10]
    )

    genders = np.array(["Male"] * 329 + ["Female"] * 279 + ["Others"] * 12)
    rng.shuffle(genders)
    employees["gender"] = genders

    managers = np.repeat(["Anuj", "Cassie", "Rafee", "Priya", "Zainab"], 124)
    rng.shuffle(managers)
    employees["manager"] = managers

    # Create a roughly 500-person organisation whose monthly active headcount
    # rises and falls by ~30–50 people as hiring and exits change the population.
    #
    # The wider synthetic roster is 620 unique people across the full period,
    # while active monthly headcount stays roughly in the 455–525 range.
    target_hc = {
        pd.Timestamp("2025-04-01"): 470,
        pd.Timestamp("2025-05-01"): 505,
        pd.Timestamp("2025-06-01"): 462,
        pd.Timestamp("2025-07-01"): 498,
        pd.Timestamp("2025-08-01"): 455,
        pd.Timestamp("2025-09-01"): 493,
        pd.Timestamp("2025-10-01"): 525,
        pd.Timestamp("2025-11-01"): 480,
        pd.Timestamp("2025-12-01"): 515,
        pd.Timestamp("2026-01-01"): 472,
        pd.Timestamp("2026-02-01"): 510,
        pd.Timestamp("2026-03-01"): 465,
        pd.Timestamp("2026-04-01"): 502,
        pd.Timestamp("2026-05-01"): 458,
        pd.Timestamp("2026-06-01"): 496,
        pd.Timestamp("2026-07-01"): 523,
        pd.Timestamp("2026-08-01"): 478,
        pd.Timestamp("2026-09-01"): 512,
        pd.Timestamp("2026-10-01"): 468,
        pd.Timestamp("2026-11-01"): 506,
        pd.Timestamp("2026-12-01"): 476,
    }

    # Employees receive a first-entry month. The active roster is then built
    # sequentially so people can join and leave without "disappearing and reappearing".
    # Earlier roster members start in Apr-25; later IDs enter over time.
    initial_active = set(employees["employee_id"].iloc[:target_hc[months[0]]])
    first_active_month = {eid: months[0] for eid in initial_active}
    last_active_month = {eid: months[-1] for eid in initial_active}

    inactive_pool = [eid for eid in employees["employee_id"] if eid not in initial_active]
    current_active = set(initial_active)
    active_sets = {months[0]: set(current_active)}

    for prev_month, month in zip(months[:-1], months[1:]):
        target = target_hc[month]
        current = len(current_active)

        if target > current:
            need = target - current
            add_ids = inactive_pool[:need]
            inactive_pool = inactive_pool[need:]
            for eid in add_ids:
                current_active.add(eid)
                first_active_month[eid] = month
                last_active_month[eid] = months[-1]
        elif target < current:
            need = current - target
            removable = list(current_active)
            rng.shuffle(removable)
            remove_ids = removable[:need]
            for eid in remove_ids:
                current_active.remove(eid)
                last_active_month[eid] = prev_month

        active_sets[month] = set(current_active)

    employees["join_month"] = employees["employee_id"].map(first_active_month)

    # Stable attributes for internal mobility propensity.
    employees["mobility_propensity"] = rng.random(n)

    voluntary_reasons = [
        "Better salary",
        "Taking time off for personal/medical reasons",
        "Onsite opportunity",
        "Better benefits package",
        "Pursuing passion outside of corporate",
        "Long Work Hours",
        "Culture Mismatch"
    ]

    involuntary_types = [
        "Dismissal",
        "Poor performance",
        "Layoff / Retrenchment",
        "Redundancy / Restructuring",
        "End of contract",
        "Probation failure",
        "Medical / Capability separation"
    ]

    rows = []

    for _, emp in employees.iterrows():
        base_sat = rng.normal(74, 7)
        base_manager = rng.normal(76, 7)
        base_team = rng.normal(78, 7)
        base_wellbeing = rng.normal(70, 8)
        base_learning = rng.normal(72, 7)
        base_innovation = rng.normal(68, 8)
        base_inclusivity = rng.normal(77, 6)
        base_pulse = rng.normal(74, 6)
        base_11 = rng.normal(82, 8)
        base_skip = rng.normal(62, 9)
        base_coach = rng.normal(65, 9)
        base_learn_score = rng.normal(71, 7)
        base_flight = rng.normal(28, 8)

        for mi, month in enumerate(months):
            if emp["employee_id"] not in active_sets[month]:
                continue

            div = emp["division"]
            mgr = emp["manager"]

            sat = base_sat + rng.normal(0, 3)
            manager_theme = base_manager + rng.normal(0, 3)
            team = base_team + rng.normal(0, 3)
            wellbeing = base_wellbeing + rng.normal(0, 3)
            culture = rng.normal(73, 6)
            org_listening = rng.normal(70, 7)
            learning_theme = base_learning + rng.normal(0, 3)
            inclusivity = base_inclusivity + rng.normal(0, 3)
            innovation = base_innovation + rng.normal(0, 3)
            work = rng.normal(67, 7)

            team_pulse = base_pulse + rng.normal(0, 3)
            one_to_one = base_11 + rng.normal(0, 3)
            skip = base_skip + rng.normal(0, 3)
            coaching = base_coach + rng.normal(0, 3)
            learning_score = base_learn_score + rng.normal(0, 3)
            flight = base_flight + rng.normal(0, 3)

            # Enterprise pressure starts building from May 2026.
            if div == "Enterprise CS" and month >= pd.Timestamp("2026-05-01"):
                months_under_pressure = (month.year - 2026) * 12 + month.month - 5
                sat -= 5 + 0.7 * months_under_pressure
                work -= 7 + 0.7 * months_under_pressure
                wellbeing -= 6
                team_pulse -= 5
                flight += 9 + 0.8 * months_under_pressure

            # Rafee deteriorates in manager cadence.
            if mgr == "Rafee" and month >= pd.Timestamp("2026-03-01"):
                one_to_one -= 12
                manager_theme -= 9
                team_pulse -= 6
                flight += 8

            # Priya improves from Jul 2026 after coaching intervention.
            if mgr == "Priya" and month >= pd.Timestamp("2026-07-01"):
                one_to_one += 8
                coaching += 10
                team_pulse += 5
                manager_theme += 6

            # Career risk pocket.
            if emp["performance"] == "Exceptional" and emp["tenure"] == "2–4 years":
                flight += 10
                learning_theme -= 5

            if emp["talent"] == "Top Talent":
                flight += 6

            # Participation.
            participation_prob = 0.84
            if mgr == "Rafee" and month >= pd.Timestamp("2026-04-01"):
                participation_prob = 0.72
            if mgr == "Priya" and month >= pd.Timestamp("2026-07-01"):
                participation_prob = 0.91

            survey_participated = rng.random() < participation_prob

            # Attrition event.
            attrition_prob = 0.007
            if div == "Enterprise CS" and month >= pd.Timestamp("2026-06-01"):
                attrition_prob += 0.010
            if mgr == "Rafee" and month >= pd.Timestamp("2026-04-01"):
                attrition_prob += 0.006
            if emp["talent"] == "Top Talent":
                attrition_prob += 0.003

            exit_event = rng.random() < attrition_prob
            exit_type = ""
            exit_reason = ""

            if exit_event:
                if rng.random() < 0.72:
                    exit_type = "Voluntary"
                    exit_reason = rng.choice(
                        voluntary_reasons,
                        p=[0.27, 0.14, 0.12, 0.12, 0.10, 0.15, 0.10]
                    )
                else:
                    exit_type = "Involuntary"
                    exit_reason = rng.choice(
                        involuntary_types,
                        p=[0.10, 0.28, 0.16, 0.18, 0.10, 0.12, 0.06]
                    )

            # Monthly exit pipeline is a point-in-time signal.
            pipeline_prob = 0.045
            if flight >= 45:
                pipeline_prob += 0.035
            if div == "Enterprise CS" and month >= pd.Timestamp("2026-06-01"):
                pipeline_prob += 0.018
            exit_pipeline_flag = rng.random() < pipeline_prob

            # Monthly internal move event.
            move_prob = 0.018
            if emp["talent"] in ["High Potential", "Top Talent"]:
                move_prob += 0.014
            internal_move_flag = rng.random() < move_prob

            if internal_move_flag:
                movement_type = rng.choice(
                    ["IJP", "Onsite Rotation", "Role Expansion"],
                    p=[0.55, 0.25, 0.20]
                )
            else:
                movement_type = "None"

            if emp["job_level"] in ["L3", "L4"]:
                successor_coverage = rng.choice(
                    ["Ready now", "Ready <12m", "No successor"],
                    p=[0.36, 0.34, 0.30]
                )
            else:
                successor_coverage = "N/A"

            rows.append({
                "employee_id": emp["employee_id"],
                "month": month,
                "division": div,
                "city": emp["city"],
                "job_level": emp["job_level"],
                "tenure": emp["tenure"],
                "performance": emp["performance"],
                "talent": emp["talent"],
                "gender": emp["gender"],
                "manager": mgr,
                "join_month": emp["join_month"],
                "exit_pipeline_flag": exit_pipeline_flag,
                "internal_move_flag": internal_move_flag,
                "movement_type": movement_type,
                "survey_participated": survey_participated,
                "satisfaction": np.clip(sat, 0, 100),
                "theme_manager": np.clip(manager_theme, 0, 100),
                "theme_work": np.clip(work, 0, 100),
                "theme_team": np.clip(team, 0, 100),
                "theme_wellbeing": np.clip(wellbeing, 0, 100),
                "theme_culture": np.clip(culture, 0, 100),
                "theme_org_listening": np.clip(org_listening, 0, 100),
                "theme_learning": np.clip(learning_theme, 0, 100),
                "theme_inclusivity": np.clip(inclusivity, 0, 100),
                "theme_innovation": np.clip(innovation, 0, 100),
                "flight_risk": np.clip(flight, 0, 100),
                "successor_coverage": successor_coverage,
                "one_to_one": np.clip(one_to_one, 0, 100),
                "skip_level": np.clip(skip, 0, 100),
                "coaching": np.clip(coaching, 0, 100),
                "team_pulse": np.clip(team_pulse, 0, 100),
                "learning_score": np.clip(learning_score, 0, 100),
                "exit_event": int(exit_event),
                "exit_type": exit_type,
                "exit_reason": exit_reason
            })

    panel = pd.DataFrame(rows)

    role_base = {
        "Enterprise CS": 14,
        "Mid-Market CS": 10,
        "SMB CS": 8,
        "Customer Support": 12,
        "CS Operations": 6
    }

    role_rows = []
    for month in months:
        for div, base in role_base.items():
            value = base
            if div == "Enterprise CS" and month >= pd.Timestamp("2026-05-01"):
                value += 5
            role_rows.append({
                "month": month,
                "division": div,
                "open_roles": max(0, int(rng.normal(value, 2)))
            })

    open_roles = pd.DataFrame(role_rows)
    return panel, open_roles


df, open_roles_df = generate_data()


# ============================================================
# HELPERS
# ============================================================
def headcount(data):
    return data["employee_id"].nunique()

def respondents(data):
    return data.loc[data["survey_participated"], "employee_id"].nunique()

def participation(data):
    hc = headcount(data)
    return respondents(data) / hc * 100 if hc else np.nan

def survey_mean(data, col):
    if respondents(data) < MIN_RESPONDENTS:
        return np.nan
    return data.loc[data["survey_participated"], col].mean()

def pct(v, decimals=0):
    if pd.isna(v):
        return "🔒"
    return f"{v:.{decimals}f}%"

def tidy_percent_axis(fig, max_y=100, dtick=10):
    fig.update_yaxes(
        range=[0, max_y],
        tick0=0,
        dtick=dtick,
        ticksuffix="%"
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=55, b=35)
    )
    return fig

def selected_period_months(month_selection, quarter_selection):
    # Quarter selection takes precedence because it is a packaged reporting period.
    if quarter_selection:
        quarter_months = []
        for q in quarter_selection:
            quarter_months.extend(QUARTER_MONTHS[q])
        return sorted(pd.to_datetime(pd.Series(quarter_months).drop_duplicates()).tolist())

    if month_selection:
        return sorted(pd.to_datetime(month_selection))

    # Nothing selected = recent 6 months.
    return sorted(df["month"].unique())[-6:]

def apply_non_time_filters(data):
    f = data.copy()
    mapping = {
        "division": sel_division,
        "city": sel_city,
        "job_level": sel_level,
        "tenure": sel_tenure,
        "performance": sel_perf,
        "talent": sel_talent,
        "gender": sel_gender,
        "manager": sel_manager
    }
    for col, values in mapping.items():
        if values:
            f = f[f[col].isin(values)]
    return f

def period_headcount_average(data, months):
    monthly = (
        data[data["month"].isin(months)]
        .groupby("month")["employee_id"]
        .nunique()
    )
    return monthly.mean() if len(monthly) else np.nan

def period_attrition(data, months):
    period = data[data["month"].isin(months)]
    exits = period["exit_event"].sum()
    avg_hc = period_headcount_average(data, months)
    return (exits / avg_hc * 100) if avg_hc else np.nan

def compact_multiselect(label, options, key, format_func=None):
    return st.sidebar.multiselect(
        label,
        options=options,
        default=[],
        key=key,
        format_func=format_func if format_func else str,
        placeholder="All"
    )


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="pp-header">
<h1>People Pulse</h1>
<p>
Customer Success • People Health & Organisational Insights<br>
A focused view of workforce health, employee voice, talent and manager effectiveness.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="privacy">🔒 Synthetic data • No individual records shown • Minimum survey group = 5</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("Data cuts")
st.sidebar.caption(
    "Leave Month and Quarter blank to view the latest 6 months. "
    "If a Quarter is selected, it takes precedence over Month."
)

month_options = sorted(df["month"].unique(), reverse=True)
quarter_options = list(QUARTER_MONTHS.keys())[::-1]  # recent quarter first

sel_quarters = compact_multiselect(
    "Quarter",
    quarter_options,
    key="quarter_filter"
)

sel_months = compact_multiselect(
    "Month",
    month_options,
    key="month_filter",
    format_func=lambda x: pd.Timestamp(x).strftime("%b %Y")
)

def filter_options(col):
    return sorted(df[col].dropna().unique().tolist())

sel_division = compact_multiselect("Division", filter_options("division"), "division_filter")
sel_city = compact_multiselect("City", filter_options("city"), "city_filter")
sel_level = compact_multiselect("Job Level", filter_options("job_level"), "level_filter")
sel_tenure = compact_multiselect("Tenure", filter_options("tenure"), "tenure_filter")
sel_perf = compact_multiselect("Performance", filter_options("performance"), "performance_filter")
sel_talent = compact_multiselect("Talent", filter_options("talent"), "talent_filter")
sel_gender = compact_multiselect("Gender", filter_options("gender"), "gender_filter")
sel_manager = compact_multiselect("Manager", filter_options("manager"), "manager_filter")

period_months = selected_period_months(sel_months, sel_quarters)

filtered_non_time = apply_non_time_filters(df)
filtered = filtered_non_time[filtered_non_time["month"].isin(period_months)].copy()

if filtered.empty:
    st.warning("No employees match this combination of filters.")
    st.stop()

period_start = min(period_months)
period_end = max(period_months)


# ============================================================
# TABS
# ============================================================
tabs = st.tabs([
    "🏢 Organisation Overview",
    "📉 Attrition",
    "🎧 Employee Listening",
    "🌟 Talent",
    "👥 Manager Effectiveness"
])


# ============================================================
# 1. ORGANISATION OVERVIEW
# ============================================================
with tabs[0]:
    st.subheader("Organisation Overview")

    avg_hc = period_headcount_average(filtered_non_time, period_months)

    joiners = (
        filtered[
            filtered["join_month"].isin(period_months)
        ][["employee_id", "join_month"]]
        .drop_duplicates()
        .shape[0]
    )

    exit_pipeline = int(filtered["exit_pipeline_flag"].sum())
    internal_moves = int(filtered["internal_move_flag"].sum())

    roles = open_roles_df[open_roles_df["month"].isin(period_months)].copy()
    if sel_division:
        roles = roles[roles["division"].isin(sel_division)]
    open_roles = int(roles["open_roles"].sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Headcount", f"{avg_hc:.0f}")
    c2.metric("Joiners", joiners)
    c3.metric("Exit Pipeline", exit_pipeline)
    c4.metric("Open Roles", open_roles)
    c5.metric("Internal Moves", internal_moves)

    st.caption(
        "For multi-month or quarterly views: Headcount is the average monthly headcount; "
        "Joiners, Exit Pipeline, Open Roles and Internal Moves are summed across the selected months."
    )

    latest_selected_month = max(period_months)

    # Gender mix uses the latest month in the selected period.
    latest_snapshot = filtered_non_time[
        filtered_non_time["month"] == latest_selected_month
    ].copy()

    # Headcount trend ALWAYS shows six months ending in selected/latest month.
    six_month_window = list(
        pd.date_range(
            end=pd.Timestamp(latest_selected_month),
            periods=6,
            freq="MS"
        )
    )
    hc_trend_data = filtered_non_time[
        filtered_non_time["month"].isin(six_month_window)
    ].copy()

    left, right = st.columns(2)

    with left:
        gender_counts = (
            latest_snapshot.drop_duplicates("employee_id")["gender"]
            .value_counts()
            .reset_index()
        )
        gender_counts.columns = ["Gender", "Count"]

        fig = px.pie(
            gender_counts,
            names="Gender",
            values="Count",
            hole=0.52,
            title=f"Gender mix • {pd.Timestamp(latest_selected_month).strftime('%b %Y')}"
        )
        fig.update_traces(
            textinfo="percent",
            texttemplate="%{percent:.0%}"
        )
        fig.update_layout(
            legend_title_text="",
            margin=dict(l=15, r=15, t=55, b=15)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        trend = (
            hc_trend_data.groupby("month")["employee_id"]
            .nunique()
            .reindex(six_month_window)
            .reset_index()
        )
        trend.columns = ["Month", "Headcount"]
        trend["Month Label"] = trend["Month"].dt.strftime("%b %Y")

        fig = px.line(
            trend,
            x="Month Label",
            y="Headcount",
            markers=True,
            text="Headcount",
            title="Headcount trend • recent 6 months"
        )
        fig.update_traces(textposition="top center")
        fig.update_xaxes(
            title=None,
            type="category"
        )
        fig.update_yaxes(title="Headcount")
        fig.update_layout(
            margin=dict(l=20, r=20, t=55, b=35)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### AI summaries")

    positive_points = []
    watch_points = []

    move_rate = internal_moves / max(avg_hc, 1) * 100
    pipeline_rate = exit_pipeline / max(avg_hc, 1) * 100

    if move_rate >= 8:
        positive_points.append(
            f"Internal movement is active at roughly {move_rate:.0f}% of average headcount across the selected period."
        )
    if joiners >= 25:
        positive_points.append(
            f"Hiring momentum is healthy with {joiners} joiners across the selected period."
        )
    if open_roles / max(len(period_months), 1) <= 50:
        positive_points.append(
            "Average monthly open roles are at a manageable level."
        )

    if pipeline_rate >= 8:
        watch_points.append(
            f"Exit pipeline volume is elevated relative to average headcount ({pipeline_rate:.0f}%)."
        )
    if open_roles / max(len(period_months), 1) >= 55:
        watch_points.append(
            "Open-role demand is elevated and may create capacity pressure."
        )
    if joiners < 10 and len(period_months) >= 3:
        watch_points.append(
            "Joiner volume is relatively low for the selected multi-month period."
        )

    if not positive_points:
        positive_points.append("Workforce movement is broadly stable in the selected cut.")
    if not watch_points:
        watch_points.append("No major workforce pressure is visible in the selected cut.")

    st.markdown(
        '<div class="ai-good"><b>Positive signal</b><br>' +
        "<br>".join([f"• {x}" for x in positive_points]) +
        "<br><br><b>Suggested action:</b> protect internal mobility and direct hiring capacity toward the most constrained teams.</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="ai-watch"><b>Watch-out</b><br>' +
        "<br>".join([f"• {x}" for x in watch_points]) +
        "<br><br><b>Suggested action:</b> review vacancies, exit pipeline and workforce movement together before the next business review.</div>",
        unsafe_allow_html=True
    )


# ============================================================
# 2. ATTRITION
# ============================================================
with tabs[1]:
    st.subheader("Attrition")

    monthly_attr = (
        filtered.groupby("month")
        .agg(
            Exits=("exit_event", "sum"),
            HC=("employee_id", "nunique")
        )
        .reset_index()
        .sort_values("month")
    )
    monthly_attr["Attrition %"] = (
        monthly_attr["Exits"] / monthly_attr["HC"] * 100
    )
    monthly_attr["Month Label"] = monthly_attr["month"].dt.strftime("%b %Y")

    max_monthly_attr = max(5, int(np.ceil(monthly_attr["Attrition %"].max() / 5.0) * 5 + 5))

    fig = px.line(
        monthly_attr,
        x="Month Label",
        y="Attrition %",
        markers=True,
        text="Attrition %",
        title="Monthly attrition"
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="top center"
    )
    fig.update_xaxes(title=None, type="category")
    fig.update_yaxes(
        range=[0, max_monthly_attr],
        tick0=0,
        dtick=5,
        ticksuffix="%",
        title="Attrition"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
    st.plotly_chart(fig, use_container_width=True)

    # Selected period attrition = exits / average monthly headcount.
    selected_attrition = period_attrition(filtered_non_time, period_months)

    # LTM attrition is trailing 12 months ending at the latest selected month.
    ltm_months = list(
        pd.date_range(
            end=pd.Timestamp(period_end),
            periods=12,
            freq="MS"
        )
    )
    ltm_attrition = period_attrition(filtered_non_time, ltm_months)

    voluntary_count = int((filtered["exit_type"] == "Voluntary").sum())
    involuntary_count = int((filtered["exit_type"] == "Involuntary").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Selected Period Attrition", pct(selected_attrition, 1))
    c2.metric("LTM Attrition", pct(ltm_attrition, 1))
    c3.metric("Voluntary Exits", voluntary_count)
    c4.metric("Involuntary Exits", involuntary_count)

    q = filtered.copy()
    q["Quarter"] = q["month"].map({
        m: qname
        for qname, qmonths in QUARTER_MONTHS.items()
        for m in qmonths
    })

    quarterly = (
        q.dropna(subset=["Quarter"])
        .groupby("Quarter")
        .agg(
            Exits=("exit_event", "sum")
        )
        .reset_index()
    )

    q_hc_rows = []
    for qname in quarterly["Quarter"]:
        months_q = [m for m in QUARTER_MONTHS[qname] if m in filtered["month"].unique()]
        avg_q_hc = period_headcount_average(filtered_non_time, months_q)
        exits_q = quarterly.loc[quarterly["Quarter"] == qname, "Exits"].iloc[0]
        q_hc_rows.append({
            "Quarter": qname,
            "Attrition %": exits_q / avg_q_hc * 100 if avg_q_hc else np.nan
        })

    quarterly_rates = pd.DataFrame(q_hc_rows)
    quarter_order = list(QUARTER_MONTHS.keys())
    quarterly_rates["Quarter"] = pd.Categorical(
        quarterly_rates["Quarter"],
        categories=quarter_order,
        ordered=True
    )
    quarterly_rates = quarterly_rates.sort_values("Quarter")

    left, right = st.columns(2)

    with left:
        if len(quarterly_rates):
            max_q = max(5, int(np.ceil(quarterly_rates["Attrition %"].max() / 5.0) * 5 + 5))
            fig = px.bar(
                quarterly_rates,
                x="Quarter",
                y="Attrition %",
                text="Attrition %",
                title="Quarterly attrition"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                cliponaxis=False
            )
            fig.update_yaxes(
                range=[0, max_q],
                tick0=0,
                dtick=5,
                ticksuffix="%"
            )
            fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
            st.plotly_chart(fig, use_container_width=True)

    with right:
        mix = (
            filtered[filtered["exit_event"] == 1]["exit_type"]
            .value_counts()
            .reset_index()
        )
        mix.columns = ["Type", "Count"]

        if len(mix):
            fig = px.pie(
                mix,
                names="Type",
                values="Count",
                hole=0.55,
                title="Voluntary vs involuntary"
            )
            fig.update_traces(
                textinfo="label+percent",
                textposition="inside"
            )
            fig.update_layout(
                showlegend=False,
                margin=dict(l=15, r=15, t=55, b=15)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No exits in the selected cut.")

    voluntary = (
        filtered[
            (filtered["exit_event"] == 1) &
            (filtered["exit_type"] == "Voluntary")
        ]["exit_reason"]
        .value_counts()
        .rename_axis("Reason")
        .reset_index(name="Count")
        .sort_values("Count", ascending=True)
    )

    involuntary = (
        filtered[
            (filtered["exit_event"] == 1) &
            (filtered["exit_type"] == "Involuntary")
        ]["exit_reason"]
        .value_counts()
        .rename_axis("Reason")
        .reset_index(name="Count")
        .sort_values("Count", ascending=True)
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Top voluntary exit reasons")
        if len(voluntary):
            fig = px.bar(
                voluntary,
                x="Count",
                y="Reason",
                orientation="h",
                text="Count"
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(
                dtick=1,
                title="Exits",
                rangemode="tozero"
            )
            fig.update_yaxes(title=None)
            fig.update_layout(
                height=max(320, 48 * len(voluntary)),
                margin=dict(l=10, r=35, t=15, b=35)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No voluntary exits in this cut.")

    with right:
        st.markdown("#### Involuntary separation types")
        if len(involuntary):
            fig = px.bar(
                involuntary,
                x="Count",
                y="Reason",
                orientation="h",
                text="Count"
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_xaxes(
                dtick=1,
                title="Exits",
                rangemode="tozero"
            )
            fig.update_yaxes(title=None)
            fig.update_layout(
                height=max(320, 48 * len(involuntary)),
                margin=dict(l=10, r=35, t=15, b=35)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No involuntary exits in this cut.")


# ============================================================
# 3. EMPLOYEE LISTENING
# ============================================================
with tabs[2]:
    st.subheader("Employee Listening")

    sat = survey_mean(filtered, "satisfaction")
    part = participation(filtered)

    c1, c2 = st.columns(2)
    c1.metric("Satisfaction", pct(sat))
    c2.metric("Participation", pct(part))

    theme_map = {
        "Manager": "theme_manager",
        "Work": "theme_work",
        "Team": "theme_team",
        "Wellbeing": "theme_wellbeing",
        "Culture": "theme_culture",
        "Org Listening": "theme_org_listening",
        "Learning": "theme_learning",
        "Inclusivity": "theme_inclusivity",
        "Innovation": "theme_innovation"
    }

    theme_rows = []
    for name, col in theme_map.items():
        theme_rows.append({
            "Theme": name,
            "Sentiment": survey_mean(filtered, col)
        })

    themes = pd.DataFrame(theme_rows).dropna().sort_values("Sentiment")

    fig = px.bar(
        themes,
        x="Sentiment",
        y="Theme",
        orientation="h",
        text="Sentiment",
        title="Current theme sentiment"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_xaxes(
        range=[0, 100],
        tick0=0,
        dtick=10,
        ticksuffix="%",
        title="Positive sentiment"
    )
    fig.update_yaxes(title=None)
    fig.update_layout(
        height=470,
        margin=dict(l=20, r=35, t=55, b=35)
    )
    st.plotly_chart(fig, use_container_width=True)

    selected_theme = st.selectbox(
        "Sentiment trend theme",
        list(theme_map.keys())
    )

    # Trend follows the selected period, but uses monthly values.
    trend_rows = []
    for month, g in filtered.groupby("month"):
        val = survey_mean(g, theme_map[selected_theme])
        if not pd.isna(val):
            trend_rows.append({
                "Month": month,
                "Sentiment": val
            })

    trend_themes = pd.DataFrame(trend_rows).sort_values("Month")
    trend_themes["Month Label"] = trend_themes["Month"].dt.strftime("%b %Y")

    fig = px.line(
        trend_themes,
        x="Month Label",
        y="Sentiment",
        markers=True,
        text="Sentiment",
        title=f"{selected_theme} sentiment trend"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="top center"
    )
    fig.update_xaxes(title=None, type="category")
    fig.update_yaxes(
        range=[0, 100],
        tick0=0,
        dtick=10,
        ticksuffix="%"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 4. TALENT
# ============================================================
with tabs[3]:
    st.subheader("Talent")

    # Talent snapshot uses latest month in selected period.
    latest = filtered_non_time[
        filtered_non_time["month"] == period_end
    ].copy()

    top_talent = latest[latest["talent"] == "Top Talent"]["employee_id"].nunique()
    high_risk = latest[latest["flight_risk"] >= 45]["employee_id"].nunique()

    critical_roles = latest[latest["job_level"].isin(["L3", "L4"])]
    covered = critical_roles[
        critical_roles["successor_coverage"] != "No successor"
    ]["employee_id"].nunique()
    critical_total = critical_roles["employee_id"].nunique()
    coverage = covered / critical_total * 100 if critical_total else np.nan

    ijp = int((filtered["movement_type"] == "IJP").sum())
    onsite = int((filtered["movement_type"] == "Onsite Rotation").sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Top Talent", top_talent)
    c2.metric("High Flight Risk", high_risk)
    c3.metric("Successor Coverage", pct(coverage))
    c4.metric("IJP Moves", ijp)
    c5.metric("Onsite Rotations", onsite)

    left, right = st.columns(2)

    with left:
        talent_mix = (
            latest.drop_duplicates("employee_id")["talent"]
            .value_counts()
            .reset_index()
        )
        talent_mix.columns = ["Talent", "Count"]

        fig = px.bar(
            talent_mix,
            x="Talent",
            y="Count",
            text="Count",
            title=f"Talent mix • {pd.Timestamp(period_end).strftime('%b %Y')}"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        mobility = (
            filtered[filtered["movement_type"] != "None"]["movement_type"]
            .value_counts()
            .reset_index()
        )
        mobility.columns = ["Movement", "Count"]

        if len(mobility):
            fig = px.bar(
                mobility,
                x="Movement",
                y="Count",
                text="Count",
                title="Internal mobility • selected period"
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No internal mobility in the selected cut.")

    risk_by_talent = (
        latest.groupby("talent")["flight_risk"]
        .mean()
        .reset_index()
        .sort_values("flight_risk", ascending=False)
    )

    fig = px.bar(
        risk_by_talent,
        x="talent",
        y="flight_risk",
        text="flight_risk",
        title="Flight risk by talent segment"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_yaxes(
        range=[0, 100],
        tick0=0,
        dtick=10,
        ticksuffix="%"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 5. MANAGER EFFECTIVENESS
# ============================================================
with tabs[4]:
    st.subheader("Manager Effectiveness")

    manager_rows = []

    for mgr, g in filtered.groupby("manager"):
        manager_rows.append({
            "Manager": mgr,
            "HC": headcount(g),
            "Respondents": respondents(g),
            "1:1 Coverage": survey_mean(g, "one_to_one"),
            "Skip Levels": survey_mean(g, "skip_level"),
            "Coaching": survey_mean(g, "coaching"),
            "Team Pulse": survey_mean(g, "team_pulse"),
            "Learning Score": survey_mean(g, "learning_score")
        })

    mgr_df = pd.DataFrame(manager_rows)

    display_mgr = mgr_df.copy()
    for col in ["1:1 Coverage", "Skip Levels", "Coaching", "Team Pulse", "Learning Score"]:
        display_mgr[col] = display_mgr[col].apply(lambda x: "🔒" if pd.isna(x) else f"{x:.0f}%")

    st.dataframe(
        display_mgr,
        use_container_width=True,
        hide_index=True
    )

    metric_choice = st.selectbox(
        "Manager metric",
        ["1:1 Coverage", "Skip Levels", "Coaching", "Team Pulse", "Learning Score"]
    )

    plot_df = mgr_df.dropna(subset=[metric_choice]).sort_values(metric_choice, ascending=False)

    fig = px.bar(
        plot_df,
        x="Manager",
        y=metric_choice,
        text=metric_choice,
        title=f"{metric_choice} by manager"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_yaxes(
        range=[0, 100],
        tick0=0,
        dtick=10,
        ticksuffix="%"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=55, b=35))
    st.plotly_chart(fig, use_container_width=True)

    if len(plot_df):
        best = plot_df.iloc[0]
        low = plot_df.iloc[-1]

        st.markdown(
            f"""
            <div class="ai-good">
            <b>Positive signal</b><br>
            {best['Manager']} is strongest on {metric_choice} at {best[metric_choice]:.0f}%.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="ai-watch">
            <b>Watch-out</b><br>
            {low['Manager']} is lowest on {metric_choice} at {low[metric_choice]:.0f}%.
            <br><br>
            <b>Suggested action:</b> diagnose whether the gap is driven by cadence,
            capability, workload or team context before choosing an intervention.
            </div>
            """,
            unsafe_allow_html=True
        )


st.divider()
st.caption(
    "People Pulse prototype • Synthetic Customer Success data • ~500 active employees per month • "
    "No individual employee records or comments displayed."
)
