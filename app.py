"""
NYS County Health Explorer — Main Entry (Overview Page)
"""
import streamlit as st
import plotly.express as px
from data_utils import load_data, get_counties, get_state_avgs, compute_burden, inject_theme_css, COORDS

st.set_page_config(
    page_title="NYS Health Explorer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_theme_css()

# ── Load Data ────────────────────────────────────────────────────────────────
df_all = load_data()
df_c   = get_counties(df_all)
savgs  = get_state_avgs(df_all)
burden = compute_burden(df_c, savgs)

n_counties = df_c['county_name'].nunique()
n_topics   = df_c['health_topic'].nunique()
n_indic    = df_c['indicator'].nunique()
n_records  = len(df_c)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🩺 NYS County Health Explorer</h1>
    <p>Interactive analysis of <span class="accent">25,000+</span> health records across
       <span class="accent">62 counties</span> ·
       <span class="accent">15 health topics</span> ·
       <span class="accent">300+ indicators</span></p>
    <p style="margin-top:0.3rem;">Data: NYS DOH Community Health Indicator Reports (CHIRS) · health.data.ny.gov</p>
</div>
""", unsafe_allow_html=True)

# ── Stat Cards ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-row">
    <div class="stat-card c1"><div class="number">{n_counties}</div><div class="label">Counties</div></div>
    <div class="stat-card c2"><div class="number">{n_topics}</div><div class="label">Health Topics</div></div>
    <div class="stat-card c3"><div class="number">{n_indic}</div><div class="label">Indicators</div></div>
    <div class="stat-card c4"><div class="number">{n_records:,}</div><div class="label">Records</div></div>
</div>
""", unsafe_allow_html=True)

# ── Topics Bar ───────────────────────────────────────────────────────────────
st.subheader("Health Topics at a Glance")

topic_counts = (df_c.groupby('health_topic')['indicator'].count()
                .sort_values(ascending=True).reset_index())
topic_counts.columns = ['Topic', 'Records']
topic_counts['Short'] = topic_counts['Topic'].str.replace(' Indicators', '')

fig = px.bar(
    topic_counts, y='Short', x='Records', orientation='h',
    color='Records',
    color_continuous_scale=['#99f6e4', '#14b8a6', '#0f766e'],
    text='Records'
)
fig.update_traces(textposition='outside', textfont_size=11)
fig.update_layout(
    height=480,
    margin=dict(l=0, r=30, t=10, b=0),
    xaxis=dict(showgrid=False, title=''),
    yaxis=dict(showgrid=False, title=''),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    coloraxis_showscale=False,
    font=dict(family='Inter')
)
st.plotly_chart(fig, use_container_width=True)

# ── Quick Map ────────────────────────────────────────────────────────────────
st.subheader("County Overview Map")

bmap = burden.reset_index()
bmap.columns = ['County', 'Ratio']
bmap['lat'] = bmap['County'].map(lambda x: COORDS.get(x, (None, None))[0])
bmap['lon'] = bmap['County'].map(lambda x: COORDS.get(x, (None, None))[1])
bmap = bmap.dropna(subset=['lat', 'lon'])

fig = px.scatter_mapbox(
    bmap, lat='lat', lon='lon',
    size='Ratio', color='Ratio',
    hover_name='County',
    hover_data={'Ratio': ':.2f', 'lat': False, 'lon': False},
    color_continuous_scale=[[0, '#059669'], [0.45, '#fbbf24'], [1, '#dc2626']],
    size_max=22, zoom=5.5, opacity=0.85,
    mapbox_style="carto-positron",
    center={"lat": 42.85, "lon": -75.5},
)
fig.update_layout(
    height=480,
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Burden", thickness=14, len=0.5)
)
st.plotly_chart(fig, use_container_width=True)

st.info("👈 **Use the sidebar** to navigate between pages — County Map, Rankings, Deep Dive, Topic Spotlight, and ML Clusters.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown('<div class="foot">NYS County Health Explorer · Vikash Maheshwari · Python · Streamlit · Plotly · scikit-learn</div>', unsafe_allow_html=True)
