"""
Page 1 — Interactive County Health Map
"""
import streamlit as st
import numpy as np, pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_utils import load_data, get_counties, get_state_avgs, inject_theme_css, COORDS

st.set_page_config(page_title="County Map", page_icon="🗺️", layout="wide")
inject_theme_css()

df_all = load_data()
df_c   = get_counties(df_all)
savgs  = get_state_avgs(df_all)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🗺️ County Health Map</h1>
    <p>Select a health topic and indicator — see every county on the map, then explore the ranking below</p>
</div>
""", unsafe_allow_html=True)

# ── Filters ──────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    topic = st.selectbox("Health Topic", sorted(df_c['health_topic'].unique()))
with c2:
    indicators = sorted(df_c[df_c['health_topic'] == topic]['indicator'].unique())
    indicator = st.selectbox("Indicator", indicators)

# ── Data ─────────────────────────────────────────────────────────────────────
filt = df_c[(df_c['health_topic'] == topic) & (df_c['indicator'] == indicator)]
mdata = (filt.groupby('county_name')
         .agg(rate=('percent_rate', 'mean'), lat=('lat', 'first'), lon=('lon', 'first'),
              years=('data_years', 'first'))
         .dropna(subset=['lat', 'lon']).reset_index())

if len(mdata) == 0:
    st.warning("No data for this selection.")
    st.stop()

sa = savgs.get(indicator)

# ── Metrics ──────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Counties with Data", len(mdata))
if sa: c2.metric("State Average", f"{sa:.1f}")
c3.metric("Data Period", mdata['years'].iloc[0] if len(mdata) > 0 else "—")

# ── Map ──────────────────────────────────────────────────────────────────────
fig = px.scatter_mapbox(
    mdata, lat='lat', lon='lon',
    size='rate', color='rate',
    hover_name='county_name',
    hover_data={'rate': ':.1f', 'lat': False, 'lon': False},
    color_continuous_scale=[[0, '#059669'], [0.5, '#fbbf24'], [1, '#dc2626']],
    size_max=24, zoom=5.8, opacity=0.85,
    mapbox_style="carto-positron",
    center={"lat": 42.85, "lon": -75.5},
)
fig.update_layout(
    height=500, margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Rate", thickness=14, len=0.5)
)
st.plotly_chart(fig, use_container_width=True)

# ── Bar Ranking ──────────────────────────────────────────────────────────────
st.subheader("County Ranking")
sort_dir = st.radio("Sort:", ["Highest First", "Lowest First"], horizontal=True)
mdata_s = mdata.sort_values('rate', ascending=(sort_dir == "Lowest First"))

fig = go.Figure(go.Bar(
    x=mdata_s['rate'], y=mdata_s['county_name'], orientation='h',
    marker=dict(
        color=mdata_s['rate'],
        colorscale=[[0, '#059669'], [0.5, '#fbbf24'], [1, '#dc2626']],
        cornerradius=4
    ),
    text=mdata_s['rate'].apply(lambda x: f'{x:.1f}'),
    textposition='outside', textfont=dict(size=10)
))
if sa:
    fig.add_vline(x=sa, line_dash="dot", line_color="gray", line_width=1.5,
                  annotation_text="State Avg", annotation_font_size=10)
fig.update_layout(
    height=max(350, len(mdata_s) * 18),
    margin=dict(l=0, r=40, t=10, b=0),
    xaxis=dict(showgrid=False, title='Rate'),
    yaxis=dict(showgrid=False, categoryorder='total ascending' if sort_dir == "Highest First" else 'total descending'),
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter')
)
st.plotly_chart(fig, use_container_width=True)

# ── Data Table ───────────────────────────────────────────────────────────────
with st.expander("📋 Raw Data"):
    st.dataframe(mdata[['county_name', 'rate', 'years']].sort_values('rate', ascending=False).reset_index(drop=True),
                 use_container_width=True)
