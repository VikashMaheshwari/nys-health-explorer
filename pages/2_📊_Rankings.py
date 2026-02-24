"""
Page 2 — County Health Burden Rankings
"""
import streamlit as st
import numpy as np, pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_utils import load_data, get_counties, get_state_avgs, compute_burden, inject_theme_css, COORDS

st.set_page_config(page_title="Rankings", page_icon="📊", layout="wide")
inject_theme_css()

df_all = load_data()
df_c   = get_counties(df_all)
savgs  = get_state_avgs(df_all)
burden = compute_burden(df_c, savgs)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📊 County Health Burden Rankings</h1>
    <p>All 62 counties ranked by average health burden — ratio above 1.0 means worse than state average</p>
</div>
""", unsafe_allow_html=True)

burden_df = burden.reset_index()
burden_df.columns = ['County', 'Ratio']

n_show = st.slider("Show top N:", 8, 30, 12)

c1, c2 = st.columns(2)

with c1:
    st.subheader("🔴 Highest Burden")
    top = burden_df.head(n_show).sort_values('Ratio')
    fig = go.Figure(go.Bar(
        x=top['Ratio'], y=top['County'], orientation='h',
        marker=dict(color=top['Ratio'],
                    colorscale=[[0, '#fca5a5'], [1, '#991b1b']], cornerradius=4),
        text=top['Ratio'].apply(lambda x: f'{x:.2f}x'),
        textposition='outside', textfont=dict(size=11)
    ))
    fig.add_vline(x=1.0, line_dash="dot", line_color="gray", line_width=1.5)
    fig.update_layout(
        height=max(300, n_show * 30),
        margin=dict(l=0, r=50, t=10, b=0),
        xaxis=dict(showgrid=False, range=[0.9, burden_df['Ratio'].max() * 1.1]),
        yaxis=dict(showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter')
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🟢 Healthiest Counties")
    bot = burden_df.tail(n_show).sort_values('Ratio', ascending=False)
    fig = go.Figure(go.Bar(
        x=bot['Ratio'], y=bot['County'], orientation='h',
        marker=dict(color=bot['Ratio'],
                    colorscale=[[0, '#065f46'], [1, '#a7f3d0']], cornerradius=4),
        text=bot['Ratio'].apply(lambda x: f'{x:.2f}x'),
        textposition='outside', textfont=dict(size=11)
    ))
    fig.add_vline(x=1.0, line_dash="dot", line_color="gray", line_width=1.5)
    fig.update_layout(
        height=max(300, n_show * 30),
        margin=dict(l=0, r=50, t=10, b=0),
        xaxis=dict(showgrid=False, range=[0, 1.08]),
        yaxis=dict(showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter')
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Map ──────────────────────────────────────────────────────────────────────
st.subheader("Geographic View")

bmap = burden_df.copy()
bmap['lat'] = bmap['County'].map(lambda x: COORDS.get(x, (np.nan, np.nan))[0])
bmap['lon'] = bmap['County'].map(lambda x: COORDS.get(x, (np.nan, np.nan))[1])
bmap['Status'] = bmap['Ratio'].apply(lambda x: 'Above Avg' if x > 1 else 'Below Avg')
bmap = bmap.dropna(subset=['lat', 'lon'])

fig = px.scatter_mapbox(
    bmap, lat='lat', lon='lon',
    size='Ratio', color='Ratio',
    hover_name='County',
    hover_data={'Ratio': ':.2f', 'Status': True, 'lat': False, 'lon': False},
    color_continuous_scale=[[0, '#059669'], [0.45, '#fbbf24'], [1, '#dc2626']],
    size_max=22, zoom=5.5, opacity=0.85,
    mapbox_style="carto-positron",
    center={"lat": 42.85, "lon": -75.5},
)
fig.update_layout(
    height=480, margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Ratio", thickness=14, len=0.5)
)
st.plotly_chart(fig, use_container_width=True)
