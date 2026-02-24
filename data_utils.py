"""
Shared data loading and utilities for the NYS Health Dashboard.
"""
import os, warnings, numpy as np, pandas as pd
import streamlit as st

warnings.filterwarnings('ignore')

# ── NYS County Coordinates ──────────────────────────────────────────────────
COORDS = {
    'Albany': (42.65,-73.76), 'Allegany': (42.26,-78.03), 'Broome': (42.16,-75.82),
    'Cattaraugus': (42.25,-78.68), 'Cayuga': (42.93,-76.57), 'Chautauqua': (42.30,-79.41),
    'Chemung': (42.14,-76.76), 'Chenango': (42.49,-75.61), 'Clinton': (44.75,-73.68),
    'Columbia': (42.25,-73.63), 'Cortland': (42.60,-76.18), 'Delaware': (42.20,-74.97),
    'Dutchess': (41.77,-73.74), 'Erie': (42.75,-78.78), 'Essex': (44.12,-73.78),
    'Franklin': (44.59,-74.30), 'Fulton': (43.11,-74.42), 'Genesee': (43.00,-78.19),
    'Greene': (42.28,-74.13), 'Hamilton': (43.66,-74.50), 'Herkimer': (43.42,-74.96),
    'Jefferson': (44.00,-75.86), 'Lewis': (43.78,-75.45), 'Livingston': (42.73,-77.79),
    'Madison': (42.91,-75.67), 'Monroe': (43.16,-77.61), 'Montgomery': (42.91,-74.44),
    'Nassau': (40.74,-73.59), 'Niagara': (43.17,-78.83), 'Oneida': (43.24,-75.44),
    'Onondaga': (43.05,-76.15), 'Ontario': (42.85,-77.30), 'Orange': (41.40,-74.27),
    'Orleans': (43.34,-78.22), 'Oswego': (43.46,-76.21), 'Otsego': (42.63,-75.03),
    'Putnam': (41.43,-73.76), 'Rensselaer': (42.71,-73.51), 'Rockland': (41.15,-74.02),
    'Saratoga': (43.10,-73.86), 'Schenectady': (42.81,-74.06), 'Schoharie': (42.59,-74.45),
    'Schuyler': (42.39,-76.88), 'Seneca': (42.78,-76.82), 'St. Lawrence': (44.49,-75.11),
    'Steuben': (42.27,-77.39), 'Suffolk': (40.94,-72.68), 'Sullivan': (41.72,-74.77),
    'Tioga': (42.17,-76.31), 'Tompkins': (42.45,-76.47), 'Ulster': (41.89,-74.26),
    'Warren': (43.56,-73.84), 'Washington': (43.31,-73.43), 'Wayne': (43.07,-77.06),
    'Westchester': (41.12,-73.79), 'Wyoming': (42.70,-78.23), 'Yates': (42.63,-77.11),
    'Bronx': (40.84,-73.86), 'Kings': (40.63,-73.95), 'New York': (40.78,-73.97),
    'Queens': (40.72,-73.79), 'Richmond': (40.58,-74.15),
}

CLUSTER_COLORS = ['#14b8a6', '#3b82f6', '#f43f5e', '#f59e0b', '#8b5cf6']


@st.cache_data
def load_data():
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "nys_health_output", "chirs_data_cache.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache)
    else:
        import requests
        records = []
        for offset in range(0, 30000, 5000):
            r = requests.get(f"https://health.data.ny.gov/resource/54ci-sdfi.json?$limit=5000&$offset={offset}")
            if r.status_code != 200 or not r.json(): break
            records.extend(r.json())
        df = pd.DataFrame(records)
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        df.to_csv(cache, index=False)

    for c in ['event_count', 'average_number_of_denominator', 'percent_rate']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    df['lat'] = df['county_name'].map(lambda x: COORDS.get(x, (np.nan, np.nan))[0])
    df['lon'] = df['county_name'].map(lambda x: COORDS.get(x, (np.nan, np.nan))[1])
    return df


@st.cache_data
def get_counties(df):
    exclude = ['New York State', 'New York State (excluding NYC)', 'New York City',
               'Capital Region', 'Central NY', 'Finger Lakes', 'Long Island',
               'Mid-Hudson', 'Mohawk Valley', 'North Country', 'Southern Tier',
               'Tug Hill Seaway', 'Western NY']
    out = df[~df['county_name'].isin(exclude)].copy()
    return out[~out['county_name'].str.contains('/', na=False)].copy()


@st.cache_data
def get_state_avgs(df):
    s = df[df['county_name'] == 'New York State']
    return dict(zip(s['indicator'], s['percent_rate']))


@st.cache_data
def compute_burden(dfc, savgs):
    rows = []
    for _, r in dfc.iterrows():
        sa = savgs.get(r.get('indicator'))
        cr = r.get('percent_rate')
        if pd.notna(cr) and pd.notna(sa) and sa != 0:
            rows.append({'county': r['county_name'], 'ratio': cr / sa})
    return pd.DataFrame(rows).groupby('county')['ratio'].mean().sort_values(ascending=False)


def inject_theme_css():
    """Inject CSS that adapts to both light and dark Streamlit themes."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .block-container { padding-top: 1rem; max-width: 1200px; }

    /* Hero — always has its own dark background, white text */
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0d9488 100%);
        border-radius: 14px;
        padding: 2rem 2.2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(13,148,136,0.3) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero h1 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        position: relative;
    }
    .hero p {
        color: #cbd5e1;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        margin: 0;
        position: relative;
    }
    .hero .accent { color: #5eead4; font-weight: 600; }

    /* Stat Cards — use semi-transparent bg that works on any theme */
    .stat-row { display: flex; gap: 0.8rem; margin-bottom: 1.5rem; }
    .stat-card {
        flex: 1;
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-card .number {
        font-family: 'Inter', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .stat-card .label {
        font-size: 0.75rem;
        opacity: 0.6;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }
    .stat-card.c1 .number { color: #14b8a6; }
    .stat-card.c2 .number { color: #3b82f6; }
    .stat-card.c3 .number { color: #f59e0b; }
    .stat-card.c4 .number { color: #f43f5e; }

    /* Section divider */
    .sdiv {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.45;
        margin: 1.5rem 0 0.6rem 0;
    }

    /* Footer */
    .foot {
        text-align: center;
        padding: 1.2rem 0;
        opacity: 0.4;
        font-size: 0.78rem;
        margin-top: 2rem;
        border-top: 1px solid rgba(128,128,128,0.2);
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
