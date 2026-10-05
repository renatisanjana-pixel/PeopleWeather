import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='People Pulse | Customer Success', page_icon='🟣', layout='wide')

MIN_RESPONDENTS = 5

st.markdown('''
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 3rem;}
[data-testid="stMetric"]{background:#fff;border:1px solid #ececf2;padding:12px 14px;border-radius:14px;}
[data-testid="stMetricLabel"]{font-size:.86rem;}
[data-testid="stMetricValue"]{font-size:1.95rem;}
.pp-header{padding:22px 26px;border-radius:18px;background:linear-gradient(120deg,#4C1D95,#7C3AED,#A855F7);color:white;margin-bottom:12px;}
.pp-header h1{margin:0;font-size:34px;}
.pp-header p{margin:7px 0 0;opacity:.94;line-height:1.45;}
.privacy{display:inline-block;padding:7px 12px;border-radius:18px;background:#F3E8FF;color:#6B21A8;font-weight:600;font-size:13px;margin-bottom:8px;}
.ai-good{padding:16px 18px;background:#F0FDF4;border-left:5px solid #22C55E;border-radius:12px;margin:8px 0;}
.ai-watch{padding:16px 18px;background:#FFF7ED;border-left:5px solid #F97316;border-radius:12px;margin:8px 0;}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 500
    employees = pd.DataFrame({'employee_id':[f'E{i:03d}' for i in range(1,n+1)]})

    divisions = ['Enterprise CS']*145 + ['Mid-Market CS']*115 + ['SMB CS']*90 + ['Customer Support']*85 + ['CS Operations']*65
    np.random.shuffle(divisions)
    employees['division'] = divisions
    employees['city'] = np.random.choice(['Bengaluru','Mumbai','Delhi NCR','Hyderabad','Pune'], n, p=[.42,.18,.15,.15,.10])
    employees['job_level'] = np.random.choice(['L1','L2','L3','L4'], n, p=[.25,.35,.25,.15])
    employees['tenure'] = np.random.choice(['<1 year','1–2 years','2–4 years','4+ years'], n, p=[.16,.24,.35,.25])
    employees['performance'] = np.random.choice(['Developing','Strong','Exceptional'], n, p=[.10,.68,.22])
    employees['talent'] = np.random.choice(['Core Talent','High Potential','Top Talent'], n, p=[.72,.18,.10])

    genders = np.array(['Male']*265 + ['Female']*225 + ['Others']*10)
    np.random.shuffle(genders)
    employees['gender'] = genders

    managers = ['Anuj','Cassie','Rafee','Priya','Zainab']
    manager_values = np.repeat(managers, 100)
    np.random.shuffle(manager_values)
    employees['manager'] = manager_values

    months = pd.date_range('2025-10-01', periods=12, freq='MS')
    employees['join_month'] = np.random.choice(months, n)
    employees['exit_pipeline_flag'] = np.random.rand(n) < 0.055
    employees['internal_move_flag'] = np.random.rand(n) < 0.12
    employees['movement_type'] = np.where(
        employees['internal_move_flag'],
        np.random.choice(['IJP','Onsite Rotation','Role Expansion'], n, p=[.55,.25,.20]),
        'None'
    )

    voluntary_reasons = [
        'Better salary','Taking time off for personal/medical reasons','Onsite opportunity',
        'Better benefits package','Pursuing passion outside of corporate','Long Work Hours','Culture Mismatch'
    ]
    involuntary_types = [
        'Dismissal','Poor performance','Layoff / Retrenchment','Redundancy / Restructuring',
        'End of contract','Probation failure','Medical / Capability separation'
    ]

    rows = []
    for _, emp in employees.iterrows():
        base_sat = np.random.normal(74,7)
        base_manager = np.random.normal(76,7)
        base_team = np.random.normal(78,7)
        base_wellbeing = np.random.normal(70,8)
        base_learning = np.random.normal(72,7)
        base_innovation = np.random.normal(68,8)
        base_inclusivity = np.random.normal(77,6)
        base_pulse = np.random.normal(74,6)
        base_11 = np.random.normal(82,8)
        base_skip = np.random.normal(62,9)
        base_coach = np.random.normal(65,9)
        base_learn_score = np.random.normal(71,7)
        base_flight = np.random.normal(28,8)

        for mi, month in enumerate(months):
            div = emp['division']
            mgr = emp['manager']
            sat = base_sat + np.random.normal(0,3)
            manager_theme = base_manager + np.random.normal(0,3)
            team = base_team + np.random.normal(0,3)
            wellbeing = base_wellbeing + np.random.normal(0,3)
            culture = np.random.normal(73,6)
            org_listening = np.random.normal(70,7)
            learning_theme = base_learning + np.random.normal(0,3)
            inclusivity = base_inclusivity + np.random.normal(0,3)
            innovation = base_innovation + np.random.normal(0,3)
            work = np.random.normal(67,7)
            team_pulse = base_pulse + np.random.normal(0,3)
            one_to_one = base_11 + np.random.normal(0,3)
            skip = base_skip + np.random.normal(0,3)
            coaching = base_coach + np.random.normal(0,3)
            learning_score = base_learn_score + np.random.normal(0,3)
            flight = base_flight + np.random.normal(0,3)

            if div == 'Enterprise CS' and mi >= 7:
                sat -= 7; work -= 9; wellbeing -= 8; team_pulse -= 6; flight += 12
            if mgr == 'Rafee' and mi >= 6:
                one_to_one -= 12; manager_theme -= 9; team_pulse -= 6; flight += 8
            if mgr == 'Priya' and mi >= 8:
                one_to_one += 8; coaching += 10; team_pulse += 5; manager_theme += 6
            if emp['performance'] == 'Exceptional' and emp['tenure'] == '2–4 years':
                flight += 10; learning_theme -= 5
            if emp['talent'] == 'Top Talent':
                flight += 6

            participation_prob = .84
            if mgr == 'Rafee' and mi >= 7: participation_prob = .72
            if mgr == 'Priya' and mi >= 8: participation_prob = .91
            survey_participated = np.random.rand() < participation_prob

            attrition_prob = .005
            if div == 'Enterprise CS' and mi >= 8: attrition_prob += .012
            if mgr == 'Rafee' and mi >= 7: attrition_prob += .008
            if emp['talent'] == 'Top Talent': attrition_prob += .003

            exit_event = np.random.rand() < attrition_prob
            exit_type = ''
            exit_reason = ''
            if exit_event:
                if np.random.rand() < .72:
                    exit_type = 'Voluntary'
                    exit_reason = np.random.choice(voluntary_reasons, p=[.27,.14,.12,.12,.10,.15,.10])
                else:
                    exit_type = 'Involuntary'
                    exit_reason = np.random.choice(involuntary_types, p=[.10,.28,.16,.18,.10,.12,.06])

            if emp['job_level'] in ['L3','L4']:
                successor_coverage = np.random.choice(['Ready now','Ready <12m','No successor'], p=[.36,.34,.30])
            else:
                successor_coverage = 'N/A'

            rows.append({
                'employee_id':emp['employee_id'],'month':month,'division':div,'city':emp['city'],
                'job_level':emp['job_level'],'tenure':emp['tenure'],'performance':emp['performance'],
                'talent':emp['talent'],'gender':emp['gender'],'manager':mgr,'join_month':emp['join_month'],
                'exit_pipeline_flag':emp['exit_pipeline_flag'],'internal_move_flag':emp['internal_move_flag'],
                'movement_type':emp['movement_type'],'survey_participated':survey_participated,
                'satisfaction':np.clip(sat,0,100),'theme_manager':np.clip(manager_theme,0,100),
                'theme_work':np.clip(work,0,100),'theme_team':np.clip(team,0,100),
                'theme_wellbeing':np.clip(wellbeing,0,100),'theme_culture':np.clip(culture,0,100),
                'theme_org_listening':np.clip(org_listening,0,100),'theme_learning':np.clip(learning_theme,0,100),
                'theme_inclusivity':np.clip(inclusivity,0,100),'theme_innovation':np.clip(innovation,0,100),
                'flight_risk':np.clip(flight,0,100),'successor_coverage':successor_coverage,
                'one_to_one':np.clip(one_to_one,0,100),'skip_level':np.clip(skip,0,100),
                'coaching':np.clip(coaching,0,100),'team_pulse':np.clip(team_pulse,0,100),
                'learning_score':np.clip(learning_score,0,100),'exit_event':int(exit_event),
                'exit_type':exit_type,'exit_reason':exit_reason
            })

    panel = pd.DataFrame(rows)

    role_rows = []
    role_base = {'Enterprise CS':14,'Mid-Market CS':10,'SMB CS':8,'Customer Support':12,'CS Operations':6}
    for month in months:
        for div, base in role_base.items():
            value = base + (5 if div == 'Enterprise CS' and month >= pd.Timestamp('2026-05-01') else 0)
            role_rows.append({'month':month,'division':div,'open_roles':max(0,int(np.random.normal(value,2)))})

    return panel, pd.DataFrame(role_rows)

df, open_roles_df = generate_data()

def headcount(data): return data['employee_id'].nunique()
def respondents(data): return data.loc[data['survey_participated'],'employee_id'].nunique()
def participation(data):
    hc = headcount(data)
    return respondents(data)/hc*100 if hc else np.nan

def survey_mean(data,col):
    if respondents(data) < MIN_RESPONDENTS: return np.nan
    return data.loc[data['survey_participated'],col].mean()

def pct(v): return '🔒' if pd.isna(v) else f'{v:.0f}%'

def percent_chart(fig,height=330):
    fig.update_yaxes(range=[0,100],ticksuffix='%')
    fig.update_layout(height=height,margin=dict(l=20,r=20,t=55,b=30))
    return fig

st.markdown('''
<div class="pp-header">
<h1>People Pulse</h1>
<p>Customer Success • People Health & Organisational Insights<br>
A focused view of workforce health, employee voice, talent and manager effectiveness.</p>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="privacy">🔒 Synthetic data • No individual records shown • Minimum survey group = 5</div>', unsafe_allow_html=True)

st.sidebar.title('Data cuts')
st.sidebar.caption('Leave blank to include all values.')
month_options = sorted(df['month'].unique())
sel_months = st.sidebar.multiselect('Month', month_options, default=[month_options[-1]], format_func=lambda x: pd.Timestamp(x).strftime('%b %Y'))

def multi_filter(label,col):
    return st.sidebar.multiselect(label, sorted(df[col].dropna().unique().tolist()), default=[])

sel_division = multi_filter('Division','division')
sel_city = multi_filter('City','city')
sel_level = multi_filter('Job Level','job_level')
sel_tenure = multi_filter('Tenure','tenure')
sel_perf = multi_filter('Performance','performance')
sel_talent = multi_filter('Talent','talent')
sel_gender = multi_filter('Gender','gender')
sel_manager = multi_filter('Manager','manager')

if not sel_months:
    st.sidebar.warning('Select at least one month.')
    st.stop()

def apply_filters(data):
    f = data[data['month'].isin(sel_months)].copy()
    mapping = {'division':sel_division,'city':sel_city,'job_level':sel_level,'tenure':sel_tenure,
               'performance':sel_perf,'talent':sel_talent,'gender':sel_gender,'manager':sel_manager}
    for col, values in mapping.items():
        if values: f = f[f[col].isin(values)]
    return f

filtered = apply_filters(df)
if filtered.empty:
    st.warning('No employees match this combination of filters.')
    st.stop()

tabs = st.tabs(['🏢 Organisation Overview','📉 Attrition','🎧 Employee Listening','🌟 Talent','👥 Manager Effectiveness'])

with tabs[0]:
    st.subheader('Organisation Overview')
    latest_month = max(pd.to_datetime(sel_months))
    latest = filtered[filtered['month']==latest_month].copy()
    hc = headcount(latest)
    joiners = latest.loc[latest['join_month']==latest_month,'employee_id'].nunique()
    exit_pipeline = latest.loc[latest['exit_pipeline_flag'],'employee_id'].nunique()
    internal_moves = latest.loc[latest['internal_move_flag'],'employee_id'].nunique()
    roles = open_roles_df[open_roles_df['month']==latest_month].copy()
    if sel_division: roles = roles[roles['division'].isin(sel_division)]
    open_roles = int(roles['open_roles'].sum())

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric('Headcount',hc); c2.metric('Joiners',joiners); c3.metric('Exit Pipeline',exit_pipeline)
    c4.metric('Open Roles',open_roles); c5.metric('Internal Moves',internal_moves)

    left,right = st.columns(2)
    with left:
        gender_counts = latest.drop_duplicates('employee_id')['gender'].value_counts().reset_index()
        gender_counts.columns=['Gender','Count']
        st.plotly_chart(px.pie(gender_counts,names='Gender',values='Count',hole=.45,title='Gender mix'),use_container_width=True)
    with right:
        trend = filtered.groupby('month')['employee_id'].nunique().reset_index(name='Headcount')
        st.plotly_chart(px.line(trend,x='month',y='Headcount',markers=True,title='Headcount trend'),use_container_width=True)

    positive=[]; watch=[]
    if internal_moves>=25: positive.append(f'Internal mobility is healthy with {internal_moves} employees moving internally.')
    if joiners>=15: positive.append(f'Hiring momentum is strong with {joiners} joiners in the latest month.')
    if open_roles<=45: positive.append(f'Open roles are relatively contained at {open_roles}.')
    if exit_pipeline>=20: watch.append(f'{exit_pipeline} employees are currently in the exit pipeline.')
    if open_roles>=50: watch.append(f'Open roles are elevated at {open_roles}, suggesting capacity pressure.')
    if joiners<8: watch.append(f'Joiner volume is low at {joiners}, which may slow backfills or growth.')
    if not positive: positive.append('Overall workforce movement is stable in the selected cut.')
    if not watch: watch.append('No major workforce pressure is visible in the selected cut.')

    st.markdown('<div class="ai-good"><b>Positive signal</b><br>'+ '<br>'.join('• '+x for x in positive) + '<br><br><b>Suggested action:</b> sustain internal mobility and preserve hiring momentum where demand is highest.</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-watch"><b>Watch-out</b><br>'+ '<br>'.join('• '+x for x in watch) + '<br><br><b>Suggested action:</b> review vacancies, exit pipeline and hiring capacity together before the next monthly review.</div>', unsafe_allow_html=True)

with tabs[1]:
    st.subheader('Attrition')
    monthly_attr = filtered.groupby('month').agg(Exits=('exit_event','sum'),HC=('employee_id','nunique')).reset_index()
    monthly_attr['Attrition %'] = monthly_attr['Exits']/monthly_attr['HC']*100
    fig = px.line(monthly_attr,x='month',y='Attrition %',markers=True,text='Attrition %',title='Monthly attrition')
    fig.update_traces(texttemplate='%{text:.1f}%',textposition='top center')
    st.plotly_chart(fig,use_container_width=True)

    q = filtered.copy(); q['Quarter']=q['month'].dt.to_period('Q').astype(str)
    quarterly = q.groupby('Quarter').agg(Exits=('exit_event','sum'),HC=('employee_id','nunique')).reset_index()
    quarterly['Attrition %']=quarterly['Exits']/quarterly['HC']*100
    ltm_exits = filtered['exit_event'].sum(); avg_hc = filtered.groupby('month')['employee_id'].nunique().mean(); ltm_attr = ltm_exits/avg_hc*100 if avg_hc else 0
    c1,c2,c3 = st.columns(3)
    c1.metric('LTM Attrition',f'{ltm_attr:.1f}%'); c2.metric('Voluntary Exits',int((filtered['exit_type']=='Voluntary').sum())); c3.metric('Involuntary Exits',int((filtered['exit_type']=='Involuntary').sum()))

    left,right=st.columns(2)
    with left:
        fig=px.bar(quarterly,x='Quarter',y='Attrition %',text='Attrition %',title='Quarterly attrition')
        fig.update_traces(texttemplate='%{text:.1f}%',textposition='outside'); st.plotly_chart(fig,use_container_width=True)
    with right:
        mix=filtered[filtered['exit_event']==1]['exit_type'].value_counts().reset_index(); mix.columns=['Type','Count']
        if len(mix): st.plotly_chart(px.pie(mix,names='Type',values='Count',hole=.45,title='Voluntary vs involuntary'),use_container_width=True)
        else: st.info('No exits in the selected cut.')

    voluntary=filtered[(filtered['exit_event']==1)&(filtered['exit_type']=='Voluntary')]['exit_reason'].value_counts().reset_index(); voluntary.columns=['Reason','Count']
    involuntary=filtered[(filtered['exit_event']==1)&(filtered['exit_type']=='Involuntary')]['exit_reason'].value_counts().reset_index(); involuntary.columns=['Reason','Count']
    left,right=st.columns(2)
    with left:
        st.markdown('#### Top voluntary exit reasons')
        if len(voluntary): st.plotly_chart(px.bar(voluntary,x='Count',y='Reason',orientation='h'),use_container_width=True)
        else: st.info('No voluntary exits in this cut.')
    with right:
        st.markdown('#### Involuntary separation types')
        if len(involuntary): st.plotly_chart(px.bar(involuntary,x='Count',y='Reason',orientation='h'),use_container_width=True)
        else: st.info('No involuntary exits in this cut.')

with tabs[2]:
    st.subheader('Employee Listening')
    c1,c2=st.columns(2); c1.metric('Satisfaction',pct(survey_mean(filtered,'satisfaction'))); c2.metric('Participation',f'{participation(filtered):.0f}%')
    theme_map={'Manager':'theme_manager','Work':'theme_work','Team':'theme_team','Wellbeing':'theme_wellbeing','Culture':'theme_culture','Org Listening':'theme_org_listening','Learning':'theme_learning','Inclusivity':'theme_inclusivity','Innovation':'theme_innovation'}
    themes=pd.DataFrame([{'Theme':name,'Sentiment':survey_mean(filtered,col)} for name,col in theme_map.items()]).dropna()
    fig=px.bar(themes.sort_values('Sentiment'),x='Sentiment',y='Theme',orientation='h',text='Sentiment',title='Current theme sentiment')
    fig.update_traces(texttemplate='%{text:.0f}%',textposition='outside'); fig.update_xaxes(range=[0,100],ticksuffix='%'); st.plotly_chart(fig,use_container_width=True)

    trend_rows=[]
    for month,g in filtered.groupby('month'):
        for name,col in theme_map.items():
            val=survey_mean(g,col)
            if not pd.isna(val): trend_rows.append({'Month':month,'Theme':name,'Sentiment':val})
    trend_themes=pd.DataFrame(trend_rows)
    selected_theme=st.selectbox('Sentiment trend theme',list(theme_map.keys()))
    t=trend_themes[trend_themes['Theme']==selected_theme]
    fig=px.line(t,x='Month',y='Sentiment',markers=True,text='Sentiment',title=f'{selected_theme} sentiment trend')
    fig.update_traces(texttemplate='%{text:.0f}%',textposition='top center'); st.plotly_chart(percent_chart(fig),use_container_width=True)

with tabs[3]:
    st.subheader('Talent')
    latest_month=max(pd.to_datetime(sel_months)); latest=filtered[filtered['month']==latest_month].copy()
    top_talent=latest[latest['talent']=='Top Talent']['employee_id'].nunique(); high_risk=latest[latest['flight_risk']>=45]['employee_id'].nunique()
    critical_roles=latest[latest['job_level'].isin(['L3','L4'])]; covered=critical_roles[critical_roles['successor_coverage']!='No successor']['employee_id'].nunique(); critical_total=critical_roles['employee_id'].nunique(); coverage=covered/critical_total*100 if critical_total else np.nan
    ijp=latest[latest['movement_type']=='IJP']['employee_id'].nunique(); onsite=latest[latest['movement_type']=='Onsite Rotation']['employee_id'].nunique()
    c1,c2,c3,c4,c5=st.columns(5); c1.metric('Top Talent',top_talent); c2.metric('High Flight Risk',high_risk); c3.metric('Successor Coverage',pct(coverage)); c4.metric('IJP Moves',ijp); c5.metric('Onsite Rotation',onsite)

    left,right=st.columns(2)
    with left:
        talent_mix=latest.drop_duplicates('employee_id')['talent'].value_counts().reset_index(); talent_mix.columns=['Talent','Count']
        st.plotly_chart(px.bar(talent_mix,x='Talent',y='Count',text='Count',title='Talent mix'),use_container_width=True)
    with right:
        mobility=latest[latest['movement_type']!='None']['movement_type'].value_counts().reset_index(); mobility.columns=['Movement','Count']
        if len(mobility): st.plotly_chart(px.bar(mobility,x='Movement',y='Count',text='Count',title='Internal mobility'),use_container_width=True)
        else: st.info('No internal mobility in the selected cut.')

    risk_by_talent=latest.groupby('talent')['flight_risk'].mean().reset_index()
    fig=px.bar(risk_by_talent,x='talent',y='flight_risk',text='flight_risk',title='Flight risk by talent segment')
    fig.update_traces(texttemplate='%{text:.0f}%',textposition='outside'); st.plotly_chart(percent_chart(fig),use_container_width=True)

with tabs[4]:
    st.subheader('Manager Effectiveness')
    manager_rows=[]
    for mgr,g in filtered.groupby('manager'):
        manager_rows.append({'Manager':mgr,'HC':headcount(g),'Respondents':respondents(g),'1:1 Coverage':survey_mean(g,'one_to_one'),'Skip Levels':survey_mean(g,'skip_level'),'Coaching':survey_mean(g,'coaching'),'Team Pulse':survey_mean(g,'team_pulse'),'Learning Score':survey_mean(g,'learning_score')})
    mgr_df=pd.DataFrame(manager_rows)
    st.dataframe(mgr_df.round(1),use_container_width=True,hide_index=True)
    metric_choice=st.selectbox('Manager metric',['1:1 Coverage','Skip Levels','Coaching','Team Pulse','Learning Score'])
    plot_df=mgr_df.dropna(subset=[metric_choice])
    fig=px.bar(plot_df,x='Manager',y=metric_choice,text=metric_choice,title=f'{metric_choice} by manager')
    fig.update_traces(texttemplate='%{text:.0f}%',textposition='outside'); st.plotly_chart(percent_chart(fig),use_container_width=True)
    if len(plot_df):
        best=plot_df.sort_values(metric_choice,ascending=False).iloc[0]; low=plot_df.sort_values(metric_choice).iloc[0]
        st.markdown(f'<div class="ai-good"><b>Positive signal</b><br>{best["Manager"]} is strongest on {metric_choice} at {best[metric_choice]:.0f}%.</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="ai-watch"><b>Watch-out</b><br>{low["Manager"]} is lowest on {metric_choice} at {low[metric_choice]:.0f}%.<br><br><b>Suggested action:</b> diagnose whether the gap is driven by cadence, capability, workload or team context before choosing an intervention.</div>',unsafe_allow_html=True)

st.divider()
st.caption('People Pulse prototype • Synthetic Customer Success data • 500 employees • No individual employee records or comments displayed.')
