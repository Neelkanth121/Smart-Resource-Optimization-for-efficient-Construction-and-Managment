import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# ─────────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ConstructIQ — Smart Construction Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API = "http://127.0.0.1:8000"

# ─────────────────────────────────────────────
#  Global CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global resets ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #1f2937;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    padding: 0.4rem 0;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800;
    font-size: 1.3rem;
    color: #f8fafc !important;
    border-bottom: 1px solid #374151;
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
}

/* ── Page headings ── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem !important;
    font-weight: 700;
    color: #0f172a;
}

/* ── Section subheaders ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #94a3b8;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}

/* ── Risk result banner ── */
.risk-banner {
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    animation: fadeSlideUp 0.4s ease;
}
.risk-banner.low   { background: #f0fdf4; border: 2px solid #4ade80; }
.risk-banner.medium{ background: #fffbeb; border: 2px solid #fbbf24; }
.risk-banner.high  { background: #fef2f2; border: 2px solid #f87171; }

.risk-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.risk-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
}
.risk-banner.low   .risk-value { color: #16a34a; }
.risk-banner.medium .risk-value { color: #d97706; }
.risk-banner.high  .risk-value  { color: #dc2626; }

.risk-icon {
    font-size: 3rem;
    line-height: 1;
}

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Cost result banner ── */
.cost-banner {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
    animation: fadeSlideUp 0.4s ease;
}
.cost-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #0f172a;
}
.cost-sub {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 0.25rem;
}

/* ── Hero area ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 1rem;
    color: #64748b;
    max-width: 580px;
    line-height: 1.6;
}

/* ── Pill badges ── */
.pill {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.pill-green  { background:#dcfce7; color:#15803d; }
.pill-amber  { background:#fef3c7; color:#b45309; }
.pill-red    { background:#fee2e2; color:#b91c1c; }
.pill-gray   { background:#f1f5f9; color:#475569; }

/* ── Stale warning ── */
.stale-notice {
    font-size: 0.82rem;
    color: #92400e;
    background: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    margin-top: 0.75rem;
    display: inline-block;
}

/* ── Expander tweak ── */
details summary {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #0f172a !important;
    color: #f8fafc !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1e293b !important;
}
.stButton > button:not([kind="primary"]) {
    border-radius: 10px !important;
}

/* ── Stat table ── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

/* ── Sidebar logo area ── */
.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.sidebar-tagline {
    font-size: 0.72rem;
    color: #64748b;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  API helpers
# ─────────────────────────────────────────────
@st.cache_data
def fetch_image():
    response = requests.get(f"{API}/image")
    return Image.open(BytesIO(response.content))

@st.cache_data
def fetch_shape():
    return requests.get(f"{API}/shape").json()

@st.cache_data(ttl=60)
def fetch_filtered(target_str):
    return requests.get(f"{API}/filter", params={"targets": target_str}).json()

@st.cache_data
def fetched_statistics():
    return requests.get(f"{API}/statistics").json()

def predict_risk(data):
    response = requests.post(f"{API}/predict", json=data, timeout=10)
    return response.json()

def predict_cost(data):
    response = requests.post(f"{API}/predict_cost", json=data, timeout=10)
    return response.json()


# ─────────────────────────────────────────────
#  Sidebar Navigation
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">ConstructIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Smart Construction Intelligence</div>', unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "Navigation",
        ["Home", "Dataset & Statistics", "Risk Prediction", "Cost Estimation"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown(
        '<p style="font-size:0.7rem;color:#475569;line-height:1.6;">'
        "Powered by XGBoost & LightGBM<br>FastAPI backend · v1.0"
        "</p>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════
if page == "Home":
    col_txt, col_img = st.columns([1, 1], gap="large")

    with col_txt:
        st.markdown(
            '<div class="hero-title">Smart Resource Optimization for Construction</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="hero-sub">Machine learning models trained on real project data to help '
            'you predict risk levels and estimate costs — before breaking ground.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Projects in Dataset", "10 K+", help="Total records used for training")
        c2.metric("Risk Model", "XGBoost", help="Gradient-boosted classifier")
        c3.metric("Cost Model", "LightGBM", help="Pipeline-based regressor")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("About this platform"):
            st.markdown(
                "This platform applies machine learning to predict two critical outputs for "
                "large-scale construction projects:\n\n"
                "- **Risk Level** — Low / Medium / High, based on structural sensors, "
                "environmental conditions, resource usage, and site anomalies.\n"
                "- **Estimated Cost** — Predicted actual spend versus the planned budget, "
                "surfacing potential overruns early.\n\n"
                "Both models are trained on 12 months of historical project data across "
                "Bridge, Tunnel, Dam, Building, and Road project types."
            )
            st.success("Model is trained on 12 months of real shipment and site data.")
            st.warning("Predictions are estimates based on historical patterns.")

    with col_img:
        with st.spinner("Loading overview image..."):
            try:
                img = fetch_image()
                st.image(img, caption="Project overview", use_container_width=True)
            except Exception:
                st.info("Backend not reachable — start the FastAPI server to load the image.")


# ═══════════════════════════════════════════════
#  DATASET & STATISTICS
# ═══════════════════════════════════════════════
elif page == "Dataset & Statistics":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Dataset Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Filter the training dataset by risk category and inspect descriptive statistics.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Fetching dataset shape..."):
        try:
            shape = fetch_shape()
            c1, c2 = st.columns(2)
            c1.metric("Total Rows", f"{shape['rows']:,}")
            c2.metric("Total Columns", shape["cols"])
        except Exception:
            st.error("Cannot connect to backend. Ensure FastAPI is running.")
            st.stop()

    st.markdown('<div class="section-header">Filter by Risk Level</div>', unsafe_allow_html=True)

    RISK_MAPPING = {"Low Risk": 0, "Moderate Risk": 1, "High Risk": 2}
    selected_labels = st.multiselect(
        "Select risk categories to display",
        list(RISK_MAPPING.keys()),
        placeholder="Choose one or more risk levels…",
    )

    if st.button("Apply Filter", type="primary"):
        if not selected_labels:
            st.warning("Select at least one risk level before filtering.")
        else:
            target_nums = [RISK_MAPPING[x] for x in selected_labels]
            targets_str = ",".join(str(n) for n in target_nums)
            with st.spinner("Filtering…"):
                result = fetch_filtered(targets_str)
            filtered_df = pd.DataFrame(result["data"])
            st.caption(
                f"Showing **{result['filtered_count']:,}** of **{result['total_count']:,}** rows"
            )
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">Descriptive Statistics</div>', unsafe_allow_html=True)
    with st.spinner("Loading statistics..."):
        stats_dict = fetched_statistics()
    stats_df = pd.DataFrame(stats_dict).set_index("index")
    stats_df.index.name = None
    st.dataframe(stats_df, use_container_width=True)


# ═══════════════════════════════════════════════
#  RISK PREDICTION
# ═══════════════════════════════════════════════
elif page == "Risk Prediction":
    st.markdown('<div class="hero-title" style="font-size:2rem;">Risk Prediction</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Fill in all site parameters below. The XGBoost model will classify the project risk as Low, Medium, or High.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Feature importance guide — what drives risk most?"):
        importance_data = {
            "Rank": list(range(1, 11)),
            "Feature": [
                "Anomaly Detected", "Image Analysis Score", "Accident Count",
                "Equipment Utilization", "Completion Percentage", "Labor Hours",
                "Load Bearing Capacity", "Material Usage", "Air Quality Index", "Vibration Level",
            ],
            "What it means": [
                "Unusual sensor readings or equipment malfunction flagged on site — strongest predictor",
                "AI-based structural image score — higher score indicates more damage",
                "Number of accidents reported during the project",
                "How heavily equipment is used relative to capacity",
                "How far along the project is — risk profile shifts with progress",
                "Total labor hours logged — proxy for project stress",
                "Structural capacity of load-bearing elements",
                "Amount of material consumed — reflects project scale and strain",
                "Air pollution index — affects worker safety and site conditions",
                "Measured vibration on site — indicates structural stress",
            ],
            "Impact": ["Very High", "Very High", "High", "High", "High",
                       "Medium", "Medium", "Medium", "Medium", "Low"],
        }
        impact_colors = {
            "Very High": "pill-red", "High": "pill-amber",
            "Medium": "pill-gray", "Low": "pill-green",
        }
        df_imp = pd.DataFrame(importance_data)
        st.dataframe(df_imp, use_container_width=True, hide_index=True)

    # ── Section 1: Project Info ──────────────────
    st.markdown('<div class="section-header">01 — Project information</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        project_type = st.selectbox("Project Type *", ["", "Bridge", "Tunnel", "Dam", "Building", "Road"])
    with c2:
        planned_cost = st.number_input("Planned Cost ($) *", min_value=1_045_475, max_value=49_968_538, value=None, placeholder="1,045,475 – 49,968,538")
    with c3:
        planned_duration = st.number_input("Planned Duration (days) *", min_value=180, max_value=899, value=None, placeholder="180 – 899")

    # ── Section 2: Structural Sensors ─────────────
    st.markdown('<div class="section-header">02 — Structural sensors</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        vibration_level = st.number_input("Vibration Level *", min_value=0.0, max_value=100.0, value=None, placeholder="0.0 – 100.0")
    with c2:
        crack_width = st.number_input("Crack Width (mm) *", min_value=0.0, max_value=10.0, value=None, placeholder="0.0 – 10.0")
    with c3:
        load_bearing = st.number_input("Load Bearing Capacity *", min_value=50.0, max_value=499.0, value=None, placeholder="50.0 – 499.0")

    # ── Section 3: Environmental ─────────────────
    st.markdown('<div class="section-header">03 — Environmental conditions</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        temperature = st.number_input("Temperature (°C) *", min_value=-10.0, max_value=45.0, value=None, placeholder="-10.0 – 45.0")
    with c2:
        humidity = st.number_input("Humidity (%) *", min_value=20.0, max_value=90.0, value=None, placeholder="20.0 – 90.0")
    with c3:
        weather = st.selectbox("Weather Condition *", ["", "Sunny", "Cloudy", "Rainy", "Stormy", "Snowy"])
    with c4:
        air_quality = st.number_input("Air Quality Index *", min_value=50, max_value=299, value=None, placeholder="50 – 299")

    # ── Section 4: Resources ─────────────────────
    st.markdown('<div class="section-header">04 — Resource usage</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        energy = st.number_input("Energy Consumption (kWh) *", min_value=5054.0, max_value=49942.0, value=None, placeholder="5,054 – 49,942")
    with c2:
        material = st.number_input("Material Usage (tons) *", min_value=101.0, max_value=999.0, value=None, placeholder="101 – 999")
    with c3:
        labor = st.number_input("Labor Hours *", min_value=1001, max_value=9997, value=None, placeholder="1,001 – 9,997")
    with c4:
        equipment = st.number_input("Equipment Utilization (%) *", min_value=0.0, max_value=100.0, value=None, placeholder="0 – 100")

    # ── Section 5: Risk Indicators ───────────────
    st.markdown('<div class="section-header">05 — Risk indicators</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        accident_count = st.number_input("Accident Count *", min_value=0, max_value=9, value=None, placeholder="0 – 9")
    with c2:
        anomaly_detected = st.selectbox(
            "Anomaly Detected *", ["", 0, 1],
            format_func=lambda x: "Select…" if x == "" else ("Yes — anomaly present" if x == 1 else "No anomaly"),
        )
    with c3:
        image_score = st.number_input("Image Analysis Score (%) *", min_value=0.0, max_value=100.0, value=None, placeholder="0 – 100")

    # ── Section 6: Progress ──────────────────────
    st.markdown('<div class="section-header">06 — Project progress</div>', unsafe_allow_html=True)
    completion = st.slider("Completion Percentage (%)", min_value=0, max_value=100, value=50)
    st.caption(f"Current progress: **{completion}%**")

    st.divider()

    fields = {
        "Project Type": project_type, "Planned Cost": planned_cost,
        "Planned Duration": planned_duration, "Vibration Level": vibration_level,
        "Crack Width": crack_width, "Load Bearing Capacity": load_bearing,
        "Temperature": temperature, "Humidity": humidity,
        "Weather Condition": weather, "Air Quality Index": air_quality,
        "Energy Consumption": energy, "Material Usage": material,
        "Labor Hours": labor, "Equipment Utilization": equipment,
        "Accident Count": accident_count, "Anomaly Detected": anomaly_detected,
        "Image Analysis Score": image_score,
    }

    btn_col, _ = st.columns([1, 3])
    with btn_col:
        clicked = st.button("Run Risk Analysis", type="primary", use_container_width=True)

    if clicked:
        empty_fields = [name for name, val in fields.items() if val == "" or val is None]
        if empty_fields:
            st.warning("Please fill in all fields before predicting.")
            for f in empty_fields:
                st.markdown(f"  — {f}")
        else:
            payload = {
                "Project_Type":          project_type,
                "Planned_Cost":          planned_cost,
                "Planned_Duration":      planned_duration,
                "Vibration_Level":       vibration_level,
                "Crack_Width":           crack_width,
                "Load_Bearing_Capacity": load_bearing,
                "Temperature":           temperature,
                "Humidity":              humidity,
                "Weather_Condition":     weather,
                "Air_Quality_Index":     air_quality,
                "Energy_Consumption":    energy,
                "Material_Usage":        material,
                "Labor_Hours":           labor,
                "Equipment_Utilization": equipment,
                "Accident_Count":        accident_count,
                "Anomaly_Detected":      int(anomaly_detected),
                "Image_Analysis_Score":  image_score,
                "Completion_Percentage": completion,
            }

            try:
                with st.spinner("Running inference…"):
                    result = predict_risk(payload)

                if "risk_level" in result:
                    risk = result["risk_level"]
                    icon_map    = {"Low": "✅", "Medium": "⚠️", "High": "🚨"}
                    css_map     = {"Low": "low",  "Medium": "medium", "High": "high"}
                    advice_map  = {
                        "Low":    "Project appears well-controlled. Maintain current monitoring cadence.",
                        "Medium": "Elevated risk detected. Review anomaly logs and resource allocation.",
                        "High":   "Critical risk. Immediate site inspection and management review recommended.",
                    }
                    st.markdown(
                        f"""
                        <div class="risk-banner {css_map[risk]}">
                            <div class="risk-icon">{icon_map[risk]}</div>
                            <div>
                                <div class="risk-label">Predicted Risk Level</div>
                                <div class="risk-value">{risk} Risk</div>
                                <div style="font-size:0.88rem;color:#475569;margin-top:0.5rem;">{advice_map[risk]}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # summary strip
                    st.markdown("<br>", unsafe_allow_html=True)
                    sc1, sc2, sc3, sc4 = st.columns(4)
                    sc1.metric("Project Type",     project_type)
                    sc2.metric("Completion",       f"{completion}%")
                    sc3.metric("Anomaly",          "Yes" if anomaly_detected == 1 else "No")
                    sc4.metric("Accidents",        int(accident_count))
                else:
                    st.error(f"Backend error: {result}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend — ensure FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ═══════════════════════════════════════════════
#  COST ESTIMATION
# ═══════════════════════════════════════════════
elif page == "Cost Estimation":
    if "prediction" not in st.session_state:
        st.session_state.prediction = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "stale" not in st.session_state:
        st.session_state.stale = False

    def mark_stale():
        st.session_state.stale = True

    st.markdown('<div class="hero-title" style="font-size:2rem;">Cost Estimator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Predict the actual project cost using the LightGBM pipeline — and see how it compares to your planned budget.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 1: Project Profile ────────────────
    st.markdown('<div class="section-header">01 — Project profile</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        project_type = st.selectbox(
            "Project Type", ["Tunnel", "Dam", "Building", "Road", "Bridge"],
            index=None, placeholder="Select project type", on_change=mark_stale,
        )
    with col2:
        planned_cost = st.number_input(
            "Planned Cost (USD)", min_value=1_045_475, max_value=49_968_538,
            value=None, step=10_000, placeholder="1,045,475 – 49,968,538", on_change=mark_stale,
        )
    with col3:
        planned_duration = st.number_input(
            "Planned Duration (days)", min_value=180, max_value=899,
            value=None, step=1, placeholder="180 – 899 days", on_change=mark_stale,
        )

    # ── Section 2: Site Conditions ───────────────
    st.markdown('<div class="section-header">02 — Site conditions</div>', unsafe_allow_html=True)
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        load_bearing = st.number_input(
            "Load Bearing Capacity (kN/m²)", min_value=50.0, max_value=499.0,
            value=None, step=1.0, placeholder="50.0 – 499.0", on_change=mark_stale,
        )
    with col5:
        temperature = st.number_input(
            "Temperature (°C)", min_value=-10.0, max_value=45.0,
            value=None, step=0.5, placeholder="-10.0 – 45.0", on_change=mark_stale,
        )
    with col6:
        humidity = st.number_input(
            "Humidity (%)", min_value=20.0, max_value=90.0,
            value=None, step=1.0, placeholder="20.0 – 90.0", on_change=mark_stale,
        )
    with col7:
        weather_condition = st.selectbox(
            "Weather Condition", ["Sunny", "Cloudy", "Rainy", "Stormy", "Snowy"],
            index=None, placeholder="Select condition", on_change=mark_stale,
        )

    # ── Section 3: Environmental & Operational ────
    st.markdown('<div class="section-header">03 — Environmental & operational</div>', unsafe_allow_html=True)
    col8, col9, col10, col11, col12 = st.columns(5)
    with col8:
        aqi = st.number_input(
            "Air Quality Index", min_value=50, max_value=299,
            value=None, step=1, placeholder="50 – 299", on_change=mark_stale,
        )
    with col9:
        energy_consumption = st.number_input(
            "Energy (kWh)", min_value=5054.0, max_value=49942.0,
            value=None, step=100.0, placeholder="5,054 – 49,942", on_change=mark_stale,
        )
    with col10:
        material_usage = st.number_input(
            "Material Usage (tons)", min_value=101.0, max_value=999.0,
            value=None, step=1.0, placeholder="101 – 999", on_change=mark_stale,
        )
    with col11:
        labor_hours = st.number_input(
            "Labor Hours", min_value=1001, max_value=9997,
            value=None, step=50, placeholder="1,001 – 9,997", on_change=mark_stale,
        )
    with col12:
        accident_count = st.number_input(
            "Accident Count", min_value=0, max_value=9,
            value=None, step=1, placeholder="0 – 9", on_change=mark_stale,
        )

    st.divider()

    btn_col, _ = st.columns([1, 3])
    with btn_col:
        predict_clicked = st.button("Generate Estimate", type="primary", use_container_width=True)

    if predict_clicked:
        missing_nums = any(v is None for v in [
            planned_cost, planned_duration, load_bearing, temperature,
            humidity, aqi, energy_consumption, material_usage, labor_hours, accident_count,
        ])
        missing_cats = any(v is None for v in [project_type, weather_condition])

        if missing_nums or missing_cats:
            st.warning("Please fill in all fields before generating an estimate.")
        else:
            payload = {
                "Project_Type":          project_type,
                "Planned_Cost":          planned_cost,
                "Planned_Duration":      planned_duration,
                "Load_Bearing_Capacity": load_bearing,
                "Temperature":           temperature,
                "Humidity":              humidity,
                "Weather_Condition":     weather_condition,
                "Air_Quality_Index":     aqi,
                "Energy_Consumption":    energy_consumption,
                "Material_Usage":        material_usage,
                "Labor_Hours":           labor_hours,
                "Accident_Count":        accident_count,
            }
            try:
                with st.spinner("Running model inference…"):
                    data = predict_cost(payload)
                st.session_state.prediction = data.get("estimated_cost", data)
                st.session_state.error = None
                st.session_state.stale = False
            except requests.exceptions.ConnectionError:
                st.session_state.error = "Cannot connect to backend — ensure FastAPI server is running on port 8000."
                st.session_state.prediction = None
            except requests.exceptions.HTTPError as e:
                st.session_state.error = f"Server returned an error: {e.response.status_code}"
                st.session_state.prediction = None
            except Exception as e:
                st.session_state.error = f"Unexpected error: {str(e)}"
                st.session_state.prediction = None

    # ── Result ───────────────────────────────────
    if st.session_state.prediction is not None:
        cost = st.session_state.prediction
        formatted = f"${cost:,.0f}" if isinstance(cost, (int, float)) else str(cost)

        if st.session_state.stale:
            st.markdown(
                '<div class="stale-notice">⚠ Input values have changed — click Generate Estimate to refresh.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Estimation result</div>', unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("Predicted Cost (USD)", formatted)

        if isinstance(cost, (int, float)) and planned_cost:
            deviation = cost - planned_cost
            pct = (deviation / planned_cost) * 100
            m2.metric(
                "Cost Deviation",
                f"${deviation:+,.0f}",
                delta=f"{pct:+.1f}% vs planned",
                delta_color="inverse",
            )
            m3.metric("Planned Cost (USD)", f"${planned_cost:,.0f}")

        st.markdown(
            f'<div class="cost-sub">Project: <strong>{project_type}</strong>  ·  '
            f'Duration: <strong>{planned_duration} days</strong>  ·  '
            f'Weather: <strong>{weather_condition}</strong></div>',
            unsafe_allow_html=True,
        )

    elif st.session_state.error:
        st.error(st.session_state.error)