import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

raw_df = pd.read_csv("bim_ai_civil_engineering_dataset.csv")
target_col = "Risk_Level"
input_cols = [
    "Project_Type",
    "Planned_Cost",
    "Planned_Duration",
    "Vibration_Level",
    "Crack_Width",
    "Load_Bearing_Capacity",
    "Temperature",
    "Humidity",
    "Weather_Condition",
    "Air_Quality_Index",
    "Energy_Consumption",
    "Material_Usage",
    "Labor_Hours",
    "Equipment_Utilization",
    "Accident_Count",
    "Image_Analysis_Score",
    "Anomaly_Detected",
    "Completion_Percentage",
]
RISK_MAPPING = {"Low": 0, "Medium": 1, "High": 2}
y = raw_df[target_col].map(RISK_MAPPING)
X = raw_df[input_cols].copy()
x_train, x_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

num = x_train.select_dtypes(include="number").columns.tolist()
cat = x_train.select_dtypes(include="object").columns.tolist()
pre = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ]
)


def to_array(arr):
    return np.asarray(arr)


def report(name, pipe):
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    acc = accuracy_score(y_test, pred)
    f1w = f1_score(y_test, pred, average="weighted")
    print(f"{name} test acc: {acc:.4f}  f1_weighted: {f1w:.4f}")


report(
    "RF default",
    Pipeline(
        [
            ("pre", pre),
            ("clf", RandomForestClassifier(random_state=42, n_jobs=-1)),
        ]
    ),
)

pre2 = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ]
)
report(
    "RF tuned",
    Pipeline(
        [
            ("pre", pre2),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=12,
                    min_samples_leaf=4,
                    min_samples_split=8,
                    max_features="sqrt",
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    ),
)

pre3 = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ]
)
report(
    "HGB",
    Pipeline(
        [
            ("pre", pre3),
            (
                "clf",
                HistGradientBoostingClassifier(
                    max_depth=6,
                    max_iter=200,
                    learning_rate=0.05,
                    l2_regularization=1.0,
                    min_samples_leaf=20,
                    random_state=42,
                ),
            ),
        ]
    ),
)

pre4 = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ]
)
pipe_xgb = Pipeline(
    [
        ("pre", pre4),
        ("to_arr", FunctionTransformer(to_array, validate=False)),
        (
            "clf",
            XGBClassifier(
                n_estimators=400,
                max_depth=4,
                learning_rate=0.05,
                min_child_weight=5,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_alpha=1.0,
                reg_lambda=2.0,
                random_state=42,
                n_jobs=-1,
                eval_metric="mlogloss",
            ),
        ),
    ]
)
report("XGB regularized", pipe_xgb)

# Re-fit best two for blend (reuse last pre - need separate fits)
pre_rf = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ]
)
rf_t = Pipeline(
    [
        ("pre", pre_rf),
        (
            "clf",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=12,
                min_samples_leaf=4,
                min_samples_split=8,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)
pre_h = ColumnTransformer(
    [
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat),
    ]
)
hgb_p = Pipeline(
    [
        ("pre", pre_h),
        (
            "clf",
            HistGradientBoostingClassifier(
                max_depth=6,
                max_iter=200,
                learning_rate=0.05,
                l2_regularization=1.0,
                min_samples_leaf=20,
                random_state=42,
            ),
        ),
    ]
)
rf_t.fit(x_train, y_train)
hgb_p.fit(x_train, y_train)
proba_rf = rf_t.predict_proba(x_test)
proba_h = hgb_p.predict_proba(x_test)
blend = (proba_rf + proba_h) / 2
pred = np.argmax(blend, axis=1)
acc = accuracy_score(y_test, pred)
f1w = f1_score(y_test, pred, average="weighted")
print(f"Blend RF+HGB test acc: {acc:.4f}  f1_weighted: {f1w:.4f}")
