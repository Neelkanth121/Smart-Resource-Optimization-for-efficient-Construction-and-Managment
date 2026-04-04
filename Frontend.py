import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config("Smart Resource Optimization for efficient Construction and Managment",layout="wide")

API = "http://127.0.0.1:8000"

#----------------------- Side Bar Navigation --------------------------------
st.sidebar.title("Menu")
page = st.sidebar.radio("Go To",["Home","DataSet Preview and Statistics","Risk Prediction","Cost Estimation"])


#----------------------- API Call Functions ----------------------------------
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
    response = requests.post(f"{API}/predict", json=data)
    print(f"STATUS: {response.status_code}")
    print(f"BODY: {repr(response.text)}")
    return response.json()    

#--------------------------- Home --------------------------------------------
if page == "Home":
    st.title("Smart Resource Optimization for efficient Construction and Managment")
    st.header("Introduction")

    with st.spinner("Loading Image...."):
        img = fetch_image()
        st.image(img,caption="Overview",width="stretch")
    
    with st.expander("! About this web Page"):
        st.markdown("This project uses machine learning to predict key supply chain metrics such as demand fluctuations, delivery performance, and potential delays. By analyzing historical logistics data, the model uncovers patterns that help businesses optimize inventory, improve operational efficiency, and reduce costs. It enables proactive decision-making and enhances overall supply chain reliability.")
        st.success("Model is trained of 12 months of shipment data.")
        st.warning("Predictions are estimated based on Historical data")



#------------------------- DataSet Preview -----------------------------------
elif page == "DataSet Preview and Statistics":
    st.header("Dataset Preview")
    with st.spinner("Loading Dataset...."):
        shape = fetch_shape()
    st.write((shape['rows'], shape['cols']))

    RISK_MAPPING = {"Low Risk":0, "Moderate Risk":1, "High Risk":2}
    selected_labels = st.multiselect("Select Your Target Column: ", list(RISK_MAPPING.keys()))
    target_nums = [RISK_MAPPING[x] for x in selected_labels]

    if st.button("Submit"):
        if target_nums:
            targets_str = ",".join(str(n) for n in target_nums)

            with st.spinner("Filtering Data......"):
                result = fetch_filtered(targets_str)

            filtered_df = pd.DataFrame(result["data"])
            st.dataframe(filtered_df,width="stretch")
            st.caption(f"Showing {result["filtered_count"]} of {result["total_count"]} rows.")

        else:
            st.warning("Please Select atleast one Value for filtering.")

    st.header("Data Statistics")
    with st.spinner("Loading statistics..."):
        stats_dict = fetched_statistics()

    stats_df = pd.DataFrame(stats_dict).set_index('index')
    stats_df.index.name = None
    st.dataframe(stats_df, width="stretch")


