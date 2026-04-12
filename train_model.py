"""
ChurnSense Pro - Model Training Pipeline
Synced with Final_customer_churn_analysis_eda_ml_modelling notebook
Trains: Random Forest, Logistic Regression, Gradient Boosting, XGBoost, Decision Tree, SVM
"""

import pandas as pd
import numpy as np
import joblib
import json
import warnings
warnings.filterwarnings("ignore")

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier

import os
os.makedirs("models", exist_ok=True)

# ── [1/7] Load dataset ──────────────────────────────────────
print("[1/7] Loading dataset...")
df = pd.read_csv("customer_churn.csv")

# ── [2/7] Clean data ────────────────────────────────────────
print("[2/7] Cleaning data...")
df = df.drop(["customerID"], axis=1)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df.drop(labels=df[df["tenure"] == 0].index, axis=0, inplace=True)
df.dropna(inplace=True)
df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

# ── [3/7] Encode & prepare features ─────────────────────────
print("[3/7] Encoding features...")
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
df = pd.get_dummies(df, drop_first=True)

X = df.drop("Churn", axis=1)
y = df["Churn"]

# ── [4/7] Scale numeric features ────────────────────────────
print("[4/7] Scaling features...")
num_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols] = scaler.transform(X_test[num_cols])

# ── [5/7] Train all models ───────────────────────────────────
print("[5/7] Training models...")

def get_metrics(model, X_test, y_test, use_proba=True):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if use_proba else model.decision_function(X_test)
    return {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred), 4),
        "f1":        round(f1_score(y_test, y_pred), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_prob), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
    }

results = {}

# Random Forest
print("  -> Random Forest")
rf = RandomForestClassifier(n_estimators=400, min_samples_split=5, class_weight="balanced", random_state=42)
rf.fit(X_train, y_train)
results["Random Forest"] = get_metrics(rf, X_test, y_test)

# Logistic Regression
print("  -> Logistic Regression")
lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
lr.fit(X_train, y_train)
results["Logistic Regression"] = get_metrics(lr, X_test, y_test)

# Gradient Boosting
print("  -> Gradient Boosting")
gb = GradientBoostingClassifier(n_estimators=500, learning_rate=0.03, max_depth=3, random_state=42)
gb.fit(X_train, y_train)
results["Gradient Boosting"] = get_metrics(gb, X_test, y_test)

# XGBoost (tuned)
print("  -> XGBoost (RandomizedSearchCV)")
xgb = XGBClassifier(objective="binary:logistic", random_state=42,
                    use_label_encoder=False, eval_metric="logloss")
param_grid_xgb = {
    "n_estimators": [300, 500, 700],
    "max_depth": [3, 4, 5, 6],
    "learning_rate": [0.01, 0.03, 0.05],
    "subsample": [0.8, 1],
    "colsample_bytree": [0.8, 1]
}
xgb_search = RandomizedSearchCV(xgb, param_grid_xgb, n_iter=10, cv=3,
                                 scoring="accuracy", random_state=42, n_jobs=-1, verbose=0)
xgb_search.fit(X_train, y_train)
best_xgb = xgb_search.best_estimator_
results["XGBoost"] = get_metrics(best_xgb, X_test, y_test)

# Decision Tree (tuned)
print("  -> Decision Tree (GridSearchCV)")
dt = DecisionTreeClassifier(class_weight="balanced", random_state=42)
param_grid_dt = {
    "criterion": ["gini", "entropy"],
    "max_depth": [3, 5, 10, 15, None],
    "min_samples_split": [2, 5, 10, 20],
    "min_samples_leaf": [1, 2, 5, 10]
}
dt_grid = GridSearchCV(dt, param_grid_dt, cv=5, scoring="roc_auc", n_jobs=-1)
dt_grid.fit(X_train, y_train)
best_dt = dt_grid.best_estimator_
results["Decision Tree"] = get_metrics(best_dt, X_test, y_test)

# SVM (tuned)
print("  -> SVM (GridSearchCV)")
svm_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(probability=True, random_state=42))
])
param_grid_svm = {
    "svm__kernel": ["rbf", "linear"],
    "svm__C": [0.1, 1, 10],
    "svm__gamma": ["scale", "auto"]
}
svm_grid = GridSearchCV(svm_pipeline, param_grid_svm, cv=5, scoring="roc_auc", n_jobs=-1)
svm_grid.fit(X_train, y_train)
best_svm = svm_grid.best_estimator_
results["SVM"] = get_metrics(best_svm, X_test, y_test)

# ── [6/7] Print results ──────────────────────────────────────
print("\n[6/7] Model Results:")
print(f"{'Model':<22} {'Accuracy':>9} {'Precision':>10} {'Recall':>8} {'F1':>8} {'ROC-AUC':>9}")
print("-" * 70)
for name, m in results.items():
    print(f"{name:<22} {m['accuracy']:>9.4f} {m['precision']:>10.4f} {m['recall']:>8.4f} {m['f1']:>8.4f} {m['roc_auc']:>9.4f}")

# ── [7/7] Save artifacts ─────────────────────────────────────
print("\n[7/7] Saving artifacts...")

# Best model = XGBoost
best_xgb.save_model("models/churn_model.json")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(X.columns.tolist(), "models/feature_columns.pkl")
joblib.dump(num_cols, "models/numeric_cols.pkl")

# Feature importance (XGBoost top 20)
importance = best_xgb.feature_importances_
feat_imp = dict(sorted(
    zip(X.columns.tolist(), importance.tolist()),
    key=lambda x: x[1], reverse=True
)[:20])
with open("models/feature_importance.json", "w") as f:
    json.dump(feat_imp, f)

# Model comparison
with open("models/model_comparison.json", "w") as f:
    json.dump(results, f)

# Dataset stats
df_raw = pd.read_csv("customer_churn.csv")
df_raw["TotalCharges"] = pd.to_numeric(df_raw["TotalCharges"], errors="coerce")
df_raw.drop(labels=df_raw[df_raw["tenure"] == 0].index, inplace=True)
df_raw.dropna(inplace=True)
df_raw["SeniorCitizen"] = df_raw["SeniorCitizen"].map({0: "No", 1: "Yes"})

churn_count = int((df_raw["Churn"] == "Yes").sum())
no_churn_count = int((df_raw["Churn"] == "No").sum())

contract_churn = df_raw.groupby("Contract")["Churn"].apply(
    lambda x: round((x == "Yes").mean(), 4)
).to_dict()

internet_churn = df_raw.groupby("InternetService")["Churn"].apply(
    lambda x: round((x == "Yes").mean(), 4)
).to_dict()

stats = {
    "total_customers": len(df_raw),
    "churn_count": churn_count,
    "no_churn_count": no_churn_count,
    "churn_rate": round(churn_count / len(df_raw) * 100, 2),
    "avg_tenure": round(df_raw["tenure"].mean(), 1),
    "avg_monthly": round(df_raw["MonthlyCharges"].mean(), 2),
    "avg_total": round(df_raw["TotalCharges"].mean(), 2),
    "contract_churn": contract_churn,
    "internet_churn": internet_churn,
    "xgb_metrics": {
        "accuracy": results["XGBoost"]["accuracy"],
        "roc_auc": results["XGBoost"]["roc_auc"]
    }
}
with open("models/dataset_stats.json", "w") as f:
    json.dump(stats, f)

print("\n✅ Training complete! All artifacts saved to models/")
