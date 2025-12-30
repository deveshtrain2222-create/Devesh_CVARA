import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Crypto Risk Analytics Dashboard",
    layout="wide"
)
import logging
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)

# ==========================================================
# THEME
# ==========================================================
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background: radial-gradient(circle at top, #0f1b3d 0%, #0b1220 45%, #050914 100%);
    color: #e5e7eb;
}
.block-container { padding: 2rem; }
div[data-testid="column"] > div {
    background: rgba(255,255,255,0.04);
    border-radius: 18px;
    padding: 22px;
}
.card {
    background: linear-gradient(145deg, rgba(56,189,248,0.18), rgba(14,165,233,0.06));
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 0 20px rgba(56,189,248,0.15);
}
h1, h2, h3 { color: #60a5fa; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# LOAD DATA (SAFE)
# ==========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("crypto_processed.csv")

    df["Date"] = pd.to_datetime(df["Date"])

    required_cols = ["Crypto", "Date", "Close", "Returns", "Volatility", "Sharpe_Ratio"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    return df.dropna()

data = load_data()

# ==========================================================
# TITLE
# ==========================================================
st.markdown("## 🔷 Milestone 3: Visualization Dashboard")

# ==========================================================
# LAYOUT
# ==========================================================
left, right = st.columns([1.1, 2.4])

# ==========================================================
# LEFT PANEL
# ==========================================================
with left:
    st.markdown("### 📋 Requirements")
    st.markdown("""
    • Interactive Plotly visualizations  
    • Price & volatility time-series  
    • Risk–return analysis  
    • Multi-asset comparison  
    """)

    st.markdown("### 🔄 Controls")

    selected_crypto = st.multiselect(
        "Assets",
        options=sorted(data["Crypto"].unique()),
        default=[data["Crypto"].unique()[0]]
    )

    start_date = st.date_input("Start Date", data["Date"].min())
    end_date = st.date_input("End Date", data["Date"].max())

    if start_date > end_date:
        st.warning("Start date must be before end date")

    st.caption(f"Last Updated: {pd.Timestamp.now()}")

# ==========================================================
# FILTER DATA (SAFE)
# ==========================================================
filtered = data[
    (data["Crypto"].isin(selected_crypto)) &
    (data["Date"] >= pd.to_datetime(start_date)) &
    (data["Date"] <= pd.to_datetime(end_date))
]

if filtered.empty:
    st.warning("No data available for selected filters")
    st.stop()

# ==========================================================
# RIGHT PANEL
# ==========================================================
with right:

    # ------------------------------------------------------
    # PRICE & VOLATILITY
    # ------------------------------------------------------
    st.markdown("### 📈 Price & Volatility Trends")

    fig = go.Figure()

    for coin in filtered["Crypto"].unique():
        dfc = filtered[filtered["Crypto"] == coin]

        fig.add_trace(go.Scatter(
            x=dfc["Date"],
            y=dfc["Close"],
            name=f"{coin} Price",
            mode="lines"
        ))

        fig.add_trace(go.Scatter(
            x=dfc["Date"],
            y=dfc["Volatility"],
            name=f"{coin} Volatility",
            mode="lines",
            yaxis="y2",
            line=dict(dash="dot")
        ))

    fig.update_layout(
        template="plotly_dark",
        height=420,
        yaxis=dict(title="Price"),
        yaxis2=dict(title="Volatility", overlaying="y", side="right"),
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------
    # RISK–RETURN SCATTER
    # ------------------------------------------------------
    st.markdown("### 🎯 Risk–Return Analysis")

    rr = filtered.groupby("Crypto").mean(numeric_only=True).reset_index()

    scatter = px.scatter(
        rr,
        x="Volatility",
        y="Returns",
        color="Crypto",
        size=[20]*len(rr),
        template="plotly_dark"
    )

    scatter.update_traces(
        marker=dict(size=22, opacity=0.9, line=dict(width=1.5, color="white"))
    )

    st.plotly_chart(scatter, use_container_width=True)

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------
    avg_vol = filtered["Volatility"].mean()
    avg_ret = filtered["Returns"].mean()
    avg_sharpe = filtered["Sharpe_Ratio"].mean()

    risk_level = "Low" if avg_vol < 0.3 else "Medium" if avg_vol < 0.6 else "High"

    k1, k2, k3, k4 = st.columns(4)

    k1.markdown(f"<div class='card'><h2>{avg_vol:.2%}</h2><p>Volatility</p></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='card'><h2>{avg_sharpe:.2f}</h2><p>Sharpe Ratio</p></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='card'><h2>{avg_ret:.2%}</h2><p>Avg Return</p></div>", unsafe_allow_html=True)
    k4.markdown(f"<div class='card'><h2>{risk_level}</h2><p>Risk Level</p></div>", unsafe_allow_html=True)