#------------------------------------------- Risk Prediction ---------------------------------------------------
elif page == "Risk Prediction":
    st.title("Risk Prediction")
    with st.expander("Feature Importance Guide — What affects Risk the most?"):
        st.markdown("Features are ranked by their influence on the Risk prediction model (XGBoost Gain).")
        
        importance_data = {
            "Rank": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "Feature": [
                "Anomaly Detected",
                "Image Analysis Score",
                "Accident Count",
                "Equipment Utilization",
                "Completion Percentage",
                "Labor Hours",
                "Load Bearing Capacity",
                "Material Usage",
                "Air Quality Index",
                "Vibration Level",
            ],
            "What it means": [
                "Whether an anomaly(Unusual sensor readings,Structural behavior outside expected thresholds,Equipment malfunction signals) was flagged on site — strongest predictor",
                "AI-based structural image score — higher score = more damage",
                "Number of accidents reported during the project",
                "How heavily equipment is being used relative to capacity",
                "How far along the project is — risk profile changes with progress",
                "Total labor hours logged — proxy for project stress",
                "Structural capacity of load-bearing elements",
                "Amount of material consumed — reflects project scale and strain",
                "Air pollution index — affects worker safety and site conditions",
                "Measured vibration on site — indicates structural stress",
            ],
            "Impact": [
                "Very High",
                "Very High",
                "High",
                "High",
                "High",
                "Medium",
                "Medium",
                "Medium",
                "Medium",
                "Low",
            ]
        }

        st.dataframe(
            pd.DataFrame(importance_data),
            width='stretch',
            hide_index=True
        )
    # ── Group 1: Project Info ──────────────────────────────────────────
    st.subheader("Project Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        project_type = st.selectbox("Project Type *", ["", "Bridge", "Tunnel", "Dam", "Building", "Road"])
    with c2:
        planned_cost = st.number_input("Planned Cost ($) *", min_value=1_045_475, max_value=49_968_538, value=None, placeholder="1,045,475 – 49,968,538")
    with c3:
        planned_duration = st.number_input("Planned Duration (days) *", min_value=180, max_value=899, value=None, placeholder="180 – 899")

    # ── Group 2: Structural Sensors ────────────────────────────────────
    st.subheader("Structural Sensors")
    c1, c2, c3 = st.columns(3)
    with c1:
        vibration_level = st.number_input("Vibration Level *", min_value=0.0, max_value=100.0, value=None, placeholder="0.0 – 100.0")
    with c2:
        crack_width = st.number_input("Crack Width (mm) *", min_value=0.0, max_value=10.0, value=None, placeholder="0.0 – 10.0")
    with c3:
        load_bearing = st.number_input("Load Bearing Capacity *", min_value=50.0, max_value=499.0, value=None, placeholder="50.0 – 499.0")

    # ── Group 3: Environmental Conditions ─────────────────────────────
    st.subheader("Environmental Conditions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        temperature = st.number_input("Temperature (°C) *", min_value=-10.0, max_value=45.0, value=None, placeholder="-10.0 – 45.0")
    with c2:
        humidity = st.number_input("Humidity (%) *", min_value=20.0, max_value=90.0, value=None, placeholder="20.0 – 90.0")
    with c3:
        weather = st.selectbox("Weather Condition *", ["", "Sunny", "Cloudy", "Rainy", "Stormy", "Snowy"])
    with c4:
        air_quality = st.number_input("Air Quality Index *", min_value=50, max_value=299, value=None, placeholder="50 – 299")

    # ── Group 4: Resource Usage ────────────────────────────────────────
    st.subheader("Resource Usage")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        energy = st.number_input("Energy Consumption (kWh) *", min_value=5054.0, max_value=49942.0, value=None, placeholder="5,054 – 49,942")
    with c2:
        material = st.number_input("Material Usage (tons) *", min_value=101.0, max_value=999.0, value=None, placeholder="101 – 999")
    with c3:
        labor = st.number_input("Labor Hours *", min_value=1001, max_value=9997, value=None, placeholder="1,001 – 9,997")
    with c4:
        equipment = st.number_input("Equipment Utilization (%) *", min_value=0.0, max_value=100.0, value=None, placeholder="Enter utilization")

    # ── Group 5: Risk Indicators ───────────────────────────────────────
    st.subheader("Risk Indicators")
    c1, c2, c3 = st.columns(3)
    with c1:
        accident_count = st.number_input("Accident Count *", min_value=0, max_value=9, value=None, placeholder="0 – 9")
    with c2:
        anomaly_detected = st.selectbox("Anomaly Detected *", ["", 0, 1], format_func=lambda x: "Select" if x == "" else ("Yes" if x == 1 else "No"))
    with c3:
        image_score = st.number_input("Image Analysis Score (%) *", min_value=0.0, max_value=100.0, value=None, placeholder="Enter score")

    # ── Group 6: Project Progress ──────────────────────────────────────
    st.subheader("Project Progress")
    completion = st.number_input("Completion Percentage (%) *", min_value=0, max_value=100, value=None, placeholder="Enter completion %")
    # ── Validation ─────────────────────────────────────────────────────
    st.divider()

    fields = {
        "Project Type":             project_type,
        "Planned Cost":             planned_cost,
        "Planned Duration":         planned_duration,
        "Vibration Level":          vibration_level,
        "Crack Width":              crack_width,
        "Load Bearing Capacity":    load_bearing,
        "Temperature":              temperature,
        "Humidity":                 humidity,
        "Weather Condition":        weather,
        "Air Quality Index":        air_quality,
        "Energy Consumption":       energy,
        "Material Usage":           material,
        "Labor Hours":              labor,
        "Equipment Utilization":    equipment,
        "Accident Count":           accident_count,
        "Anomaly Detected":         anomaly_detected,
        "Image Analysis Score":     image_score,
        "Completion Percentage":    completion,
    }

    if st.button("Predict Risk Level", width='stretch'):
        # collect all empty fields
        empty_fields = [name for name, val in fields.items() if val == "" or val is None]

        if empty_fields:
            st.warning("Please fill in the following fields before predicting:")
            for field in empty_fields:
                st.markdown(f"- {field}")
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
                "Anomaly_Detected":      bool(anomaly_detected),
                "Image_Analysis_Score":  image_score,
                "Completion_Percentage": completion,
            }

            result = predict_risk(payload)

            if "risk_level" in result:
                risk = result["risk_level"]
                color = {"Low": "green", "Medium": "orange", "High": "red"}[risk]
                st.markdown(f"### Predicted Risk Level: :{color}[**{risk}**]")
            else:
                st.error(f"Backend error: {result}")


elif page == "Cost Estimation":
    # ── Session state ───────────────────────────────────────────────────────────────
    if "prediction" not in st.session_state:
        st.session_state.prediction = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "stale" not in st.session_state:
        st.session_state.stale = False

    def mark_stale():
        st.session_state.stale = True

    # ── Header ──────────────────────────────────────────────────────────────────────
    st.title("Cost Estimator")
    st.caption("Project cost estimation via machine learning  //  v1.0")
    st.divider()

    # ── Section 1: Project Profile ─────────────────────────────────────────────────
    st.subheader("01  Project Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        project_type = st.selectbox(
            "Project Type",
            ["Tunnel", "Dam", "Building", "Road", "Bridge"],
            index=None,
            placeholder="Select project type",
            on_change=mark_stale,
        )
    with col2:
        planned_cost = st.number_input(
            "Planned Cost (USD)",
            min_value=1_045_475,
            max_value=49_968_538,
            value=None,
            step=10_000,
            placeholder="1,045,475 – 49,968,538",
            on_change=mark_stale,
        )
    with col3:
        planned_duration = st.number_input(
            "Planned Duration (days)",
            min_value=180,
            max_value=899,
            value=None,
            step=1,
            placeholder="180 – 899 days",
            on_change=mark_stale,
        )

    st.divider()

    # ── Section 2: Site Conditions ─────────────────────────────────────────────────
    st.subheader("02  Site Conditions")

    col4, col5, col6, col7 = st.columns(4)

    with col4:
        load_bearing = st.number_input(
            "Load Bearing Capacity (kN/m²)",
            min_value=50.0,
            max_value=499.0,
            value=None,
            step=1.0,
            placeholder="50.0 – 499.0",
            on_change=mark_stale,
        )
    with col5:
        temperature = st.number_input(
            "Temperature (°C)",
            min_value=-10.0,
            max_value=45.0,
            value=None,
            step=0.5,
            placeholder="-10.0 – 45.0",
            on_change=mark_stale,
        )
    with col6:
        humidity = st.number_input(
            "Humidity (%)",
            min_value=20.0,
            max_value=90.0,
            value=None,
            step=1.0,
            placeholder="20.0 – 90.0",
            on_change=mark_stale,
        )
    with col7:
        weather_condition = st.selectbox(
            "Weather Condition",
            ["Sunny", "Cloudy", "Rainy", "Stormy", "Snowy"],
            index=None,
            placeholder="Select condition",
            on_change=mark_stale,
        )

    st.divider()

    # ── Section 3: Environmental & Operational ─────────────────────────────────────
    st.subheader("03  Environmental & Operational")

    col8, col9, col10, col11, col12 = st.columns(5)

    with col8:
        aqi = st.number_input(
            "Air Quality Index",
            min_value=50,
            max_value=299,
            value=None,
            step=1,
            placeholder="50 – 299",
            on_change=mark_stale,
        )
    with col9:
        energy_consumption = st.number_input(
            "Energy Consumption (kWh)",
            min_value=5054.0,
            max_value=49942.0,
            value=None,
            step=100.0,
            placeholder="5,054 – 49,942",
            on_change=mark_stale,
        )
    with col10:
        material_usage = st.number_input(
            "Material Usage (tons)",
            min_value=101.0,
            max_value=999.0,
            value=None,
            step=1.0,
            placeholder="101 – 999",
            on_change=mark_stale,
        )
    with col11:
        labor_hours = st.number_input(
            "Labor Hours",
            min_value=1001,
            max_value=9997,
            value=None,
            step=50,
            placeholder="1,001 – 9,997",
            on_change=mark_stale,
        )
    with col12:
        accident_count = st.number_input(
            "Accident Count",
            min_value=0,
            max_value=9,
            value=None,
            step=1,
            placeholder="0 – 9",
            on_change=mark_stale,
        )

    st.divider()

    # ── Predict button ──────────────────────────────────────────────────────────────
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        predict_clicked = st.button("Generate Estimate", use_container_width=True, type="primary")

    if predict_clicked:
        missing_nums = any(v is None for v in [
            planned_cost, planned_duration, load_bearing,
            temperature, humidity, aqi, energy_consumption,
            material_usage, labor_hours, accident_count
        ])
        missing_cats = any(v is None for v in [project_type, weather_condition])

        if missing_nums or missing_cats:
            st.warning("Please fill in all fields before generating an estimate.")
        else:
            payload = {
                "Project_Type": project_type,
                "Planned_Cost": planned_cost,
                "Planned_Duration": planned_duration,
                "Load_Bearing_Capacity": load_bearing,
                "Temperature": temperature,
                "Humidity": humidity,
                "Weather_Condition": weather_condition,
                "Air_Quality_Index": aqi,
                "Energy_Consumption": energy_consumption,
                "Material_Usage": material_usage,
                "Labor_Hours": labor_hours,
                "Accident_Count": accident_count,
            }
            try:
                with st.spinner("Running model inference..."):
                    response = requests.post(
                        "http://localhost:8000/predict_cost",
                        json=payload,
                        timeout=10,
                    )
                response.raise_for_status()
                data = response.json()
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

    # ── Result display ──────────────────────────────────────────────────────────────
    if st.session_state.prediction is not None:

        st.subheader("Estimated Project Cost")

        cost = st.session_state.prediction
        formatted = f"${cost:,.0f}" if isinstance(cost, (int, float)) else str(cost)
        deviation = f"${cost - planned_cost:,.0f}" if isinstance(cost, (int, float)) else str(cost)

        m0, m1 = st.columns(2)
        m0.metric(label="Predicted Cost (USD)", value=formatted)
        m1.metric(label="Cost Deviation (USD)", value=(deviation))

        if st.session_state.stale:
            st.info("Input values have changed — click Generate Estimate to refresh.")

        st.caption(f"Project: {project_type}  //  Duration: {planned_duration} days  //  Weather: {weather_condition}")


    elif st.session_state.error:
        st.error(st.session_state.error)
