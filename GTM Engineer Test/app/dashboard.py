import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db_connection

st.set_page_config(page_title="Catalyst Channel Tracker", layout="wide")
st.title("📊 Platform-Wide GTM Market Intelligence & ROI Tracker")


@st.cache_data(ttl=2)
def fetch_dashboard_data():
    with get_db_connection() as conn:
        # Isolate the latest telemetry snapshot for each tracked video asset
        analytics_df = pd.read_sql_query("""
            WITH latest_snapshots AS (
                SELECT DISTINCT ON (video_id) video_id, view_count
                FROM video_metrics_snapshots
                ORDER BY video_id, captured_at DESC
            )
            SELECT v.topic, v.format, AVG(s.view_count) as avg_views, MAX(s.view_count) as peak_views
            FROM videos v
            JOIN latest_snapshots s ON v.video_id = s.video_id
            GROUP BY v.topic, v.format 
            ORDER BY avg_views DESC;
        """, conn)

        # Sum the totals using only the latest snapshots to avoid data aggregation multipliers
        metrics_summary = pd.read_sql_query("""
            WITH latest_snapshots AS (
                SELECT DISTINCT ON (video_id) view_count 
                FROM video_metrics_snapshots 
                ORDER BY video_id, captured_at DESC
                    )
            SELECT SUM(view_count) as total_views FROM latest_snapshots;
        """, conn)

        # Pull the newest generated recommendation engine log entries
        recs_df = pd.read_sql_query("""
            SELECT topic, format, angle, reasoning 
            FROM recommendations 
            ORDER BY generated_at DESC 
            LIMIT 1;
        """, conn)

    return analytics_df, recs_df, metrics_summary['total_views'].iloc[0] or 0


analytics_data, recommendations_data, total_views = fetch_dashboard_data()

# UI Control Frame
st.sidebar.header("🎯 Live Tracking Mode")
st.sidebar.success("📡 System Status: Self-Sustaining Worker Active")
st.sidebar.info(
    "The background engine is automatically gathering channel snapshots over time and updating the operational storage layer.")

if st.sidebar.button("🔄 Force UI View Refresh", type="primary"):
    st.cache_data.clear()
    st.rerun()

tab1, tab2, tab3 = st.tabs(["💵 Client ROI View", "📈 Feed Analytics", "🧠 Gemini AI Recommendation"])

with tab1:
    st.header("Strategic Pipeline Generation")
    est_clicks = int(total_views * 0.01)
    est_signups = int(est_clicks * 0.05)
    est_pipeline = est_signups * 1200

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Client Asset Views", f"{total_views:,}")
    col2.metric("Est. Site Conversions (1% CTR)", f"{est_clicks:,}")
    col3.metric("Est. Trial Activations (5% Conv)", f"{est_signups:,}")
    col4.metric("Est. Direct Pipeline ($)", f"${est_pipeline:,}")
    st.success(f"🔥 Total Account Proxy Pipeline Unlocked: ${est_pipeline:,}")

with tab2:
    st.header("Content Performance Distribution")
    if not analytics_data.empty:
        analytics_data["Category Cluster"] = analytics_data["topic"] + " (" + analytics_data["format"] + ")"
        st.bar_chart(analytics_data.set_index("Category Cluster")[["avg_views"]])
        st.dataframe(analytics_data[["topic", "format", "avg_views", "peak_views"]], use_container_width=True)
    else:
        st.warning(
            "No structural asset metric models found in the database. Ensure your worker loop is processing correctly.")

with tab3:
    st.header("🧠 Active Strategy Framework (Gemini Intelligence Engine)")
    if not recommendations_data.empty:
        active_rec = recommendations_data.iloc[0]
        st.info(f"**Target Campaign Angle:**\n## {active_rec['angle']}")

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Recommended Content Domain", active_rec['topic'])
        col_m2.metric("Structural Delivery Blueprint", active_rec['format'])

        st.markdown("#### 📊 Machine Learning Reasoning Matrix")
        st.write(active_rec['reasoning'])
    else:
        st.info("Awaiting the first analytical optimization log from the automated worker thread.")