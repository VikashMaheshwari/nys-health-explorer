"""
Page 3 — County Deep Dive
"""
import streamlit as st
import numpy as np, pandas as pd
import plotly.graph_objects as go
from data_utils import load_data, get_counties, get_state_avgs, inject_theme_css

st.set_page_config(page_title="County Dive", page_icon="🔍", layout="wide")
inject_theme_css()

df_all = load_data()
df_c   = get_counties(df_all)
savgs  = get_state_avgs(df_all)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🔍 County Deep Dive</h1>
    <p>Select any county to see its full health profile compared against the state average</p>
</div>
""", unsafe_allow_html=True)

county = st.selectbox("Choose a County", sorted(df_c['county_name'].unique()))

cd = df_c[df_c['county_name'] == county]
comps = []
for _, r in cd.iterrows():
    sa = savgs.get(r.get('indicator'))
    cr = r.get('percent_rate')
    if pd.notna(cr) and pd.notna(sa) and sa != 0:
        comps.append({
            'topic': r['health_topic'],
            'indicator': r['indicator'],
            'county_rate': cr,
            'state_rate': sa,
            'ratio': cr / sa
        })

if not comps:
    st.warning("No comparison data available.")
    st.stop()

df_comp = pd.DataFrame(comps)

# ── Summary Metrics ──────────────────────────────────────────────────────────
overall = df_comp['ratio'].mean()
above = (df_comp['ratio'] > 1.0).sum()
below = (df_comp['ratio'] <= 1.0).sum()

c1, c2, c3 = st.columns(3)
c1.metric("Overall Ratio", f"{overall:.2f}x", delta="Above Avg" if overall > 1 else "Below Avg",
          delta_color="inverse")
c2.metric("Indicators Above State", f"{above}")
c3.metric("Indicators Below State", f"{below}")

# ── Topic Ratio Bar ──────────────────────────────────────────────────────────
st.subheader(f"{county} — Disparity by Health Topic")

topic_avg = (df_comp.groupby('topic')['ratio'].mean()
             .sort_values(ascending=True).reset_index())
topic_avg.columns = ['Topic', 'Ratio']
topic_avg['Short'] = topic_avg['Topic'].str.replace(' Indicators', '').str[:30]
topic_avg['clr'] = topic_avg['Ratio'].apply(
    lambda x: '#ef4444' if x > 1.15 else ('#f59e0b' if x > 1.0 else '#10b981'))

fig = go.Figure(go.Bar(
    x=topic_avg['Ratio'], y=topic_avg['Short'], orientation='h',
    marker=dict(color=topic_avg['clr'], cornerradius=5),
    text=topic_avg['Ratio'].apply(lambda x: f'{x:.2f}x'),
    textposition='outside', textfont=dict(size=11)
))
fig.add_vline(x=1.0, line_dash="dot", line_color="gray", line_width=2,
              annotation_text="State Avg", annotation_font_size=10)
fig.update_layout(
    height=max(300, len(topic_avg) * 32),
    margin=dict(l=0, r=50, t=10, b=0),
    xaxis=dict(showgrid=False, title='County / State Ratio'),
    yaxis=dict(showgrid=False),
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter')
)
st.plotly_chart(fig, use_container_width=True)

# ── Top / Bottom Indicators ─────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.subheader("⚠️ Highest Burden Indicators")
    worst = df_comp.nlargest(8, 'ratio')
    for _, r in worst.iterrows():
        icon = "🔴" if r['ratio'] > 1.5 else "🟡"
        st.markdown(f"{icon} **{r['ratio']:.2f}x** — {r['indicator'][:55]}")

with c2:
    st.subheader("✅ Best Performing")
    best = df_comp.nsmallest(8, 'ratio')
    for _, r in best.iterrows():
        st.markdown(f"🟢 **{r['ratio']:.2f}x** — {r['indicator'][:55]}")

# ── Full Table ───────────────────────────────────────────────────────────────
with st.expander("📋 All Indicators"):
    st.dataframe(df_comp.sort_values('ratio', ascending=False).reset_index(drop=True),
                 use_container_width=True)
