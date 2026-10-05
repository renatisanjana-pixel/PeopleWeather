import streamlit as st
import pandas as pd
import numpy as np

# ------------------------------------------------------------
# PAGE SETUP
# ------------------------------------------------------------

st.set_page_config(
    page_title="PeoplePulse | Customer Success",
    page_icon="🟣",
    layout="wide"
)

MIN_GROUP_SIZE = 5

# ------------------------------------------------------------
# STYLING
# ------------------------------------------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e9e9ef;
    padding: 14px 16px;
    border-radius: 14px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
}

.pp-header {
    padding: 22px 26px;
    border-radius: 18px;
    background: linear-gradient(120deg, #4C1D95, #7C3AED, #A855F7);
    color: white;
    margin-bottom: 18px;
}

.pp-header h1 {
    margin: 0;
    font-size: 34px;
}

.pp-header p {
    margin: 6px 0 0 0;
    opacity: 0.9;
    font-size: 15px;
}

.privacy-badge {
    display: inline-block;
    background: #F3E8FF;
    color: #6B21A8;
    border-radius: 20px;
    padding: 7px 12px;
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 12px;
}

.ai-box {
    padding: 18px 20px;
    border-left: 5px solid #7C3AED;
    background-color: #F8F5FF;
    border-radius: 12px;
    margin-top: 10px;
    margin-bottom: 15px;
}

.alert-box {
    padding: 16px 18px;
    background-color: #FFF7ED;
    border-left: 5px solid #F97316;
    border-radius: 12px;
    margin-bottom: 12px;
}

.good-box {
    padding: 16px 18px;
    background-color: #F0FDF4;
    border-left: 5px solid #22C55E;
    border-radius: 12px;
    margin-bottom: 12px;
}

.small-note {
    color: #6B7280;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# SYNTHETIC DATA GENERATION
# ------------------------------------------------------------

@st.cache_data
def create_data():

    np.random.seed(42)

    division_counts = {
        "Enterprise Customer Success": 145,
        "Mid-Market Customer Success": 115,
        "SMB Customer Success": 90,
        "Customer Support": 85,
        "Customer Success Operations": 65
    }

    divisions = []
    for division, count in division_counts.items():
        divisions.extend([division] * count)

    np.random.shuffle(divisions)

    n = 500

    cities = np.random.choice(
        ["Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune"],
        n,
        p=[0.42, 0.18, 0.15, 0.15, 0.10]
    )

    levels = np.random.choice(
        ["L1", "L2", "L3", "L4", "L5", "L6"],
        n,
        p=[0.12, 0.25, 0.27, 0.20, 0.11, 0.05]
    )

    tenure = np.random.choice(
        ["<1 year", "1–2 years", "2–4 years", "4–7 years", "7+ years"],
        n,
        p=[0.15, 0.22, 0.32, 0.23, 0.08]
    )

    performance = np.random.choice(
        ["Developing", "Strong", "Exceptional"],
        n,
        p=[0.10, 0.68, 0.22]
    )

    talent = np.random.choice(
        ["Core Talent", "High Potential", "Critical Talent"],
        n,
        p=[0.72, 0.18, 0.10]
    )

    managers = [f"Manager Group {i:02d}" for i in range(1, 41)]
    manager_assignment = np.repeat(managers, 13)[:n]

    np.random.shuffle(manager_assignment)

    employee_base = pd.DataFrame({
        "division": divisions,
        "city": cities,
        "job_level": levels,
        "tenure": tenure,
        "performance": performance,
        "talent": talent,
        "manager": manager_assignment
    })

    months = pd.date_range("2025-10-01", periods=12, freq="MS")

    records = []

    for idx, person in employee_base.iterrows():

        base_enps = np.random.normal(32, 13)
        base_manager = np.random.normal(76, 9)
        base_workload = np.random.normal(53, 10)
        base_one_to_one = np.random.normal(82, 9)
        base_career = np.random.normal(72, 9)
        base_risk = np.random.normal(31, 10)

        for month_num, month in enumerate(months):

            enps = base_enps + np.random.normal(0, 5)
            manager_connection = base_manager + np.random.normal(0, 4)
            workload = base_workload + np.random.normal(0, 4)
            one_to_one = base_one_to_one + np.random.normal(0, 4)
            career = base_career + np.random.normal(0, 4)
            risk = base_risk + np.random.normal(0, 4)

            # ------------------------------------------------
            # ENGINEERED PEOPLE PATTERNS
            # ------------------------------------------------

            # Enterprise CS workload rises in later months
            if (
                person["division"] == "Enterprise Customer Success"
                and month_num >= 7
            ):
                workload += 9 + (month_num - 7) * 1.8
                enps -= 5
                risk += 7

            # Certain manager cohorts show deteriorating connection
            if (
                person["manager"] in
                ["Manager Group 03", "Manager Group 07",
                 "Manager Group 23", "Manager Group 27"]
                and month_num >= 6
            ):
                one_to_one -= 13
                manager_connection -= 10
                enps -= 7
                risk += 8

            # 2–4 year high performers have stronger career risk
            if (
                person["tenure"] == "2–4 years"
                and person["performance"] == "Exceptional"
            ):
                career -= 9
                risk += 10

            # Critical talent shows stronger mobility appetite
            if person["talent"] == "Critical Talent":
                career -= 5
                risk += 6

            # Manager connection affects engagement signal
            if manager_connection < 65:
                enps -= 8
                risk += 7

            # Customer-facing roles have stronger connectedness
            if person["division"] in [
                "Enterprise Customer Success",
                "Customer Support"
            ]:
                customer_connectedness = np.random.normal(82, 7)
            else:
                customer_connectedness = np.random.normal(72, 8)

            # Simulated participation
            pulse_participation = np.random.normal(82, 7)

            # Small probability of exit
            exit_probability = max(
                0.001,
                min(0.04, 0.003 + risk / 4000)
            )

            exit_event = (
                1 if month_num >= 8 and np.random.random() < exit_probability
                else 0
            )

            records.append({
                "month": month,
                "division": person["division"],
                "city": person["city"],
                "job_level": person["job_level"],
                "tenure": person["tenure"],
                "performance": person["performance"],
                "talent": person["talent"],
                "manager": person["manager"],
                "enps": np.clip(enps, -100, 100),
                "manager_connection": np.clip(manager_connection, 0, 100),
                "workload_pressure": np.clip(workload, 0, 100),
                "one_to_one_completion": np.clip(one_to_one, 0, 100),
                "career_sentiment": np.clip(career, 0, 100),
                "flight_risk_signal": np.clip(risk, 0, 100),
                "pulse_participation": np.clip(
                    pulse_participation, 0, 100
                ),
                "customer_connectedness": np.clip(
                    customer_connectedness, 0, 100
                ),
                "exit_event": exit_event
            })

    return pd.DataFrame(records)


df = create_data()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown("""
<div class="pp-header">
    <h1>PeoplePulse</h1>
    <p>
    Customer Success • People × Performance × Risk
    <br>
    Know where your people need attention before the numbers become business problems.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="privacy-badge">'
    '🔒 Privacy protected • Minimum group size: 5 • Synthetic data'
    '</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------

st.sidebar.title("Explore the organisation")
st.sidebar.caption("All data shown is aggregated.")

selected_month = st.sidebar.selectbox(
    "Month",
    sorted(df["month"].unique(), reverse=True),
    format_func=lambda x: pd.Timestamp(x).strftime("%b %Y")
)

snapshot = df[df["month"] == selected_month].copy()


def add_filter(label, column):

    values = ["All"] + sorted(snapshot[column].unique().tolist())

    return st.sidebar.selectbox(label, values)


division_filter = add_filter("Division", "division")
city_filter = add_filter("City", "city")
level_filter = add_filter("Job Level", "job_level")
tenure_filter = add_filter("Tenure", "tenure")
performance_filter = add_filter("Performance", "performance")
talent_filter = add_filter("Talent Mapping", "talent")
manager_filter = add_filter("Manager Group", "manager")


def apply_filters(data):

    filtered = data.copy()

    filters = {
        "division": division_filter,
        "city": city_filter,
        "job_level": level_filter,
        "tenure": tenure_filter,
        "performance": performance_filter,
        "talent": talent_filter,
        "manager": manager_filter
    }

    for col, value in filters.items():

        if value != "All":
            filtered = filtered[filtered[col] == value]

    return filtered


filtered_snapshot = apply_filters(snapshot)
filtered_all_months = apply_filters(df)


# ------------------------------------------------------------
# PRIVACY CHECK
# ------------------------------------------------------------

group_size = len(filtered_snapshot)

if group_size < MIN_GROUP_SIZE:

    st.warning(
        "🔒 This view has been suppressed because fewer than "
        f"{MIN_GROUP_SIZE} employees match the selected filters."
    )

    st.caption(
        "PeoplePulse prevents small-group reporting to reduce "
        "the risk of identifying individuals."
    )

    st.stop()


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def pct(value):
    return f"{value:.0f}%"


def change(current, previous):
    return current - previous


def safe_groupby(data, group_col):

    grouped = (
        data.groupby(group_col)
        .agg(
            Headcount=(group_col, "size"),
            eNPS=("enps", "mean"),
            Workload=("workload_pressure", "mean"),
            Manager_Connection=("manager_connection", "mean"),
            One_to_One=("one_to_one_completion", "mean"),
            Career_Sentiment=("career_sentiment", "mean"),
            Flight_Risk=("flight_risk_signal", "mean")
        )
        .reset_index()
    )

    return grouped[grouped["Headcount"] >= MIN_GROUP_SIZE]


latest = filtered_snapshot

previous_month = pd.Timestamp(selected_month) - pd.DateOffset(months=1)

previous = filtered_all_months[
    filtered_all_months["month"] == previous_month
]


# ------------------------------------------------------------
# KEY METRICS
# ------------------------------------------------------------

current_enps = latest["enps"].mean()
current_workload = latest["workload_pressure"].mean()
current_manager = latest["manager_connection"].mean()
current_risk = latest["flight_risk_signal"].mean()
current_one_to_one = latest["one_to_one_completion"].mean()

if len(previous) >= MIN_GROUP_SIZE:
    previous_enps = previous["enps"].mean()
    previous_workload = previous["workload_pressure"].mean()
    previous_manager = previous["manager_connection"].mean()
    previous_risk = previous["flight_risk_signal"].mean()
else:
    previous_enps = current_enps
    previous_workload = current_workload
    previous_manager = current_manager
    previous_risk = current_risk


tabs = st.tabs([
    "🏠 Executive Pulse",
    "🌤 People Weather",
    "🎯 Talent & Risk",
    "👥 Manager Health",
    "✨ AI Actions"
])


# ============================================================
# TAB 1 — EXECUTIVE PULSE
# ============================================================

with tabs[0]:

    st.subheader("Executive Pulse")

    st.caption(
        f"Current view: {group_size} employees • "
        f"{pd.Timestamp(selected_month).strftime('%B %Y')}"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Headcount",
        group_size
    )

    c2.metric(
        "eNPS",
        f"{current_enps:.1f}",
        f"{change(current_enps, previous_enps):+.1f}"
    )

    c3.metric(
        "Workload Pressure",
        pct(current_workload),
        f"{change(current_workload, previous_workload):+.1f} pts",
        delta_color="inverse"
    )

    c4.metric(
        "Manager Connection",
        pct(current_manager),
        f"{change(current_manager, previous_manager):+.1f} pts"
    )

    c5.metric(
        "Flight Risk Signal",
        pct(current_risk),
        f"{change(current_risk, previous_risk):+.1f} pts",
        delta_color="inverse"
    )

    st.divider()

    left, right = st.columns([1.45, 1])

    with left:

        st.markdown("#### 12-month people trend")

        trend = (
            filtered_all_months
            .groupby("month")
            .agg(
                eNPS=("enps", "mean"),
                Manager_Connection=("manager_connection", "mean"),
                Career_Sentiment=("career_sentiment", "mean")
            )
        )

        st.line_chart(trend)

    with right:

        st.markdown("#### AI: What changed?")

        if current_workload - previous_workload > 2:

            st.markdown(
                f"""
                <div class="alert-box">
                <b>Workload is emerging as a pressure signal.</b><br>
                Workload increased by
                {current_workload - previous_workload:.1f} points versus
                the prior month. Manager connection and career sentiment
                should be watched alongside this trend.
                </div>
                """,
                unsafe_allow_html=True
            )

        elif current_risk > 40:

            st.markdown(
                """
                <div class="alert-box">
                <b>Retention attention recommended.</b><br>
                The selected population is showing elevated aggregate
                flight-risk signals. Review tenure, talent and manager
                segments before deciding an intervention.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="good-box">
                <b>Overall people health is currently stable.</b><br>
                No major deterioration is visible at headline level.
                Continue monitoring pockets of workload, career sentiment
                and manager connection.
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div class="small-note">
            AI interpretation is based only on aggregated indicators.
            It does not predict individual employee behaviour.
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# TAB 2 — PEOPLE WEATHER
# ============================================================

with tabs[1]:

    st.subheader("People Weather")

    st.write(
        "A quick view of where organisational pressure is building."
    )

    weather = safe_groupby(latest, "division")

    weather["Health Score"] = (
        weather["eNPS"] * 0.20
        + weather["Manager_Connection"] * 0.30
        + weather["Career_Sentiment"] * 0.25
        + (100 - weather["Workload"]) * 0.15
        + (100 - weather["Flight_Risk"]) * 0.10
    )

    weather["Weather"] = np.select(
        [
            weather["Health Score"] >= 65,
            weather["Health Score"] >= 55,
            weather["Health Score"] >= 45
        ],
        [
            "☀️ Clear",
            "🌤 Watch",
            "🌧 Pressure"
        ],
        default="⛈ Intervention"
    )

    display_weather = weather[
        [
            "division",
            "Headcount",
            "Weather",
            "Health Score",
            "eNPS",
            "Workload",
            "Manager_Connection",
            "Flight_Risk"
        ]
    ].copy()

    display_weather.columns = [
        "Division",
        "Headcount",
        "People Weather",
        "Health Score",
        "eNPS",
        "Workload",
        "Manager Connection",
        "Flight Risk"
    ]

    numeric_cols = [
        "Health Score",
        "eNPS",
        "Workload",
        "Manager Connection",
        "Flight Risk"
    ]

    display_weather[numeric_cols] = (
        display_weather[numeric_cols].round(1)
    )

    st.dataframe(
        display_weather.sort_values("Health Score"),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Workload pressure by division")

    chart_data = (
        weather
        .set_index("division")[["Workload"]]
        .sort_values("Workload", ascending=False)
    )

    st.bar_chart(chart_data)


# ============================================================
# TAB 3 — TALENT & RISK
# ============================================================

with tabs[2]:

    st.subheader("Talent & Flight-Risk Signals")

    st.caption(
        "Group-level signals only. PeoplePulse never labels an individual "
        "employee as a flight risk."
    )

    talent_view = safe_groupby(latest, "talent")

    st.dataframe(
        talent_view.rename(columns={
            "talent": "Talent Segment",
            "Manager_Connection": "Manager Connection",
            "One_to_One": "1:1 Completion",
            "Career_Sentiment": "Career Sentiment",
            "Flight_Risk": "Flight Risk Signal"
        }).round(1),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Where is career risk concentrated?")

    tenure_risk = safe_groupby(latest, "tenure")

    tenure_chart = (
        tenure_risk
        .set_index("tenure")[[
            "Career_Sentiment",
            "Flight_Risk"
        ]]
    )

    st.bar_chart(tenure_chart)

    two_four = latest[
        latest["tenure"] == "2–4 years"
    ]

    if len(two_four) >= MIN_GROUP_SIZE:

        exceptional = two_four[
            two_four["performance"] == "Exceptional"
        ]

        if len(exceptional) >= MIN_GROUP_SIZE:

            st.markdown(
                f"""
                <div class="ai-box">
                <b>AI signal:</b> The 2–4 year exceptional-performance
                population is showing a flight-risk signal of
                <b>{exceptional["flight_risk_signal"].mean():.0f}%</b>
                with career sentiment at
                <b>{exceptional["career_sentiment"].mean():.0f}%</b>.
                <br><br>
                <b>Suggested HRBP action:</b> Review career velocity,
                internal moves and role expansion opportunities for this
                population before the next pulse cycle.
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# TAB 4 — MANAGER HEALTH
# ============================================================

with tabs[3]:

    st.subheader("Manager Health")

    st.write(
        "Identifies manager populations where declining connection may "
        "become a people or business risk."
    )

    manager_health = safe_groupby(latest, "manager")

    manager_health["Attention Score"] = (
        manager_health["Workload"] * 0.25
        + manager_health["Flight_Risk"] * 0.30
        + (100 - manager_health["Manager_Connection"]) * 0.25
        + (100 - manager_health["One_to_One"]) * 0.20
    )

    manager_health = manager_health.sort_values(
        "Attention Score",
        ascending=False
    )

    st.markdown("#### Manager Risk Radar")

    radar = manager_health.rename(columns={
        "Manager_Connection": "Manager Connection",
        "Workload": "Workload Pressure",
        "manager": "Manager Group",
        "Headcount": "Team Size"
    })

    st.scatter_chart(
        radar,
        x="Manager Connection",
        y="Workload Pressure",
        size="Team Size"
    )

    st.markdown("#### Highest-priority manager populations")

    manager_table = manager_health[
        [
            "manager",
            "Headcount",
            "Manager_Connection",
            "One_to_One",
            "Workload",
            "Flight_Risk",
            "Attention Score"
        ]
    ].head(10).copy()

    manager_table.columns = [
        "Manager Group",
        "Team Size",
        "Manager Connection",
        "1:1 Completion",
        "Workload",
        "Flight Risk",
        "Attention Score"
    ]

    st.dataframe(
        manager_table.round(1),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 5 — AI ACTIONS
# ============================================================

with tabs[4]:

    st.subheader("AI Intervention Planner")

    st.write(
        "Moves the conversation from **what happened?** "
        "to **what should we do next?**"
    )

    issues = []

    if current_workload >= 62:
        issues.append("workload")

    if current_manager <= 70:
        issues.append("manager connection")

    if current_risk >= 40:
        issues.append("retention")

    if current_one_to_one <= 72:
        issues.append("manager cadence")

    if latest["career_sentiment"].mean() <= 67:
        issues.append("career progression")

    if not issues:

        st.success(
            "No material aggregate risk threshold is currently breached "
            "for this population."
        )

        st.write(
            "Recommended action: maintain current manager cadence and "
            "continue monitoring leading indicators."
        )

    else:

        st.markdown(
            f"""
            <div class="ai-box">
            <b>PeoplePulse has identified {len(issues)} priority signal(s):</b>
            {", ".join(issues)}.
            </div>
            """,
            unsafe_allow_html=True
        )

        if "workload" in issues:

            st.markdown(
                """
                **1. Workload diagnostic — next 2 weeks**

                Review account load, escalation volume and operating
                bottlenecks by CS sub-team. Validate whether the pressure
                is temporary or structural.

                **Success signal:** workload pressure falls by 5+ points.
                """
            )

        if "manager connection" in issues or "manager cadence" in issues:

            st.markdown(
                """
                **2. Manager reset — next 30 days**

                Focus selected manager cohorts on quality 1:1s, career
                conversations and workload prioritisation rather than
                adding broad-based engagement activity.

                **Success signal:** manager connection and 1:1 completion
                improve in the next pulse.
                """
            )

        if "retention" in issues or "career progression" in issues:

            st.markdown(
                """
                **3. Career intervention — next 30–45 days**

                Review internal mobility, stretch assignments and career
                pathways for high-performing and critical-talent cohorts.

                **Success signal:** career sentiment rises and aggregate
                flight-risk signals begin to decline.
                """
            )

    st.divider()

    st.markdown("#### Why am I seeing this?")

    st.write(
        """
        PeoplePulse combines aggregate trends across workload, manager
        connection, career sentiment, talent mapping and retention
        indicators. The AI layer **explains patterns and recommends
        interventions**; it does not make employment decisions.
        """
    )

    st.info(
        "Prototype principle: deterministic analytics calculate the "
        "metrics. AI interprets the signals and recommends action."
    )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.divider()

st.caption(
    "PeoplePulse prototype • Synthetic Customer Success data • "
    "500 employees • No individual employee records or comments displayed • "
    "Groups with fewer than 5 employees are suppressed."
)
