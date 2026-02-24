"""
Page 4 — Health Topic Spotlight
"""
import streamlit as st
import numpy as np, pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data_utils import load_data, get_counties, inject_theme_css

st.set_page_config(page_title="Topic Spotlight", page_icon="🎯", layout="wide")
inject_theme_css()

df_all = load_data()
df_c   = get_counties(df_all)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎯 Health Topic Spotlight</h1>
    <p>Pick any health topic — see top counties, explore indicators, and discover cross-topic patterns</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Topic Explorer", "Cross-Topic Correlations"])

with tab1:
    topic = st.selectbox("Choose Topic", sorted(df_c['health_topic'].unique()))

    filt = df_c[df_c['health_topic'] == topic]
    county_avg = (filt.groupby('county_name')['percent_rate']
                  .mean().sort_values(ascending=False).head(15).reset_index())
    county_avg.columns = ['County', 'Rate']

    st.subheader(f"Top 15 Counties — {topic.replace(' Indicators', '')}")

    fig = go.Figure(go.Bar(
        x=county_avg['Rate'], y=county_avg['County'], orientation='h',
        marker=dict(
            color=county_avg['Rate'],
            colorscale=[[0, '#bfdbfe'], [0.5, '#3b82f6'], [1, '#1e3a8a']],
            cornerradius=5
        ),
        text=county_avg['Rate'].apply(lambda x: f'{x:.1f}'),
        textposition='outside', textfont=dict(size=11)
    ))
    fig.update_layout(
        height=max(350, len(county_avg) * 28),
        margin=dict(l=0, r=40, t=10, b=0),
        xaxis=dict(showgrid=False, title='Average Rate'),
        yaxis=dict(showgrid=False, categoryorder='total ascending'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Indicator breakdown
    st.subheader("Indicators in This Topic")
    inds = sorted(filt['indicator'].unique())
    st.caption(f"{len(inds)} indicators available")

    pick_ind = st.selectbox("Explore indicator:", inds)
    ind_data = filt[filt['indicator'] == pick_ind]
    ind_avg = (ind_data.groupby('county_name')['percent_rate'].mean()
               .sort_values(ascending=False).head(20).reset_index())
    ind_avg.columns = ['County', 'Rate']

    fig = go.Figure(go.Bar(
        x=ind_avg['Rate'], y=ind_avg['County'], orientation='h',
        marker=dict(color=ind_avg['Rate'],
                    colorscale=[[0, '#fde68a'], [0.5, '#f59e0b'], [1, '#92400e']],
                    cornerradius=4),
        text=ind_avg['Rate'].apply(lambda x: f'{x:.1f}'),
        textposition='outside', textfont=dict(size=10)
    ))
    fig.update_layout(
        height=max(300, len(ind_avg) * 22),
        margin=dict(l=0, r=40, t=10, b=0),
        xaxis=dict(showgrid=False, title='Rate'),
        yaxis=dict(showgrid=False, categoryorder='total ascending'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter')
    )
    st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.subheader("Which Health Topics Co-Occur?")
    st.caption("Positive correlation = topics tend to be high or low in the same counties")

    pivot = df_c.pivot_table(index='county_name', columns='health_topic',
                             values='percent_rate', aggfunc='mean').dropna(thresh=5)

    if len(pivot) > 10:
        corr = pivot.corr()
        labels = [c.replace(' Indicators', '').replace(' and ', ' & ')[:25] for c in corr.columns]

        fig = px.imshow(
            corr.values, x=labels, y=labels,
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1, text_auto='.2f',
        )
        fig.update_layout(
            height=580, width=680,
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(family='Inter', size=9),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info("**Example:** If Obesity and Diabetes are positively correlated (red), counties with high obesity also tend to have high diabetes — they share underlying risk factors.")
