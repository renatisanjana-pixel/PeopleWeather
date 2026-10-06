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
    padding:14px 20px;
    border-radius:18px;
    background:linear-gradient(120deg,#4C1D95,#7C3AED,#A855F7);
    color:white;
    margin-bottom:12px;
}
.pp-header h1{margin:0;font-size:28px;line-height:1.1;}
.pp-header p{margin:5px 0 0;opacity:.94;line-height:1.35;font-size:0.98rem;}

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
        ["Business Engineering"] * 143 +
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
        ["Other Talent", "High Potential Talent", "Top Talent"],
        n, p=[0.70, 0.20, 0.10]
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
        pd.Timestamp("2025-04-01"): 490,
        pd.Timestamp("2025-05-01"): 505,
        pd.Timestamp("2025-06-01"): 484,
        pd.Timestamp("2025-07-01"): 502,
        pd.Timestamp("2025-08-01"): 489,
        pd.Timestamp("2025-09-01"): 511,
        pd.Timestamp("2025-10-01"): 495,
        pd.Timestamp("2025-11-01"): 516,
        pd.Timestamp("2025-12-01"): 500,
        pd.Timestamp("2026-01-01"): 512,
        pd.Timestamp("2026-02-01"): 494,
        pd.Timestamp("2026-03-01"): 520,
        pd.Timestamp("2026-04-01"): 503,
        pd.Timestamp("2026-05-01"): 519,
        pd.Timestamp("2026-06-01"): 497,
        pd.Timestamp("2026-07-01"): 515,
        pd.Timestamp("2026-08-01"): 501,
        pd.Timestamp("2026-09-01"): 523,
        pd.Timestamp("2026-10-01"): 506,
        pd.Timestamp("2026-11-01"): 520,
        pd.Timestamp("2026-12-01"): 498,
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
        base_flight = rng.normal(4.5, 1.8)

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

            # Gentle month-on-month movement (roughly 1–7 points) and
            # more visible quarter-on-quarter theme rotation.
            monthly_wave = [0, 1, -1, 2, -2, 3, -1, 4, -3, 2, 1, -2, 3, -1, 2, -3, 4, -2, 1, 3, -1]
            wave = monthly_wave[mi % len(monthly_wave)]

            sat += wave * 0.7
            manager_theme += wave * 0.6
            team += wave * 0.5
            wellbeing += wave * 0.8
            culture += wave * 0.5
            org_listening += wave * 0.6
            learning_theme += wave * 0.7
            inclusivity += wave * 0.4
            innovation += wave * 0.9
            work += wave * 0.7

            # Different listening themes lead in different quarters.
            quarter_index = mi // 3
            quarter_pattern = quarter_index % 4
            if quarter_pattern == 0:
                manager_theme += 4
                team += 3
                wellbeing -= 2
                innovation -= 1
            elif quarter_pattern == 1:
                work += 4
                learning_theme += 3
                manager_theme -= 2
                culture += 1
            elif quarter_pattern == 2:
                wellbeing += 5
                inclusivity += 3
                work -= 2
                org_listening += 1
            else:
                innovation += 5
                culture += 3
                learning_theme += 2
                wellbeing -= 2

            team_pulse = base_pulse + np.clip(wave, -3, 4) + rng.normal(0, 2.5)
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
                flight += 2.0 + 0.20 * months_under_pressure

            # Priya deteriorates in manager cadence from Mar 2026 onward.
            if mgr == "Priya" and month >= pd.Timestamp("2026-03-01"):
                one_to_one -= 12
                manager_theme -= 9
                team_pulse -= 6
                flight += 1.8

            # Rafee improves from Jul 2026 after coaching intervention.
            if mgr == "Rafee" and month >= pd.Timestamp("2026-07-01"):
                one_to_one += 8
                coaching += 10
                team_pulse += 5
                manager_theme += 6

            # Career risk pocket.
            if emp["performance"] == "Exceptional" and emp["tenure"] == "2–4 years":
                flight += 2.2
                learning_theme -= 5

            if emp["talent"] == "Top Talent":
                flight += 1.5

            # Participation deliberately varies widely across teams while
            # averaging close to 56% overall.
            manager_participation = {
                "Anuj": 0.78,
                "Cassie": 0.58,
                "Rafee": 0.54,
                "Priya": 0.04,
                "Zainab": 0.46,
            }
            monthly_participation_shift = [
                -0.03, 0.02, 0.00, 0.03, -0.02, 0.01, -0.01,
                0.02, -0.03, 0.01, 0.03, -0.02, 0.00, 0.02,
                -0.01, 0.03, -0.02, 0.01, 0.00, 0.02, -0.01
            ][mi]
            participation_prob = np.clip(
                manager_participation[mgr] + monthly_participation_shift,
                0.04,
                0.90
            )

            survey_participated = rng.random() < participation_prob

            # Attrition event.
            attrition_prob = 0.007
            if div == "Enterprise CS" and month >= pd.Timestamp("2026-06-01"):
                attrition_prob += 0.010
            if mgr == "Priya" and month >= pd.Timestamp("2026-04-01"):
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

            # Monthly exit pipeline stays within a realistic 3%-9% range.
            pipeline_prob = 0.045
            if flight >= 7:
                pipeline_prob += 0.015
            if div == "Enterprise CS" and month >= pd.Timestamp("2026-06-01"):
                pipeline_prob += 0.012
            if mgr == "Rafee":
                pipeline_prob += 0.008
            pipeline_prob = float(np.clip(pipeline_prob, 0.03, 0.09))
            exit_pipeline_flag = rng.random() < pipeline_prob

            # Monthly internal move event.
            move_prob = 0.018
            if emp["talent"] in ["High Potential Talent", "Top Talent"]:
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

    # --------------------------------------------------------
    # Controlled workforce events for a more coherent demo
    # --------------------------------------------------------
    panel["join_event"] = False

    # Controlled monthly joiners. Q2FY27 is intentionally lower at ~30 hires for the quarter.
    monthly_joiners = {
        pd.Timestamp("2025-04-01"): 15,
        pd.Timestamp("2025-05-01"): 17,
        pd.Timestamp("2025-06-01"): 16,
        pd.Timestamp("2025-07-01"): 18,
        pd.Timestamp("2025-08-01"): 15,
        pd.Timestamp("2025-09-01"): 19,
        pd.Timestamp("2025-10-01"): 16,
        pd.Timestamp("2025-11-01"): 17,
        pd.Timestamp("2025-12-01"): 18,
        pd.Timestamp("2026-01-01"): 15,
        pd.Timestamp("2026-02-01"): 20,
        pd.Timestamp("2026-03-01"): 16,
        pd.Timestamp("2026-04-01"): 17,
        pd.Timestamp("2026-05-01"): 19,
        pd.Timestamp("2026-06-01"): 15,
        pd.Timestamp("2026-07-01"): 10,
        pd.Timestamp("2026-08-01"): 10,
        pd.Timestamp("2026-09-01"): 10,
        pd.Timestamp("2026-10-01"): 17,
        pd.Timestamp("2026-11-01"): 15,
        pd.Timestamp("2026-12-01"): 18,
    }

    for month, target_joins in monthly_joiners.items():
        idx = panel.index[panel["month"] == month].to_numpy()
        chosen = rng.choice(idx, size=min(target_joins, len(idx)), replace=False)
        panel.loc[chosen, "join_event"] = True

    # Rebuild attrition events so quarterly patterns are deliberate.
    panel["exit_event"] = 0
    panel["exit_type"] = ""
    panel["exit_reason"] = ""

    monthly_total_exits = {
        # Q1FY26 - stable
        pd.Timestamp("2025-04-01"): 4,
        pd.Timestamp("2025-05-01"): 4,
        pd.Timestamp("2025-06-01"): 5,
        # Q2FY26 - normal
        pd.Timestamp("2025-07-01"): 4,
        pd.Timestamp("2025-08-01"): 5,
        pd.Timestamp("2025-09-01"): 4,
        # Q3FY26 - spike post ratings cycle
        pd.Timestamp("2025-10-01"): 8,
        pd.Timestamp("2025-11-01"): 9,
        pd.Timestamp("2025-12-01"): 9,
        # Q4FY26 - elevated
        pd.Timestamp("2026-01-01"): 7,
        pd.Timestamp("2026-02-01"): 8,
        pd.Timestamp("2026-03-01"): 8,
        # Q1FY27 - easing
        pd.Timestamp("2026-04-01"): 4,
        pd.Timestamp("2026-05-01"): 4,
        pd.Timestamp("2026-06-01"): 4,
        # Q2FY27 - back to normal (~7% annualized voluntary attrition)
        # Jul contains the quarter's single involuntary exit, leaving
        # approximately 9 voluntary exits across the quarter.
        pd.Timestamp("2026-07-01"): 4,
        pd.Timestamp("2026-08-01"): 3,
        pd.Timestamp("2026-09-01"): 4,
        # Q3FY27 - rises again
        pd.Timestamp("2026-10-01"): 8,
        pd.Timestamp("2026-11-01"): 9,
        pd.Timestamp("2026-12-01"): 9,
    }

    # Outside Oct-Mar: only one involuntary exit per quarter.
    sparse_involuntary_months = {
        pd.Timestamp("2025-04-01"),
        pd.Timestamp("2025-07-01"),
        pd.Timestamp("2026-04-01"),
        pd.Timestamp("2026-07-01"),
        pd.Timestamp("2026-09-01"),
    }

    for month, total_exits in monthly_total_exits.items():
        month_idx = panel.index[panel["month"] == month].to_numpy()
        chosen = rng.choice(month_idx, size=min(total_exits, len(month_idx)), replace=False)

        if month.month in [10, 11, 12, 1, 2, 3]:
            invol_count = min(2, len(chosen))
        elif month in sparse_involuntary_months:
            invol_count = min(1, len(chosen))
        else:
            invol_count = 0

        invol_idx = chosen[:invol_count]
        vol_idx = chosen[invol_count:]

        panel.loc[chosen, "exit_event"] = 1
        panel.loc[vol_idx, "exit_type"] = "Voluntary"
        panel.loc[invol_idx, "exit_type"] = "Involuntary"

        # Better salary is deliberately the top voluntary reason.
        for j, idx in enumerate(vol_idx):
            if j % 2 == 0:
                reason = "Better salary"
            else:
                reason = rng.choice(
                    [
                        "Taking time off for personal/medical reasons",
                        "Onsite opportunity",
                        "Better benefits package",
                        "Pursuing passion outside of corporate",
                        "Long Work Hours",
                        "Culture Mismatch",
                    ],
                    p=[0.18, 0.14, 0.14, 0.12, 0.24, 0.18]
                )
            panel.loc[idx, "exit_reason"] = reason

        # Oct-Mar involuntary exits are heavily weighted to poor performance.
        for j, idx in enumerate(invol_idx):
            if month.month in [10, 11, 12, 1, 2, 3]:
                reason = "Poor performance" if j == 0 or invol_count == 1 else rng.choice(
                    ["Poor performance", "Probation failure", "Dismissal"],
                    p=[0.75, 0.15, 0.10]
                )
            else:
                # Outside the Oct-Mar performance cycle, use varied reasons
                # so sparse involuntary exits do not collapse into one category.
                if month == pd.Timestamp("2026-07-01"):
                    reason = "Probation failure"
                elif month == pd.Timestamp("2026-09-01"):
                    reason = "End of contract"
                else:
                    reason = rng.choice(
                        ["Probation failure", "End of contract", "Dismissal"],
                        p=[0.45, 0.35, 0.20]
                    )
            panel.loc[idx, "exit_reason"] = reason


    # --------------------------------------------------------
    # SYNTHETIC CUSTOMER / BUSINESS METRICS
    # --------------------------------------------------------
    # These are intentionally aggregated in the dashboard. No employee-level
    # business ownership table is ever displayed.

    division_portfolio = {
        "Enterprise CS": (0.055, 0.16),
        "Business Engineering": (0.025, 0.08),
        "SMB CS": (0.008, 0.025),
        "Customer Support": (0.0, 0.0),
        "CS Operations": (0.0, 0.0),
    }

    division_accounts = {
        "Enterprise CS": (6, 16),
        "Business Engineering": (14, 30),
        "SMB CS": (28, 58),
        "Customer Support": (0, 0),
        "CS Operations": (0, 0),
    }

    portfolio_vals = []
    account_vals = []
    renewal_vals = []
    backup_vals = []
    sla_vals = []
    backlog_vals = []
    retention_vals = []
    customer_outcome_vals = []

    for _, r in panel.iterrows():
        div = r["division"]

        p_low, p_high = division_portfolio[div]
        if p_high > 0:
            portfolio = rng.uniform(p_low, p_high)
            if r["job_level"] == "L4":
                portfolio *= 1.25
            elif r["job_level"] == "L3":
                portfolio *= 1.10
        else:
            portfolio = 0.0

        a_low, a_high = division_accounts[div]
        accounts = int(rng.integers(a_low, a_high + 1)) if a_high > 0 else 0

        # 90-day renewal value is a subset of the owned portfolio.
        renewal_due = portfolio * rng.uniform(0.16, 0.34) if portfolio > 0 else 0.0

        backup_prob = 0.79
        if div == "Enterprise CS":
            backup_prob -= 0.08
        if r["talent"] == "Top Talent":
            backup_prob -= 0.06
        backup = bool(rng.random() < np.clip(backup_prob, 0.55, 0.90))

        # Support SLA / backlog react to people-health conditions.
        if div == "Customer Support":
            sla = (
                96
                - max(0, 72 - r["team_pulse"]) * 0.20
                - max(0, r["flight_risk"] - 5) * 0.65
            )
            if r["manager"] == "Priya":
                sla -= 3.0
            if r["month"].month in [10, 11, 12, 3]:
                sla -= 2.0
            sla = float(np.clip(sla + rng.normal(0, 1.2), 78, 99))

            backlog = int(
                np.clip(
                    rng.normal(10, 2.5) + max(0, 92 - sla) * 0.9,
                    4,
                    26
                )
            )
        else:
            sla = np.nan
            backlog = 0

        # Simple synthetic merchant-retention outcome for account-owning teams.
        if portfolio > 0:
            retention = (
                96
                + (r["team_pulse"] - 72) * 0.08
                - r["flight_risk"] * 0.20
                + rng.normal(0, 0.8)
            )
            retention = float(np.clip(retention, 86, 99))
        else:
            retention = np.nan

        # A cross-team customer outcome index used only for aggregated
        # People -> Business analysis. It is not presented as causal.
        if div == "Customer Support":
            customer_outcome = sla
        elif portfolio > 0:
            customer_outcome = retention
        else:
            customer_outcome = float(
                np.clip(91 + (r["team_pulse"] - 72) * 0.10 + rng.normal(0, 1), 84, 98)
            )

        portfolio_vals.append(portfolio)
        account_vals.append(accounts)
        renewal_vals.append(renewal_due)
        backup_vals.append(backup)
        sla_vals.append(sla)
        backlog_vals.append(backlog)
        retention_vals.append(retention)
        customer_outcome_vals.append(customer_outcome)

    panel["merchant_portfolio_cr"] = portfolio_vals
    panel["accounts_owned"] = account_vals
    panel["renewal_due_90d_cr"] = renewal_vals
    panel["backup_covered"] = backup_vals
    panel["sla_adherence"] = sla_vals
    panel["backlog_tickets"] = backlog_vals
    panel["merchant_retention"] = retention_vals
    panel["customer_outcome_index"] = customer_outcome_vals

    # New-hire ramp assumption for the prototype.
    panel["ramp_days"] = np.where(
        panel["join_event"],
        np.clip(rng.normal(78, 8, len(panel)).round(), 60, 95),
        np.nan
    )

    role_base = {
        "Enterprise CS": 14,
        "Business Engineering": 10,
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


def business_metrics(data):
    """Return aggregated business-impact metrics for the selected cut."""
    if data.empty:
        return {
            "portfolio_risk_cr": 0.0,
            "support_sla": np.nan,
            "support_backlog": 0,
            "uncovered_accounts": 0,
            "renewal_risk_cr": 0.0,
            "median_ramp_days": np.nan,
        }

    latest_month = data["month"].max()
    latest_slice = data[data["month"] == latest_month].copy()

    # Elevated people risk is deliberately cohort-level: flight-risk signal
    # OR exit-pipeline flag. No individual prediction is displayed.
    at_risk = latest_slice[
        (latest_slice["flight_risk"] >= 8) |
        (
            (latest_slice["exit_pipeline_flag"]) &
            (latest_slice["flight_risk"] >= 6)
        )
    ]

    portfolio_risk_cr = at_risk["merchant_portfolio_cr"].sum()

    # Quarter-sensitive calibration for the synthetic business story.
    # Q2FY27 is intentionally a steadier quarter; post-Q3 / ratings periods are higher.
    latest_month = pd.Timestamp(latest_month)
    quarter_risk_multiplier = 1.0
    if latest_month in QUARTER_MONTHS["Q2FY27"]:
        quarter_risk_multiplier = 0.72
    elif latest_month in QUARTER_MONTHS["Q3FY27"]:
        quarter_risk_multiplier = 1.18
    elif latest_month in QUARTER_MONTHS["Q4FY26"]:
        quarter_risk_multiplier = 1.12
    elif latest_month in QUARTER_MONTHS["Q3FY26"]:
        quarter_risk_multiplier = 1.15
    elif latest_month in QUARTER_MONTHS["Q1FY27"]:
        quarter_risk_multiplier = 0.88
    elif latest_month in QUARTER_MONTHS["Q1FY26"]:
        quarter_risk_multiplier = 0.90
    elif latest_month in QUARTER_MONTHS["Q2FY26"]:
        quarter_risk_multiplier = 0.82

    portfolio_risk_cr *= quarter_risk_multiplier

    support = latest_slice[latest_slice["division"] == "Customer Support"]
    support_sla = support["sla_adherence"].mean() if len(support) else np.nan
    support_backlog = int(support["backlog_tickets"].sum()) if len(support) else 0

    uncovered = latest_slice[
        (latest_slice["accounts_owned"] > 0) &
        (~latest_slice["backup_covered"])
    ]
    uncovered_accounts = int(uncovered["accounts_owned"].sum())

    renewal_risk_cr = latest_slice.loc[
        (latest_slice["renewal_due_90d_cr"] > 0) &
        (~latest_slice["backup_covered"]),
        "renewal_due_90d_cr"
    ].sum() * quarter_risk_multiplier

    # Backup coverage metrics for a visual progress tracker.
    total_accounts = int(latest_slice["accounts_owned"].sum())
    covered_accounts = int(
        latest_slice.loc[latest_slice["backup_covered"], "accounts_owned"].sum()
    )
    total_renewal_book_cr = float(latest_slice["renewal_due_90d_cr"].sum() * quarter_risk_multiplier)
    covered_renewal_book_cr = float(
        latest_slice.loc[latest_slice["backup_covered"], "renewal_due_90d_cr"].sum()
        * quarter_risk_multiplier
    )

    ramp = data.loc[data["join_event"], "ramp_days"].dropna()
    median_ramp_days = float(ramp.median()) if len(ramp) else 78.0

    return {
        "portfolio_risk_cr": portfolio_risk_cr,
        "support_sla": support_sla,
        "support_backlog": support_backlog,
        "uncovered_accounts": uncovered_accounts,
        "renewal_risk_cr": renewal_risk_cr,
        "median_ramp_days": median_ramp_days,
        "total_accounts": total_accounts,
        "covered_accounts": covered_accounts,
        "total_renewal_book_cr": total_renewal_book_cr,
        "covered_renewal_book_cr": covered_renewal_book_cr,
    }

def backup_progress_html(title, covered_pct, left_label, right_label):
    covered_pct = float(max(0, min(100, covered_pct)))
    uncovered_pct = 100 - covered_pct
    return f"""
    <div style="margin-top: 0.3rem; margin-bottom: 1rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
            <div style="font-weight:600; color:#1f2937;">{title}</div>
            <div style="font-size:0.95rem; font-weight:700; color:#111827;">{covered_pct:.0f}% covered</div>
        </div>
        <div style="display:flex; width:100%; height:18px; border-radius:999px; overflow:hidden; background:#e5e7eb;">
            <div style="width:{covered_pct:.2f}%; background:#22c55e;"></div>
            <div style="width:{uncovered_pct:.2f}%; background:#ef4444;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.35rem; font-size:0.9rem;">
            <div style="color:#166534;"><b>{left_label}</b></div>
            <div style="color:#991b1b;"><b>{right_label}</b></div>
        </div>
    </div>
    """

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
    n_months = max(len(months), 1)

    # Annualized attrition:
    # monthly = exits / avg HC * 12
    # quarterly ≈ exits / avg HC * (365/90)
    # other periods use a 12 / number-of-months annualization factor.
    if n_months == 3:
        annualization_factor = 365 / 90
    else:
        annualization_factor = 12 / n_months

    return (exits / avg_hc * annualization_factor * 100) if avg_hc else np.nan

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

sel_quarters = st.sidebar.multiselect(
    "Quarter",
    options=quarter_options,
    default=["Q2FY27"],
    key="quarter_filter",
    placeholder="All"
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

    joiners = int(filtered["join_event"].sum())

    # Exit Pipeline is summed across selected months.
    # Keep it deliberately lean: ~1.6%-2.2% of monthly HC, so a
    # three-month quarter generally lands around 5%-7% of average HC.
    pipeline_monthly_values = []
    for month in period_months:
        month_slice = filtered_non_time[filtered_non_time["month"] == month]
        month_hc = headcount(month_slice)
        if month_hc:
            # Slight variation by month and selected cut.
            month_rate = 0.018
            if month.month in [10, 11, 12, 1, 2, 3]:
                month_rate += 0.003
            pipeline_monthly_values.append(round(month_hc * month_rate))
    exit_pipeline = int(sum(pipeline_monthly_values)) if pipeline_monthly_values else 0

    # Open Roles are also summed across selected months.
    # They are kept close to expected replacement / growth demand rather than
    # a large percentage of the whole organisation.
    monthly_open_roles = []
    for month in period_months:
        month_slice = filtered_non_time[filtered_non_time["month"] == month]
        month_hc = headcount(month_slice)
        month_vol_exits = int(
            month_slice[
                (month_slice["exit_event"] == 1) &
                (month_slice["exit_type"] == "Voluntary")
            ].shape[0]
        )
        if month_hc:
            suggested = max(
                month_vol_exits + 2,
                round(month_hc * 0.025)
            )
            monthly_open_roles.append(
                min(round(month_hc * 0.04), suggested)
            )
    open_roles = int(sum(monthly_open_roles)) if monthly_open_roles else 0

    # Internal movement is intentionally modest: roughly 10–20 moves per quarter.
    # Scale by selected months, capped to keep the demo realistic.
    internal_moves = int(np.clip(round(5 * len(period_months)), 4, 20))

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Headcount", f"{avg_hc:.0f}")
    c2.metric("Joiners", joiners)
    c3.metric("Exit Pipeline", exit_pipeline)
    c4.metric("Open Roles", open_roles)
    c5.metric("Internal Moves", internal_moves)

    st.caption(
        "For multi-month or quarterly views: Headcount is the average monthly headcount; "
        "Joiners, Exit Pipeline and Open Roles are summed across the selected months; Internal Moves remain modest at roughly 10–20 per quarter."
    )

    # --------------------------------------------------------
    # PEOPLE -> BUSINESS IMPACT
    # --------------------------------------------------------
    biz = business_metrics(filtered)

    st.markdown("### Customer & business impact")
    row1 = st.columns(3)
    row2 = st.columns(3)

    row1[0].metric(
        "Commercial Value at Risk",
        f"₹{biz['portfolio_risk_cr']:.1f} Cr",
        help=(
            "Synthetic commercial / contract value associated with managed accounts "
            "supported by cohorts showing elevated people-risk signals. This is a "
            "cohort-level exposure indicator, not an individual resignation prediction."
        )
    )
    row1[1].metric(
        "Support SLA",
        "N/A" if pd.isna(biz["support_sla"]) else f"{biz['support_sla']:.0f}%",
        help=(
            "Share of support interactions resolved within the synthetic service-level "
            "target for the latest month in the selected view."
        )
    )
    row1[2].metric(
        "Ticket Backlog",
        f"{biz['support_backlog']:,}",
        help=(
            "Synthetic unresolved support-ticket volume carried by the Support population "
            "in the latest month of the selected view."
        )
    )

    row2[0].metric(
        "Uncovered Accounts",
        f"{biz['uncovered_accounts']:,}",
        help=(
            "Merchant accounts with elevated continuity risk because the owning cohort is "
            "in the exit pipeline or does not have backup coverage."
        )
    )
    row2[1].metric(
        "Renewal Risk (90d)",
        f"₹{biz['renewal_risk_cr']:.1f} Cr",
        help=(
            "Synthetic merchant portfolio value with a renewal due in the next 90 days "
            "where backup ownership is not currently identified."
        )
    )
    row2[2].metric(
        "Ramp to Output",
        f"{biz['median_ramp_days']:.0f} days",
        help=(
            "Median synthetic time for a new Customer Success hire to reach independent "
            "portfolio ownership / expected productivity."
        )
    )

    st.caption(
        "Business metrics are synthetic and shown only at aggregated cohort level. "
        "Commercial Value at Risk is not a prediction of individual resignation."
    )

    st.markdown("#### Backup coverage action tracker")
    accounts_total = max(1, biz["total_accounts"])
    accounts_covered = min(biz["covered_accounts"], accounts_total)
    accounts_uncovered = max(0, accounts_total - accounts_covered)
    accounts_cov_pct = 100 * accounts_covered / accounts_total

    renewal_total = max(0.01, biz["total_renewal_book_cr"])
    renewal_covered = min(biz["covered_renewal_book_cr"], renewal_total)
    renewal_uncovered = max(0.0, renewal_total - renewal_covered)
    renewal_cov_pct = 100 * renewal_covered / renewal_total

    bp1, bp2 = st.columns(2)
    with bp1:
        st.markdown(
            backup_progress_html(
                "Accounts with Backup Owner",
                accounts_cov_pct,
                f"{accounts_covered:,} with backup",
                f"{accounts_uncovered:,} need backup",
            ),
            unsafe_allow_html=True
        )
    with bp2:
        st.markdown(
            backup_progress_html(
                "Renewal Value Covered by Backup",
                renewal_cov_pct,
                f"₹{renewal_covered:.1f} Cr protected",
                f"₹{renewal_uncovered:.1f} Cr needs backup",
            ),
            unsafe_allow_html=True
        )

    latest_selected_month = max(period_months)

    # Snapshot charts use the latest month in the selected period.
    latest_selected_month = max(period_months)
    latest_snapshot = filtered_non_time[
        filtered_non_time["month"] == latest_selected_month
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
            height=250,
            legend_title_text="",
            margin=dict(l=10, r=10, t=45, b=5)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        division_counts = (
            latest_snapshot.drop_duplicates("employee_id")["division"]
            .value_counts()
            .rename_axis("Division")
            .reset_index(name="Headcount")
            .sort_values("Headcount", ascending=False)
        )

        fig = px.bar(
            division_counts,
            x="Division",
            y="Headcount",
            text="Headcount",
            title=f"Headcount by division • {pd.Timestamp(latest_selected_month).strftime('%b %Y')}"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(title=None, tickangle=-20)
        fig.update_yaxes(title=None)
        fig.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=45, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### AI summaries")

    # Current quarter comparison for voluntary attrition
    quarter_lookup = {q: months for q, months in QUARTER_MONTHS.items()}
    quarter_names = list(QUARTER_MONTHS.keys())

    # Determine the latest quarter represented by current period
    current_q = None
    for qname, qmonths in QUARTER_MONTHS.items():
        if period_end in qmonths:
            current_q = qname
            break

    previous_q = None
    if current_q in quarter_names:
        idx = quarter_names.index(current_q)
        if idx > 0:
            previous_q = quarter_names[idx - 1]

    def voluntary_annualized_attrition(data, months):
        period = data[data["month"].isin(months)].copy()
        exits = period[
            (period["exit_event"] == 1) &
            (period["exit_type"] == "Voluntary")
        ].shape[0]
        avg_hc_local = period_headcount_average(data, months)
        if not avg_hc_local:
            return np.nan
        if len(months) == 3:
            factor = 365 / 90
        else:
            factor = 12 / max(len(months), 1)
        return exits / avg_hc_local * factor * 100

    attrition_summary = "Quarter-on-quarter voluntary attrition comparison is not available for this period."
    if current_q and previous_q:
        current_attr = voluntary_annualized_attrition(filtered_non_time, QUARTER_MONTHS[current_q])
        previous_attr = voluntary_annualized_attrition(filtered_non_time, QUARTER_MONTHS[previous_q])
        if not pd.isna(current_attr) and not pd.isna(previous_attr):
            diff = current_attr - previous_attr
            direction = "increased" if diff > 0 else "reduced"
            attrition_summary = (
                f"Annualized voluntary attrition {direction} by {abs(diff):.1f} pts "
                f"from {previous_q} ({previous_attr:.1f}%) to {current_q} ({current_attr:.1f}%)."
            )

    current_vol_reasons = (
        filtered[
            (filtered["exit_event"] == 1) &
            (filtered["exit_type"] == "Voluntary")
        ]["exit_reason"]
        .value_counts()
        .head(2)
    )
    reason_text = ", ".join(current_vol_reasons.index.tolist()) if len(current_vol_reasons) else "no material voluntary exit reason"

    # Pulse/satisfaction comparison vs previous quarter
    pulse_summary = "Pulse movement is broadly stable."
    top_bottom_summary = ""

    if current_q and previous_q:
        current_q_data = apply_non_time_filters(df[df["month"].isin(QUARTER_MONTHS[current_q])])
        previous_q_data = apply_non_time_filters(df[df["month"].isin(QUARTER_MONTHS[previous_q])])

        current_pulse = survey_mean(current_q_data, "satisfaction")
        previous_pulse = survey_mean(previous_q_data, "satisfaction")

        if not pd.isna(current_pulse) and not pd.isna(previous_pulse):
            pdiff = current_pulse - previous_pulse
            if abs(pdiff) >= 0.5:
                pdir = "increased" if pdiff > 0 else "decreased"
                pulse_summary = (
                    f"Pulse {pdir} by {abs(pdiff):.1f} pts "
                    f"from {previous_q} to {current_q}."
                )

    theme_map_ai = {
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
    theme_scores = []
    for theme_name, col in theme_map_ai.items():
        score = survey_mean(filtered, col)
        if not pd.isna(score):
            theme_scores.append((theme_name, score))
    theme_scores = sorted(theme_scores, key=lambda x: x[1], reverse=True)

    if len(theme_scores) >= 4:
        top2 = ", ".join([f"{n} ({v:.0f}%)" for n, v in theme_scores[:2]])
        bottom2 = ", ".join([f"{n} ({v:.0f}%)" for n, v in theme_scores[-2:]])
        top_bottom_summary = f" Top themes: {top2}. Bottom themes: {bottom2}."

    st.markdown(
        f"""
        <div class="ai-good">
        <b>People signal</b><br>
        {pulse_summary}{top_bottom_summary}
        <br><br><b>Business context:</b> ₹{biz['portfolio_risk_cr']:.1f} Cr of commercial value is supported by cohorts showing elevated people-risk signals, with ₹{biz['renewal_risk_cr']:.1f} Cr of 90-day renewals lacking backup coverage.
        <br><br><b>Suggested action:</b> reinforce the practices behind the strongest themes and use targeted listening on the bottom two themes before choosing an intervention.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="ai-watch">
        <b>Attrition signal</b><br>
        {attrition_summary}<br>
        Top voluntary exit reasons in the selected period: <b>{reason_text}</b>.
        <br><br><b>Business context:</b> {biz['uncovered_accounts']:,} merchant accounts have elevated coverage risk in this cut. Support SLA is {"N/A" if pd.isna(biz["support_sla"]) else f"{biz['support_sla']:.0f}%"} with a synthetic backlog of {biz['support_backlog']:,} tickets.
        <br><br><b>Suggested action:</b> prioritise retention actions against the leading exit reasons, rebalance exposed account portfolios and establish backup ownership for near-term renewals.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 2. ATTRITION
# ============================================================
with tabs[1]:
    st.subheader("Attrition")

    # Quarterly attrition uses voluntary exits only and is annualized:
    # (voluntary exits / average monthly headcount) * (365/90)
    quarterly_rows = []

    for qname, qmonths in QUARTER_MONTHS.items():
        qmonths_in_scope = [m for m in qmonths if m in filtered_non_time["month"].unique()]
        if not qmonths_in_scope:
            continue

        qdata = filtered_non_time[filtered_non_time["month"].isin(qmonths_in_scope)]
        voluntary_exits = qdata[
            (qdata["exit_event"] == 1) &
            (qdata["exit_type"] == "Voluntary")
        ].shape[0]
        avg_q_hc = period_headcount_average(filtered_non_time, qmonths_in_scope)

        if avg_q_hc:
            attr_rate = voluntary_exits / avg_q_hc * (365 / 90) * 100
            quarterly_rows.append({
                "Quarter": qname,
                "Attrition %": attr_rate,
                "Voluntary Exits": voluntary_exits
            })

    quarterly_rates = pd.DataFrame(quarterly_rows)

    # Keep quarter ordering consistent
    quarter_order = list(QUARTER_MONTHS.keys())
    if len(quarterly_rates):
        quarterly_rates["Quarter"] = pd.Categorical(
            quarterly_rates["Quarter"],
            categories=quarter_order,
            ordered=True
        )
        quarterly_rates = quarterly_rates.sort_values("Quarter")

    selected_vol_exits = filtered[
        (filtered["exit_event"] == 1) &
        (filtered["exit_type"] == "Voluntary")
    ].shape[0]
    selected_invol_exits = filtered[
        (filtered["exit_event"] == 1) &
        (filtered["exit_type"] == "Involuntary")
    ].shape[0]

    selected_avg_hc = period_headcount_average(filtered_non_time, period_months)
    selected_annualized = (
        selected_vol_exits / selected_avg_hc * (365 / 90) * 100
        if selected_avg_hc and len(period_months) == 3
        else (
            selected_vol_exits / selected_avg_hc * (12 / max(len(period_months), 1)) * 100
            if selected_avg_hc else np.nan
        )
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Annualized Voluntary Attrition", pct(selected_annualized, 1))
    c2.metric("Voluntary Exits", selected_vol_exits)
    c3.metric("Involuntary Exits", selected_invol_exits)

    # Dynamic AI summary for the selected attrition period.
    voluntary_by_manager = (
        filtered[
            (filtered["exit_event"] == 1) &
            (filtered["exit_type"] == "Voluntary")
        ]
        .groupby("manager")
        .size()
        .sort_values(ascending=False)
    )

    involuntary_by_manager = (
        filtered[
            (filtered["exit_event"] == 1) &
            (filtered["exit_type"] == "Involuntary")
        ]
        .groupby("manager")
        .size()
        .sort_values(ascending=False)
    )

    top_vol_manager = voluntary_by_manager.index[0] if len(voluntary_by_manager) else "None"
    top_vol_count = int(voluntary_by_manager.iloc[0]) if len(voluntary_by_manager) else 0

    top_invol_manager = involuntary_by_manager.index[0] if len(involuntary_by_manager) else "None"
    top_invol_count = int(involuntary_by_manager.iloc[0]) if len(involuntary_by_manager) else 0

    reason_counts = (
        filtered[
            (filtered["exit_event"] == 1) &
            (filtered["exit_type"] == "Voluntary")
        ]["exit_reason"]
        .value_counts()
    )
    top_reasons = reason_counts.head(2).index.tolist()

    retention_actions = {
        "Better salary": (
            "run targeted pay-positioning checks for critical / high-performing cohorts, "
            "use selective market corrections where warranted, and strengthen the total-rewards story"
        ),
        "Taking time off for personal/medical reasons": (
            "explore leave flexibility, short career breaks, phased returns and manager-led workload adjustments"
        ),
        "Onsite opportunity": (
            "increase visibility of onsite rotations, cross-geo assignments and transparent eligibility criteria"
        ),
        "Better benefits package": (
            "benchmark the benefits proposition and improve communication of high-value benefits employees may be underusing"
        ),
        "Pursuing passion outside of corporate": (
            "use stay conversations to identify employees seeking different work models, internal gigs or reduced schedules"
        ),
        "Long Work Hours": (
            "review staffing, account load and peak-period rosters; rebalance work before retention conversations become purely compensation-led"
        ),
        "Culture Mismatch": (
            "run targeted listening with affected teams, strengthen manager expectations and address recurring local culture themes"
        ),
    }

    if top_reasons:
        reason_action_text = "<br>".join([
            f"• <b>{reason}:</b> {retention_actions.get(reason, 'run targeted stay interviews and validate the underlying driver')}."
            for reason in top_reasons
        ])
    else:
        reason_action_text = "• No material voluntary-exit reason is available for this cut."

    involuntary_text = (
        f"<b>{top_invol_manager}</b> has the most involuntary exits ({top_invol_count})."
        if top_invol_count > 0
        else "There are no involuntary exits in the selected period."
    )

    st.markdown(
        f"""
        <div class="ai-watch">
        <b>AI attrition summary</b><br>
        <b>{top_vol_manager}</b> has the most voluntary exits ({top_vol_count}) in the selected period.
        {involuntary_text}
        <br><br>
        <b>Retention priorities based on the leading voluntary exit reasons:</b><br>
        {reason_action_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    exit_business = filtered[
        (filtered["exit_event"] == 1) &
        (filtered["exit_type"] == "Voluntary")
    ]
    portfolio_reassigned = exit_business["merchant_portfolio_cr"].sum()
    accounts_reassigned = int(exit_business["accounts_owned"].sum())

    if selected_vol_exits > 0:
        st.markdown(
            f"""
            <div class="ai-watch">
            <b>Customer continuity impact</b><br>
            Voluntary exits in the selected period are associated with approximately
            <b>₹{portfolio_reassigned:.1f} Cr</b> of commercial value and
            <b>{accounts_reassigned:,}</b> merchant accounts requiring continuity planning or reassignment.
            </div>
            """,
            unsafe_allow_html=True
        )

    if len(quarterly_rates):
        max_q = max(5, int(np.ceil(quarterly_rates["Attrition %"].max() / 5.0) * 5 + 5))
        fig = px.bar(
            quarterly_rates,
            x="Quarter",
            y="Attrition %",
            text="Attrition %",
            title="Quarterly voluntary attrition • annualized"
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
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=25)
        )
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
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
            fig.update_xaxes(dtick=1, title="Exits", rangemode="tozero")
            fig.update_yaxes(title=None)
            fig.update_layout(
                height=max(230, 34 * len(voluntary)),
                margin=dict(l=10, r=35, t=10, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No voluntary exits in this cut.")

    with right:
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

        st.markdown("#### Involuntary separation types")
        if len(involuntary):
            total_involuntary = int(involuntary["Count"].sum())

            # For very small numbers, avoid oversized bars. Compact cards make
            # sparse involuntary exits easier to read without visually exaggerating them.
            if total_involuntary <= 4 and len(involuntary) <= 4:
                card_cols = st.columns(len(involuntary))
                for col, (_, row) in zip(card_cols, involuntary.sort_values("Count", ascending=False).iterrows()):
                    share = (row["Count"] / total_involuntary * 100) if total_involuntary else 0
                    with col:
                        st.metric(
                            row["Reason"],
                            f"{int(row['Count'])} exit" if int(row["Count"]) == 1 else f"{int(row['Count'])} exits",
                            help=f"{share:.0f}% of involuntary separations in the selected period."
                        )

                st.caption(
                    f"{total_involuntary} involuntary separations in the selected period. "
                    "Shown as counts rather than bars because the volume is small."
                )
            else:
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
                    rangemode="tozero",
                    range=[0, max(4, int(involuntary["Count"].max()) + 1)]
                )
                fig.update_yaxes(title=None)
                fig.update_layout(
                    height=max(230, 38 * len(involuntary)),
                    margin=dict(l=10, r=35, t=10, b=30)
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

    # Dynamic AI interpretation of the strongest and weakest themes.
    if len(themes) >= 4:
        ranked = themes.sort_values("Sentiment", ascending=False).reset_index(drop=True)
        top_two = ranked.head(2)
        bottom_two = ranked.tail(2).sort_values("Sentiment")

        positive_explanations = {
            "Inclusivity": "inclusive team practices and broad access to support may be landing well",
            "Team": "strong peer support and day-to-day collaboration may be reinforcing team sentiment",
            "Manager": "regular manager touchpoints and clearer local communication may be helping",
            "Wellbeing": "workload balancing and flexibility may be supporting employee wellbeing",
            "Culture": "employees may be experiencing stronger belonging and alignment with team norms",
            "Org Listening": "visible follow-through on feedback may be increasing confidence in listening channels",
            "Learning": "access to role-relevant learning and career development may be resonating",
            "Innovation": "employees may be finding space to test ideas and improve customer processes",
            "Work": "role clarity and meaningful customer ownership may be supporting work sentiment",
        }

        watch_explanations = {
            "Work": "Possible contributors to validate: reduced quality or variety of work after projects close, repetitive operational work, or friction from external-agency hand-offs.",
            "Innovation": "Possible contributor to validate: operational payment peaks can crowd out experimentation — festive season (Oct–Nov), year-end (Dec), FY-end (Mar), education-fee cycles (Apr–Jul), summer travel (May–Jun), tax deadlines (Jun/Sep/Dec/Mar), and the first week after salary credit.",
            "Manager": "Possible contributors to validate: inconsistent 1:1 cadence, low coaching depth, or managers being absorbed in delivery escalations.",
            "Wellbeing": "Possible contributors to validate: sustained workload, escalation intensity, peak-period staffing gaps, or inadequate recovery time.",
            "Learning": "Possible contributors to validate: learning may feel too generic, difficult to use on the job, or deprioritised during delivery peaks.",
            "Culture": "Possible contributors to validate: local team experiences may not match the wider organisational culture promise.",
            "Org Listening": "Possible contributors to validate: employees may not be seeing enough visible action after prior surveys.",
            "Inclusivity": "Possible contributors to validate: uneven access to opportunities, decision-making forums, or manager support.",
            "Team": "Possible contributors to validate: cross-team dependencies, role ambiguity, or uneven workload distribution.",
        }

        top_text = "<br>".join([
            f"• <b>{row['Theme']} ({row['Sentiment']:.0f}%)</b>: {positive_explanations[row['Theme']]}."
            for _, row in top_two.iterrows()
        ])
        bottom_text = "<br>".join([
            f"• <b>{row['Theme']} ({row['Sentiment']:.0f}%)</b>: {watch_explanations[row['Theme']]}"
            for _, row in bottom_two.iterrows()
        ])

        st.markdown(
            f"""
            <div class="ai-good">
            <b>AI summary • strongest themes</b><br>
            {top_text}
            <br><br><b>Suggested action:</b> identify the practices behind these strengths and replicate them across lower-scoring teams.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="ai-watch">
            <b>AI summary • themes to explore</b><br>
            {bottom_text}
            <br><br><b>Suggested action:</b> validate these hypotheses through manager listening, targeted focus groups and the next pulse before choosing an intervention.
            </div>
            """,
            unsafe_allow_html=True
        )

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
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=25))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 4. TALENT
# ============================================================
with tabs[3]:
    st.subheader("Talent")

    latest = filtered_non_time[
        filtered_non_time["month"] == period_end
    ].copy()

    total_hc = headcount(latest)

    # Deliberate talent architecture:
    # 20% High Potential Talent + 10% Top Talent = 30% accelerated talent pool.
    high_potential = int(round(total_hc * 0.20))
    top_talent = int(round(total_hc * 0.10))
    other_talent = max(0, total_hc - high_potential - top_talent)

    # Keep high-flight-risk population to a single-digit percentage.
    avg_flight_risk_pct = float(np.clip(latest["flight_risk"].mean(), 2, 9))

    critical_roles = latest[latest["job_level"].isin(["L3", "L4"])]
    covered = critical_roles[
        critical_roles["successor_coverage"] != "No successor"
    ]["employee_id"].nunique()
    critical_total = critical_roles["employee_id"].nunique()
    coverage = covered / critical_total * 100 if critical_total else np.nan

    internal_moves = int(np.clip(round(5 * len(period_months)), 4, 20))

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Headcount", total_hc)
    c2.metric("High Potential", high_potential)
    c3.metric("Top Talent", top_talent)
    c4.metric("Flight Risk", f"{avg_flight_risk_pct:.0f}%")
    c5.metric("Successor Coverage", pct(coverage))
    c6.metric("Internal Moves", internal_moves)

    st.caption(
        "Talent mix is designed as 70% Other Talent, 20% High Potential Talent and 10% Top Talent. "
        "Internal movement is deliberately modest at roughly 10–20 moves per quarter."
    )

    talent_biz = business_metrics(latest)

    st.markdown(
        f"""
        <div class="ai-watch">
        <b>Business continuity lens</b><br>
        <b>₹{talent_biz['renewal_risk_cr']:.1f} Cr</b> of 90-day renewal value currently lacks backup coverage,
        while <b>₹{talent_biz['portfolio_risk_cr']:.1f} Cr</b> of commercial value sits in cohorts with elevated people-risk signals.
        <br><br><b>HRBP action:</b> prioritise backup ownership and succession conversations for critical commercial portfolios before broad-based retention activity.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Smaller charts
    left, right = st.columns(2)

    with left:
        talent_mix = pd.DataFrame({
            "Talent": ["Other Talent", "High Potential Talent", "Top Talent"],
            "Count": [other_talent, high_potential, top_talent]
        })
        talent_mix["Percent"] = talent_mix["Count"] / max(total_hc, 1) * 100

        fig = px.bar(
            talent_mix,
            x="Talent",
            y="Percent",
            text="Percent",
            title=f"Talent mix • {pd.Timestamp(period_end).strftime('%b %Y')}"
        )
        fig.update_traces(
            texttemplate="%{text:.0f}%",
            textposition="outside",
            cliponaxis=False
        )
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        fig.update_layout(height=260, margin=dict(l=15, r=15, t=50, b=25))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        ijp = int(round(internal_moves * 0.55))
        onsite = int(round(internal_moves * 0.25))
        role_expansion = max(0, internal_moves - ijp - onsite)

        mobility = pd.DataFrame({
            "Movement": ["IJP", "Onsite Rotation", "Role Expansion"],
            "Count": [ijp, onsite, role_expansion]
        })

        fig = px.bar(
            mobility,
            x="Movement",
            y="Count",
            text="Count",
            title="Internal mobility • selected period"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(height=260, margin=dict(l=15, r=15, t=50, b=25))
        st.plotly_chart(fig, use_container_width=True)

    # Flight risk stays single digit by segment.
    risk_by_talent = pd.DataFrame({
        "Talent": ["Other Talent", "High Potential Talent", "Top Talent"],
        "Flight Risk": [
            max(2, avg_flight_risk_pct - 2),
            min(8, avg_flight_risk_pct + 1),
            min(9, avg_flight_risk_pct + 2)
        ]
    })

    fig = px.bar(
        risk_by_talent,
        x="Talent",
        y="Flight Risk",
        text="Flight Risk",
        title="Flight risk by talent segment"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_yaxes(range=[0, 10], dtick=2, ticksuffix="%")
    fig.update_layout(height=250, margin=dict(l=15, r=15, t=50, b=25))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Aspiration Management")

    aspiration = pd.DataFrame({
        "Theme": [
            "Career growth and promotion",
            "Internal mobility or role change",
            "Skill development and learning",
            "Leadership aspirations",
            "Compensation",
            "Bigger scope and ownership",
            "Recognition and visibility",
            "Mentorship",
            "Personal or life-stage needs"
        ],
        # Ordered to a clean 100% total.
        "Share": [22, 18, 15, 11, 10, 9, 7, 5, 3]
    })

    fig = px.bar(
        aspiration.sort_values("Share"),
        x="Share",
        y="Theme",
        orientation="h",
        text="Share",
        title="Top aspiration themes"
    )
    fig.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="outside",
        cliponaxis=False
    )
    fig.update_xaxes(range=[0, 25], ticksuffix="%")
    fig.update_yaxes(title=None)
    fig.update_layout(height=360, margin=dict(l=15, r=35, t=50, b=25))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 5. MANAGER EFFECTIVENESS
# ============================================================
with tabs[4]:
    st.subheader("Manager Effectiveness")

    manager_rows = []

    # Base manager effects deliberately create a 6–15 point spread by metric.
    manager_adjustments = {
        "Anuj":   {"1:1 Coverage": 7,  "Skip Levels": 5,  "Coaching": 8,  "Team Pulse": 6,  "Learning Score": 7},
        "Cassie": {"1:1 Coverage": 3,  "Skip Levels": 2,  "Coaching": 4,  "Team Pulse": 3,  "Learning Score": 2},
        "Rafee":  {"1:1 Coverage": 6,  "Skip Levels": 4,  "Coaching": 9,  "Team Pulse": 7,  "Learning Score": 5},
        "Priya":  {"1:1 Coverage": -7, "Skip Levels": -5, "Coaching": -6, "Team Pulse": -8, "Learning Score": -5},
        "Zainab": {"1:1 Coverage": 0,  "Skip Levels": -1, "Coaching": 1,  "Team Pulse": 0,  "Learning Score": 1},
    }

    for mgr, g in filtered.groupby("manager"):
        base_vals = {
            "1:1 Coverage": survey_mean(g, "one_to_one"),
            "Skip Levels": survey_mean(g, "skip_level"),
            "Coaching": survey_mean(g, "coaching"),
            "Team Pulse": survey_mean(g, "team_pulse"),
            "Learning Score": survey_mean(g, "learning_score")
        }

        row = {
            "Manager": mgr,
            "HC": headcount(g),
            "Respondents": respondents(g)
        }

        for metric, value in base_vals.items():
            if pd.isna(value):
                row[metric] = np.nan
            else:
                row[metric] = float(
                    np.clip(
                        value + manager_adjustments[mgr][metric],
                        45,
                        95
                    )
                )

        manager_rows.append(row)

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
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=25))
    st.plotly_chart(fig, use_container_width=True)

    if len(plot_df):
        best = plot_df.iloc[0]
        low = plot_df.iloc[-1]

        sustain_actions = {
            "1:1 Coverage": "capture what is enabling consistent 1:1 cadence and replicate the operating rhythm across other teams",
            "Skip Levels": "reuse the same skip-level cadence and question set with other manager populations",
            "Coaching": "identify the coaching practices being used and turn them into peer-learning examples",
            "Team Pulse": "understand which team practices are sustaining sentiment and scale those behaviours",
            "Learning Score": "replicate the learning routines, role-based pathways and manager reinforcement that are working",
        }

        improvement_actions = {
            "1:1 Coverage": "block recurring 1:1 slots, send nudges for overdue conversations, track completion weekly and ask managers to protect the time from delivery meetings",
            "Skip Levels": "set a monthly skip-level calendar, rotate employee participation, use a standard question bank and close the loop visibly on recurring themes",
            "Coaching": "run manager coaching clinics, pair lower-scoring managers with strong peers, provide conversation prompts and measure coaching completion monthly",
            "Team Pulse": "run a focused team listening session, identify the two biggest pain points, publish a 30-day action plan and report progress back to the team",
            "Learning Score": "create role-based learning paths, protect learning time, use completion nudges, and ask managers to connect learning goals to live customer work",
        }

        st.markdown(
            f"""
            <div class="ai-good">
            <b>Positive signal</b><br>
            {best['Manager']} is strongest on {metric_choice} at {best[metric_choice]:.0f}%.
            <br><br><b>What to sustain:</b> {sustain_actions[metric_choice]}.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="ai-watch">
            <b>Watch-out</b><br>
            {low['Manager']} is lowest on {metric_choice} at {low[metric_choice]:.0f}%.
            <br><br><b>Suggested action:</b> {improvement_actions[metric_choice]}.
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # PEOPLE -> BUSINESS RELATIONSHIP
    # --------------------------------------------------------
    relationship_rows = []
    for _, mgr_row in mgr_df.iterrows():
        mgr_name = mgr_row["Manager"]
        g = filtered[filtered["manager"] == mgr_name]

        if g.empty or pd.isna(mgr_row[metric_choice]):
            continue

        customer_outcome = g["customer_outcome_index"].mean()

        relationship_rows.append({
            "Manager": mgr_name,
            "People Metric": mgr_row[metric_choice],
            "Customer Outcome": customer_outcome,
            "HC": headcount(g)
        })

    relationship_df = pd.DataFrame(relationship_rows)

    if len(relationship_df) >= 2:
        st.markdown("### People → business")
        fig = px.scatter(
            relationship_df,
            x="People Metric",
            y="Customer Outcome",
            size="HC",
            text="Manager",
            title=f"{metric_choice} vs customer outcome"
        )
        fig.update_traces(textposition="top center")
        fig.update_xaxes(
            range=[45, 100],
            ticksuffix="%",
            title=metric_choice
        )
        fig.update_yaxes(
            range=[80, 100],
            ticksuffix="%",
            title="Customer outcome index"
        )
        fig.update_layout(
            height=290,
            margin=dict(l=20, r=20, t=50, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Synthetic association only. The chart does not establish that manager behaviour causes the business outcome; "
            "staffing, workload, seasonality and merchant mix may also contribute."
        )


st.divider()
st.caption(
    "People Pulse prototype • Synthetic Customer Success data • ~500 active employees per month • "
    "No individual employee records, merchant ownership records or comments displayed."
)
