import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="People Pulse | Customer Success", page_icon="🟣", layout="wide")
MIN_RESPONDENTS = 5

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 3rem;}
[data-testid="stMetric"] {background-color:#fff;border:1px solid #e9e9ef;padding:14px 16px;border-radius:14px;box-shadow:0 2px 8px rgba(0,0,0,.04);}
.pp-header {padding:24px 28px;border-radius:20px;background:linear-gradient(120deg,#4C1D95,#7C3AED,#A855F7);color:white;margin-bottom:14px;}
.pp-header h1 {margin:0;font-size:36px;letter-spacing:.2px;}
.pp-header p {margin:7px 0 0 0;opacity:.94;font-size:16px;line-height:1.5;}
.privacy-badge {display:inline-block;background:#F3E8FF;color:#6B21A8;border-radius:20px;padding:7px 12px;font-weight:600;font-size:13px;margin-bottom:8px;}
.benchmark-box {padding:12px 16px;background:#FAFAFC;border:1px solid #ECECF2;border-radius:12px;font-size:13px;margin:6px 0 16px 0;}
.ai-box {padding:18px 20px;border-left:5px solid #7C3AED;background-color:#F8F5FF;border-radius:12px;margin-top:10px;margin-bottom:15px;}
.alert-box {padding:16px 18px;background-color:#FFF7ED;border-left:5px solid #F97316;border-radius:12px;margin-bottom:12px;}
.good-box {padding:16px 18px;background-color:#F0FDF4;border-left:5px solid #22C55E;border-radius:12px;margin-bottom:12px;}
.small-note {color:#6B7280;font-size:12px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def create_data():
    np.random.seed(42)
    n = 500
    division_counts = {
        "Enterprise Customer Success": 145,
        "Mid-Market Customer Success": 115,
        "SMB Customer Success": 90,
        "Customer Support": 85,
        "Customer Success Operations": 65,
    }
    divisions = []
    for division, count in division_counts.items():
        divisions.extend([division] * count)
    np.random.shuffle(divisions)

    cities = np.random.choice(["Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Pune"], n, p=[0.42,0.18,0.15,0.15,0.10])
    levels = np.random.choice(["L1","L2","L3","L4","L5","L6"], n, p=[0.12,0.25,0.27,0.20,0.11,0.05])
    tenure = np.random.choice(["<1 year","1–2 years","2–4 years","4–7 years","7+ years"], n, p=[0.15,0.22,0.32,0.23,0.08])
    performance = np.random.choice(["Developing","Strong","Exceptional"], n, p=[0.10,0.68,0.22])
    talent = np.random.choice(["Core Talent","High Potential","Critical Talent"], n, p=[0.72,0.18,0.10])

    genders = np.array(["Male"]*265 + ["Female"]*225 + ["Others"]*10)
    np.random.shuffle(genders)

    manager_names = ["Anuj","Beena","Cassie","Farah","Priya","Tina","Ronit","Yusuf","Rafee","Zainab"]
    managers = np.repeat(manager_names, 50)
    np.random.shuffle(managers)

    employee_base = pd.DataFrame({
        "employee_id":[f"E{i:03d}" for i in range(1,n+1)],
        "division":divisions,
        "city":cities,
        "job_level":levels,
        "tenure":tenure,
        "performance":performance,
        "talent":talent,
        "gender":genders,
        "manager":managers,
    })
    employee_base["manager_rank"] = employee_base.groupby("manager").cumcount()+1

    months = pd.date_range("2025-10-01", periods=12, freq="MS")
    records=[]

    division_effects = {
        "Enterprise Customer Success":{"pulse":-5,"manager":-2,"workload":8,"career":-4,"risk":6},
        "Mid-Market Customer Success":{"pulse":1,"manager":1,"workload":1,"career":0,"risk":0},
        "SMB Customer Success":{"pulse":5,"manager":4,"workload":-5,"career":3,"risk":-4},
        "Customer Support":{"pulse":3,"manager":2,"workload":0,"career":2,"risk":-2},
        "Customer Success Operations":{"pulse":-2,"manager":-1,"workload":3,"career":-3,"risk":3},
    }
    manager_effects = {
        "Anuj":{"pulse":5,"manager":6,"workload":-4,"risk":-4},
        "Beena":{"pulse":3,"manager":4,"workload":-2,"risk":-2},
        "Cassie":{"pulse":1,"manager":2,"workload":0,"risk":0},
        "Farah":{"pulse":-2,"manager":-2,"workload":4,"risk":3},
        "Priya":{"pulse":4,"manager":5,"workload":-3,"risk":-3},
        "Tina":{"pulse":0,"manager":0,"workload":1,"risk":1},
        "Ronit":{"pulse":-4,"manager":-5,"workload":7,"risk":6},
        "Yusuf":{"pulse":2,"manager":3,"workload":-1,"risk":-1},
        "Rafee":{"pulse":-1,"manager":-1,"workload":3,"risk":2},
        "Zainab":{"pulse":1,"manager":1,"workload":0,"risk":0},
    }

    for _, person in employee_base.iterrows():
        base_pulse=np.random.normal(74,6)
        base_manager=np.random.normal(75,6)
        base_workload=np.random.normal(46,7)
        base_one_to_one=np.random.normal(82,7)
        base_career=np.random.normal(72,7)
        base_risk=np.random.normal(28,7)

        for month_num, month in enumerate(months):
            de=division_effects[person["division"]]
            me=manager_effects[person["manager"]]
            pulse=base_pulse+de["pulse"]+me["pulse"]+np.random.normal(0,3)
            manager_connection=base_manager+de["manager"]+me["manager"]+np.random.normal(0,3)
            workload=base_workload+de["workload"]+me["workload"]+np.random.normal(0,3)
            one_to_one=base_one_to_one+np.random.normal(0,3)
            career=base_career+de["career"]+np.random.normal(0,3)
            risk=base_risk+de["risk"]+me["risk"]+np.random.normal(0,3)

            if person["division"]=="Enterprise Customer Success" and month_num>=7:
                workload += 7+(month_num-7)*2.0
                pulse -= 4+(month_num-7)*0.8
                manager_connection -= 2
                risk += 6+(month_num-7)*1.4

            if person["manager"]=="Ronit" and month_num>=6:
                one_to_one -= 11
                manager_connection -= 7
                pulse -= 5
                risk += 8

            if person["manager"]=="Farah" and month_num>=8:
                one_to_one += 8
                manager_connection += 6
                pulse += 5
                workload -= 4
                risk -= 4

            if person["tenure"]=="2–4 years" and person["performance"]=="Exceptional":
                career -= 9
                risk += 10
                pulse -= 3

            if person["talent"]=="Critical Talent":
                career -= 5
                risk += 7
            elif person["talent"]=="High Potential":
                career -= 2
                risk += 3

            if manager_connection<65:
                pulse -= 6
                risk += 5

            customer_connectedness=np.random.normal(83,6) if person["division"] in ["Enterprise Customer Success","Customer Support"] else np.random.normal(73,7)

            if person["manager"]=="Zainab":
                survey_participated = person["manager_rank"]<=4
            else:
                participation_prob=0.84
                if person["manager"]=="Ronit" and month_num>=7:
                    participation_prob=0.70
                if person["manager"]=="Farah" and month_num>=8:
                    participation_prob=0.90
                survey_participated=np.random.random()<participation_prob

            records.append({
                "employee_id":person["employee_id"],
                "month":month,
                "division":person["division"],
                "city":person["city"],
                "job_level":person["job_level"],
                "tenure":person["tenure"],
                "performance":person["performance"],
                "talent":person["talent"],
                "gender":person["gender"],
                "manager":person["manager"],
                "survey_participated":bool(survey_participated),
                "pulse":np.clip(pulse,0,100),
                "manager_connection":np.clip(manager_connection,0,100),
                "workload_pressure":np.clip(workload,0,100),
                "one_to_one_completion":np.clip(one_to_one,0,100),
                "career_sentiment":np.clip(career,0,100),
                "flight_risk_signal":np.clip(risk,0,100),
                "customer_connectedness":np.clip(customer_connectedness,0,100),
            })
    return pd.DataFrame(records)

df=create_data()

st.markdown("""
<div class="pp-header">
<h1>People Pulse</h1>
<p>Customer Success • People Health & Organisational Insights<br>
A forward-looking view of engagement, manager effectiveness, talent health and emerging people priorities.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="privacy-badge">🔒 Privacy protected • Minimum respondent group: 5 • Synthetic data</div>', unsafe_allow_html=True)

st.markdown("""
<div class="benchmark-box">
<b>How to read the scores</b><br>
<b>Positive indicators</b> (Pulse, Manager Connection, Career Sentiment, 1:1 Completion):
🟢 ≥70% healthy &nbsp; | &nbsp; 🟠 50–69% watch &nbsp; | &nbsp; 🔴 &lt;50% concern<br>
<b>Pressure indicators</b> (Workload Pressure, Flight Risk Signal):
🟢 &lt;30% low &nbsp; | &nbsp; 🟠 30–49% watch &nbsp; | &nbsp; 🔴 ≥50% high<br>
All survey-derived scores are percentages. Participation = respondents ÷ total population in the selected cut.
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Explore the organisation")
st.sidebar.caption("All survey insights are aggregated. Groups with fewer than 5 respondents are suppressed.")

all_months=sorted(df["month"].unique())
selected_months=st.sidebar.multiselect(
    "Month(s)", options=all_months, default=[all_months[-1]],
    format_func=lambda x: pd.Timestamp(x).strftime("%b %Y"),
    help="Select one or multiple months to view an aggregate."
)
if not selected_months:
    st.sidebar.warning("Select at least one month.")
    st.stop()

selected_df=df[df["month"].isin(selected_months)].copy()

def add_filter(label,column):
    values=["All"]+sorted(selected_df[column].dropna().unique().tolist())
    return st.sidebar.selectbox(label,values)

division_filter=add_filter("Division","division")
city_filter=add_filter("City","city")
level_filter=add_filter("Job Level","job_level")
tenure_filter=add_filter("Tenure","tenure")
performance_filter=add_filter("Performance","performance")
talent_filter=add_filter("Talent Mapping","talent")
gender_filter=add_filter("Gender","gender")
manager_filter=add_filter("Manager","manager")

def apply_filters(data):
    filtered=data.copy()
    filters={
        "division":division_filter,"city":city_filter,"job_level":level_filter,
        "tenure":tenure_filter,"performance":performance_filter,"talent":talent_filter,
        "gender":gender_filter,"manager":manager_filter,
    }
    for col,value in filters.items():
        if value!="All":
            filtered=filtered[filtered[col]==value]
    return filtered

filtered_selected=apply_filters(selected_df)
filtered_all=apply_filters(df)

def unique_headcount(data):
    return data["employee_id"].nunique()

def respondent_count(data):
    return data.loc[data["survey_participated"],"employee_id"].nunique()

def participation_rate(data):
    hc=unique_headcount(data)
    return respondent_count(data)/hc*100 if hc else np.nan

def survey_mean(data,col):
    resp=data[data["survey_participated"]]
    if resp["employee_id"].nunique()<MIN_RESPONDENTS:
        return np.nan
    return resp[col].mean()

def pct_or_lock(value):
    return "🔒 Suppressed" if pd.isna(value) else f"{value:.1f}%"

group_size=unique_headcount(filtered_selected)
respondents=respondent_count(filtered_selected)
if group_size==0:
    st.warning("No employees match the selected filters.")
    st.stop()
if respondents<MIN_RESPONDENTS:
    st.warning(f"🔒 Survey insights are suppressed because only {respondents} respondents match this cut. Minimum required: {MIN_RESPONDENTS}.")
    st.caption(f"Population size: {group_size}. Participation can be shown, but no survey-derived scores will populate.")

selected_sorted=sorted(pd.to_datetime(selected_months))
if len(selected_sorted)==1:
    comparison_months=[selected_sorted[0]-pd.DateOffset(months=1)]
else:
    comparison_months=list(pd.date_range(end=selected_sorted[0]-pd.DateOffset(months=1),periods=len(selected_sorted),freq="MS"))

current=filtered_selected
comparison=apply_filters(df[df["month"].isin(comparison_months)].copy())

current_pulse=survey_mean(current,"pulse")
current_workload=survey_mean(current,"workload_pressure")
current_manager=survey_mean(current,"manager_connection")
current_risk=survey_mean(current,"flight_risk_signal")
current_one_to_one=survey_mean(current,"one_to_one_completion")
current_career=survey_mean(current,"career_sentiment")
current_participation=participation_rate(current)
previous_pulse=survey_mean(comparison,"pulse")
previous_workload=survey_mean(comparison,"workload_pressure")
previous_manager=survey_mean(comparison,"manager_connection")
previous_risk=survey_mean(comparison,"flight_risk_signal")

def delta_text(current_value,previous_value):
    if pd.isna(current_value) or pd.isna(previous_value):
        return None
    return f"{current_value-previous_value:+.1f} pts"

def safe_groupby(data,group_col,order=None):
    rows=[]
    for group_value,g in data.groupby(group_col):
        hc=unique_headcount(g)
        resp=respondent_count(g)
        row={group_col:group_value,"Headcount":hc,"Respondents":resp,"Participation":(resp/hc*100) if hc else np.nan}
        if resp>=MIN_RESPONDENTS:
            r=g[g["survey_participated"]]
            row.update({
                "Pulse":r["pulse"].mean(),"Workload":r["workload_pressure"].mean(),
                "Manager Connection":r["manager_connection"].mean(),"1:1 Completion":r["one_to_one_completion"].mean(),
                "Career Sentiment":r["career_sentiment"].mean(),"Flight Risk":r["flight_risk_signal"].mean(),
            })
        else:
            row.update({"Pulse":np.nan,"Workload":np.nan,"Manager Connection":np.nan,"1:1 Completion":np.nan,"Career Sentiment":np.nan,"Flight Risk":np.nan})
        rows.append(row)
    result=pd.DataFrame(rows)
    if order:
        result[group_col]=pd.Categorical(result[group_col],categories=order,ordered=True)
        result=result.sort_values(group_col)
    return result

tabs=st.tabs(["🏠 Executive Pulse","🌤 People Weather","🎯 Talent & Risk","👥 Manager Health","✨ AI Actions"])

with tabs[0]:
    st.subheader("Executive Pulse")
    month_label=(pd.Timestamp(selected_sorted[0]).strftime("%b %Y") if len(selected_sorted)==1 else f"{pd.Timestamp(selected_sorted[0]).strftime('%b %Y')} – {pd.Timestamp(selected_sorted[-1]).strftime('%b %Y')}")
    st.caption(f"Current view: {group_size} employees • {respondents} respondents • {month_label}")

    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric("Headcount",group_size)
    c2.metric("Participation",f"{current_participation:.1f}%")
    c3.metric("Pulse",pct_or_lock(current_pulse),delta_text(current_pulse,previous_pulse))
    c4.metric("Workload Pressure",pct_or_lock(current_workload),delta_text(current_workload,previous_workload),delta_color="inverse")
    c5.metric("Manager Connection",pct_or_lock(current_manager),delta_text(current_manager,previous_manager))
    c6.metric("Flight Risk Signal",pct_or_lock(current_risk),delta_text(current_risk,previous_risk),delta_color="inverse")

    st.divider()
    st.markdown("### Four views for a quick leadership scan")
    col1,col2=st.columns(2)
    with col1:
        st.markdown("#### 1. 12-month trend")
        trend_rows=[]
        for month,g in filtered_all.groupby("month"):
            if respondent_count(g)>=MIN_RESPONDENTS:
                trend_rows.append({"month":month,"Pulse":survey_mean(g,"pulse"),"Manager Connection":survey_mean(g,"manager_connection"),"Career Sentiment":survey_mean(g,"career_sentiment")})
        trend=pd.DataFrame(trend_rows).set_index("month")
        st.line_chart(trend,height=300)
    with col2:
        st.markdown("#### 2. Manager-wise Pulse")
        manager_view=safe_groupby(current,"manager")
        st.bar_chart(manager_view.dropna(subset=["Pulse"]).set_index("manager")[["Pulse"]],height=300)

    col3,col4=st.columns(2)
    with col3:
        st.markdown("#### 3. Division-wise Pulse & Workload")
        division_view=safe_groupby(current,"division")
        st.bar_chart(division_view.dropna(subset=["Pulse"]).set_index("division")[["Pulse","Workload"]],height=300)
    with col4:
        st.markdown("#### 4. Performance × Talent Mapping")
        perf_talent_rows=[]
        for (perf,talent_seg),g in current.groupby(["performance","talent"]):
            if respondent_count(g)>=MIN_RESPONDENTS:
                perf_talent_rows.append({"Segment":f"{perf} | {talent_seg}","Pulse":survey_mean(g,"pulse"),"Flight Risk":survey_mean(g,"flight_risk_signal")})
        perf_talent=pd.DataFrame(perf_talent_rows)
        if not perf_talent.empty:
            st.bar_chart(perf_talent.set_index("Segment")[["Pulse","Flight Risk"]],height=300)
        else:
            st.info("No segment meets the minimum respondent threshold.")

    st.markdown("#### AI: What changed?")
    ai_messages=[]
    if not pd.isna(current_workload) and not pd.isna(previous_workload):
        diff=current_workload-previous_workload
        if diff>=3: ai_messages.append(f"Workload pressure rose by {diff:.1f} points versus the comparison period.")
        elif diff<=-3: ai_messages.append(f"Workload pressure improved by {abs(diff):.1f} points versus the comparison period.")
    if not pd.isna(current_pulse) and not pd.isna(previous_pulse):
        diff=current_pulse-previous_pulse
        if diff>=3: ai_messages.append(f"Pulse improved by {diff:.1f} points, indicating stronger employee sentiment.")
        elif diff<=-3: ai_messages.append(f"Pulse declined by {abs(diff):.1f} points and merits a closer look.")
    if not pd.isna(current_manager) and not pd.isna(previous_manager):
        diff=current_manager-previous_manager
        if diff>=3: ai_messages.append(f"Manager Connection strengthened by {diff:.1f} points.")
        elif diff<=-3: ai_messages.append(f"Manager Connection fell by {abs(diff):.1f} points.")
    if current_participation<60:
        ai_messages.append(f"Participation is only {current_participation:.1f}%, so insights should be interpreted cautiously.")
    if not ai_messages:
        ai_messages.append("The selected population is broadly stable versus the comparison period. No leading indicator moved by more than 3 points.")
    st.markdown('<div class="ai-box"><b>AI summary</b><br>'+"<br>".join([f"• {x}" for x in ai_messages])+'</div>',unsafe_allow_html=True)

with tabs[1]:
    st.subheader("People Weather")
    st.write("A quick view of where organisational health is strong, stable or under pressure.")
    weather=safe_groupby(current,"division")

    def health_score(row):
        if pd.isna(row["Pulse"]): return np.nan
        return row["Pulse"]*.28 + row["Manager Connection"]*.22 + row["Career Sentiment"]*.18 + row["1:1 Completion"]*.12 + (100-row["Workload"])*.10 + (100-row["Flight Risk"])*.10

    weather["Health Score"]=weather.apply(health_score,axis=1)
    def weather_label(score):
        if pd.isna(score): return "🔒 Suppressed"
        if score>=74: return "☀️ Clear"
        if score>=66: return "🌤 Stable"
        if score>=58: return "🌥 Watch"
        return "🌧 Pressure"
    weather["People Weather"]=weather["Health Score"].apply(weather_label)
    display_weather=weather[["division","Headcount","Respondents","Participation","People Weather","Health Score","Pulse","Workload","Manager Connection","Flight Risk"]].copy()
    display_weather.columns=["Division","Headcount","Respondents","Participation %","People Weather","Health Score %","Pulse %","Workload %","Manager Connection %","Flight Risk %"]
    for col in ["Participation %","Health Score %","Pulse %","Workload %","Manager Connection %","Flight Risk %"]:
        display_weather[col]=display_weather[col].round(1)
    st.dataframe(display_weather,use_container_width=True,hide_index=True)
    st.markdown("#### Workload pressure by division")
    st.bar_chart(weather.dropna(subset=["Workload"]).set_index("division")[["Workload"]])

with tabs[2]:
    st.subheader("Talent & Flight-Risk Signals")
    st.caption("Group-level signals only. People Pulse never labels an individual employee as a flight risk.")
    talent_order=["Critical Talent","High Potential","Core Talent"]
    talent_view=safe_groupby(current,"talent",order=talent_order)
    display_talent=talent_view[["talent","Headcount","Respondents","Participation","Pulse","Workload","Manager Connection","1:1 Completion","Career Sentiment","Flight Risk"]].copy()
    display_talent.columns=["Talent Segment","Headcount","Respondents","Participation %","Pulse %","Workload %","Manager Connection %","1:1 Completion %","Career Sentiment %","Flight Risk %"]
    for col in display_talent.columns[3:]:
        display_talent[col]=display_talent[col].round(1)
    st.dataframe(display_talent,use_container_width=True,hide_index=True)

    st.markdown("#### Where is career risk concentrated?")
    tenure_view=safe_groupby(current,"tenure")
    st.bar_chart(tenure_view.dropna(subset=["Career Sentiment"]).set_index("tenure")[["Career Sentiment","Flight Risk"]])

    two_four_exceptional=current[(current["tenure"]=="2–4 years") & (current["performance"]=="Exceptional")]
    if respondent_count(two_four_exceptional)>=MIN_RESPONDENTS:
        risk=survey_mean(two_four_exceptional,"flight_risk_signal")
        career=survey_mean(two_four_exceptional,"career_sentiment")
        st.markdown(f'<div class="ai-box"><b>AI signal:</b> 2–4 year exceptional performers show a <b>{risk:.1f}% Flight Risk Signal</b> and <b>{career:.1f}% Career Sentiment</b>.<br><br><b>Suggested action:</b> prioritise career-path conversations, internal mobility and role-expansion opportunities for this cohort.</div>',unsafe_allow_html=True)

with tabs[3]:
    st.subheader("Manager Health")
    st.write("A manager-level view of connection, cadence, workload and participation. Survey results do not populate for fewer than 5 respondents.")
    manager_order=["Anuj","Beena","Cassie","Farah","Priya","Tina","Ronit","Yusuf","Rafee","Zainab"]
    manager_health=safe_groupby(current,"manager",order=manager_order)
    manager_display=manager_health.copy()
    manager_display["Participation %"]=manager_display["Participation"].round(1)
    for col in ["Pulse","Workload","Manager Connection","1:1 Completion","Career Sentiment","Flight Risk"]:
        manager_display[col]=manager_display[col].apply(pct_or_lock)
    manager_display=manager_display[["manager","Headcount","Respondents","Participation %","Pulse","Manager Connection","1:1 Completion","Workload","Flight Risk"]]
    manager_display.columns=["Manager","Team Size","Respondents","Participation %","Pulse","Manager Connection","1:1 Completion","Workload","Flight Risk"]
    st.dataframe(manager_display,use_container_width=True,hide_index=True)

    st.markdown("#### Manager Risk Radar")
    radar=manager_health.dropna(subset=["Manager Connection","Workload"]).copy()
    if not radar.empty:
        st.scatter_chart(radar,x="Manager Connection",y="Workload",size="Headcount")
    zainab_row=manager_health[manager_health["manager"]=="Zainab"]
    if not zainab_row.empty:
        st.info(f"🔒 Zainab has {int(zainab_row.iloc[0]['Respondents'])} respondents in this view. Her survey scores are intentionally suppressed because the minimum is 5.")

with tabs[4]:
    st.subheader("AI Intervention Planner")
    st.write("Recommendations adapt to the selected months and organisational cut.")
    issues=[]
    positives=[]
    if current_participation<60:
        issues.append(("Participation",f"Participation is {current_participation:.1f}%. Improve response coverage before drawing strong conclusions."))
    if not pd.isna(current_workload):
        if current_workload>=60: issues.append(("Workload",f"Workload Pressure is elevated at {current_workload:.1f}%. Review account load, escalation volume and resourcing."))
        elif current_workload<40: positives.append(f"Workload Pressure is healthy at {current_workload:.1f}%.")
    if not pd.isna(current_manager):
        if current_manager<65: issues.append(("Manager connection",f"Manager Connection is {current_manager:.1f}%. Prioritise manager check-ins and quality 1:1s."))
        elif current_manager>=75: positives.append(f"Manager Connection is strong at {current_manager:.1f}%.")
    if not pd.isna(current_risk):
        if current_risk>=45: issues.append(("Retention",f"Flight Risk Signal is elevated at {current_risk:.1f}%. Review career mobility, critical roles and manager hotspots."))
        elif current_risk<30: positives.append(f"Flight Risk Signal is currently low at {current_risk:.1f}%.")
    if not pd.isna(current_career):
        if current_career<65: issues.append(("Career",f"Career Sentiment is {current_career:.1f}%. Prioritise progression clarity and internal opportunities."))
        elif current_career>=75: positives.append(f"Career Sentiment is healthy at {current_career:.1f}%.")
    if not pd.isna(current_one_to_one) and current_one_to_one<70:
        issues.append(("Manager cadence",f"1:1 Completion is {current_one_to_one:.1f}%. Reinforce manager cadence before the next pulse."))

    if positives:
        st.markdown('<div class="good-box"><b>What is working</b><br>'+"<br>".join([f"• {x}" for x in positives])+'</div>',unsafe_allow_html=True)
    if issues:
        st.markdown('<div class="ai-box"><b>Priority actions</b><br>'+"<br>".join([f"• <b>{name}:</b> {msg}" for name,msg in issues])+'</div>',unsafe_allow_html=True)
    else:
        st.success("No material threshold is currently breached for the selected population. Maintain the current operating rhythm and keep monitoring leading indicators.")

    st.markdown("#### Why am I seeing this?")
    st.write("People Pulse uses aggregated signals across Pulse, workload, manager connection, career sentiment, 1:1 completion, talent mapping and retention indicators. The AI layer explains patterns and recommends possible interventions; it does not make employment decisions or expose individual responses.")
    st.info("Prototype principle: deterministic analytics calculate the metrics. AI interprets the signals and recommends action.")

st.divider()
st.caption("People Pulse prototype • Synthetic Customer Success data • 500 employees • No individual employee records or comments displayed • Survey insights with fewer than 5 respondents are suppressed.")
