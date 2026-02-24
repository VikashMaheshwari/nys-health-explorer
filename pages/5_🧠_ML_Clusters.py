"""
Page 5 — ML Health Clusters
"""
import streamlit as st
import numpy as np, pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from data_utils import load_data, get_counties, inject_theme_css, COORDS, CLUSTER_COLORS

st.set_page_config(page_title="ML Clusters", page_icon="🧠", layout="wide")
inject_theme_css()

df_all = load_data()
df_c   = get_counties(df_all)


@st.cache_data
def run_clustering(k):
    pivot = df_c.pivot_table(index='county_name', columns='indicator',
                             values='percent_rate', aggfunc='mean')
    pivot = pivot.dropna(axis=1, thresh=int(len(pivot) * 0.6))
    pivot = pivot.dropna(axis=0, thresh=int(len(pivot.columns) * 0.6))
    pivot = pivot.fillna(pivot.median())

    X = StandardScaler().fit_transform(pivot.values)
    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)

    result = pd.DataFrame({
        'county': pivot.index,
        'pc1': X2[:, 0], 'pc2': X2[:, 1],
        'cluster': [f'Cluster {l + 1}' for l in labels]
    })
    result['lat'] = result['county'].map(lambda x: COORDS.get(x, (np.nan, np.nan))[0])
    result['lon'] = result['county'].map(lambda x: COORDS.get(x, (np.nan, np.nan))[1])

    # Cluster profiles
    profile_data = pivot.copy()
    profile_data['_cluster'] = labels
    profiles = {}
    overall_mean = pivot.mean()
    overall_std = pivot.std()
    for c_idx in range(k):
        members = pivot.index[labels == c_idx].tolist()
        cluster_mean = pivot.loc[members].mean()
        z = (cluster_mean - overall_mean) / overall_std
        profiles[f'Cluster {c_idx + 1}'] = {
            'members': sorted(members),
            'concerns': z.nlargest(5).to_dict(),
            'strengths': z.nsmallest(5).to_dict(),
        }

    return result.dropna(subset=['lat', 'lon']), sil, pca.explained_variance_ratio_[:2], profiles


@st.cache_data
def silhouette_range():
    pivot = df_c.pivot_table(index='county_name', columns='indicator',
                             values='percent_rate', aggfunc='mean')
    pivot = pivot.dropna(axis=1, thresh=int(len(pivot) * 0.6))
    pivot = pivot.dropna(axis=0, thresh=int(len(pivot.columns) * 0.6))
    pivot = pivot.fillna(pivot.median())
    X = StandardScaler().fit_transform(pivot.values)
    scores = []
    for k in range(2, 8):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        lbl = km.fit_predict(X)
        scores.append({'K': k, 'Score': silhouette_score(X, lbl)})
    return pd.DataFrame(scores)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🧠 ML Health Clusters</h1>
    <p>K-Means clustering with PCA identifies distinct county health profiles across New York State</p>
</div>
""", unsafe_allow_html=True)

k = st.slider("Number of Clusters (K)", 2, 5, 2)
cdf, sil, var, profiles = run_clustering(k)

c1, c2 = st.columns(2)
c1.metric("Silhouette Score", f"{sil:.4f}")
c2.metric("PCA Variance (2D)", f"{sum(var):.1%}")

# ── Side by Side Maps ────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Geographic Distribution")
    fig = px.scatter_mapbox(
        cdf, lat='lat', lon='lon',
        color='cluster', hover_name='county',
        color_discrete_sequence=CLUSTER_COLORS[:k],
        zoom=5.5, mapbox_style="carto-positron",
        center={"lat": 42.85, "lon": -75.5},
    )
    fig.update_traces(marker=dict(size=13, opacity=0.9))
    fig.update_layout(
        height=440, margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation='h', y=-0.05, xanchor='center', x=0.5, font_size=11)
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("PCA Projection")
    fig = px.scatter(
        cdf, x='pc1', y='pc2',
        color='cluster', hover_name='county',
        color_discrete_sequence=CLUSTER_COLORS[:k],
        labels={'pc1': f'PC1 ({var[0]:.0%})', 'pc2': f'PC2 ({var[1]:.0%})'},
    )
    fig.update_traces(marker=dict(size=11, opacity=0.85, line=dict(width=1, color='white')))
    fig.update_layout(
        height=440, margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=-0.1, xanchor='center', x=0.5, font_size=11),
        font=dict(family='Inter')
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Cluster Profiles ─────────────────────────────────────────────────────────
st.subheader("Cluster Profiles")
for name, info in profiles.items():
    with st.expander(f"📌 {name} — {len(info['members'])} counties", expanded=(name == 'Cluster 1')):
        st.write(f"**Counties:** {', '.join(info['members'])}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**⚠️ Top Concerns:**")
            for ind, sc in info['concerns'].items():
                st.markdown(f"- ↑ **+{sc:.2f}σ** — {ind[:50]}")
        with c2:
            st.markdown("**✅ Strengths:**")
            for ind, sc in info['strengths'].items():
                st.markdown(f"- ↓ **{sc:.2f}σ** — {ind[:50]}")

# ── Silhouette Chart ─────────────────────────────────────────────────────────
st.subheader("Optimal K Analysis")
sil_df = silhouette_range()
fig = px.line(sil_df, x='K', y='Score', markers=True,
              color_discrete_sequence=['#14b8a6'])
fig.update_traces(marker=dict(size=10), line=dict(width=3))
fig.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(title='Number of Clusters (K)', dtick=1),
    yaxis=dict(title='Silhouette Score', showgrid=True, gridcolor='rgba(128,128,128,0.1)'),
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter')
)
st.plotly_chart(fig, use_container_width=True)
