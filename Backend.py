from fastapi import FastAPI
from fastapi.responses import FileResponse
import joblib
from functools import lru_cache
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

xgb_model = joblib.load('xgb_model.pkl')
scaler    = joblib.load('scaler.pkl')
encoder   = joblib.load('encoder.pkl')
cost_pipeline = joblib.load("CostEstimationLGBMPipeline.joblib")


numerical_cols   = ['Planned_Cost', 'Planned_Duration', 'Vibration_Level', 'Crack_Width',
                    'Load_Bearing_Capacity', 'Temperature', 'Humidity', 'Air_Quality_Index',
                    'Energy_Consumption', 'Material_Usage', 'Labor_Hours', 'Equipment_Utilization',
                    'Accident_Count', 'Image_Analysis_Score', 'Anomaly_Detected', 'Completion_Percentage']

categorical_cols = ['Project_Type', 'Weather_Condition']

RISK_MAPPING_INV = {0: 'Low', 1: 'Medium', 2: 'High'}

class InputSchema(BaseModel):
    Project_Type:          str
    Planned_Cost:          float
    Planned_Duration:      float
    Vibration_Level:       float
    Crack_Width:           float
    Load_Bearing_Capacity: float
    Temperature:           float
    Humidity:              float
    Weather_Condition:     str
    Air_Quality_Index:     float
    Energy_Consumption:    float
    Material_Usage:        float
    Labor_Hours:           float
    Equipment_Utilization: float
    Accident_Count:        float
    Anomaly_Detected:      int
    Image_Analysis_Score:  float
    Completion_Percentage: float


class CostInputSchema(BaseModel):
    Project_Type:          str
    Planned_Cost:          float
    Planned_Duration:      float
    Load_Bearing_Capacity: float
    Temperature:           float
    Humidity:              float
    Weather_Condition:     str
    Air_Quality_Index:     float
    Energy_Consumption:    float
    Material_Usage:        float
    Labor_Hours:           float
    Accident_Count:        float

#---------------------- Data Loading --------------------------------
@lru_cache(maxsize=1)
def load_data():
    return pd.read_parquet("main_df.parquet")

#--------------------- End Point 1 ----------------------------------
@app.get("/shape")
def get_shape():
    df = load_data()
    return {"rows": df.shape[0], "cols": df.shape[1]}
#--------------------- End Point 2 -----------------------------------
@app.get("/filter")
def filtered_data(targets : str = ""):
    df = load_data()

    if targets:
        target_nums = [int(x) for x in targets.split(",")]
        filtered_data = df[df["target_numeric"].isin(target_nums)]

        return {
            "data" : filtered_data.to_dict(orient="records"),
            "filtered_count":len(filtered_data),
            "total_count" : len(df)
        }
    else:
        return {"data":[],"filtered_count":0,"total_count":len(df)}

#-------------------- End Point 3--------------------------------------
@app.get("/statistics")
def get_stat():
    df = load_data()
    stat = df.describe()
    return stat.reset_index().to_dict(orient="records")

#------------------- End Point 4 ---------------------------------------
@app.get("/image")
def get_image():
    return FileResponse("RC_COM.png", media_type="image/png")

#------------------- End Point 5 ---------------------------------------
@app.post("/predict")
def predict(data: InputSchema):
    df = pd.DataFrame([data.dict()])

    encoded = encoder.transform(df[categorical_cols])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out())

    df[numerical_cols] = scaler.transform(df[numerical_cols])

    df = df.drop(columns=categorical_cols)
    df = pd.concat([df, encoded_df], axis=1)

    df = df[xgb_model.get_booster().feature_names]

    prediction = xgb_model.predict(df, validate_features=False)[0]
    
    return {"risk_level": RISK_MAPPING_INV[int(prediction)]}



@app.post("/predict_cost")
def predict_cost(data: CostInputSchema):
    df = pd.DataFrame([data.dict()])
    prediction = cost_pipeline.predict(df)[0]
    return {"estimated_cost": round(float(prediction), 2)}