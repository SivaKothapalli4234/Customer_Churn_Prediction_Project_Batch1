"""
ChurnSense Pro - Customer Churn Prediction System
==================================================
A complete ML-powered churn prediction platform
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import plotly.graph_objects as go
import plotly.express as px
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    .main-header {
        font-size: 52px;
        font-weight: 800;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px 0;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #718096;
        font-size: 18px;
        margin-bottom: 40px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 15px;
        border-radius: 10px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: bold;
    }
    .insight-box {
        background-color: #f7fafc;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# LOAD MODEL & ARTIFACTS
# ═══════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    model = XGBClassifier()
    # Newer xgboost versions may require _estimator_type for sklearn wrapper loading.
    model._estimator_type = "classifier"
    model.load_model("models/churn_model.json")
    return model

@st.cache_resource
def load_artifacts():
    scaler = joblib.load("models/scaler.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
    numeric_cols = joblib.load("models/numeric_cols.pkl")
    
    with open("models/dataset_stats.json", "r") as f:
        stats = json.load(f)
    
    with open("models/model_comparison.json", "r") as f:
        model_comparison = json.load(f)
    
    with open("models/feature_importance.json", "r") as f:
        feature_importance = json.load(f)
    
    return scaler, feature_columns, numeric_cols, stats, model_comparison, feature_importance

model = load_model()
scaler, feature_columns, numeric_cols, stats, model_comparison, feature_importance = load_artifacts()

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("<div class='main-header'>📊 Customer Churn Prediction</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>AI-Powered Customer Churn Prediction & Analytics Platform</div>", unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════
st.sidebar.title("🎯 Navigation")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Select Module:",
    ["🏠 Dashboard", "🔍 Single Prediction", "📂 Bulk Prediction", "📊 Model Performance", "💡 Business Insights"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Start with Dashboard to see overall metrics, then use prediction modules.")

# ═══════════════════════════════════════════════════════════
# 🏠 DASHBOARD
# ═══════════════════════════════════════════════════════════
if menu == "🏠 Dashboard":
    st.markdown("### 📈 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", f"{stats['total_customers']:,}")
    with col2:
        st.metric("Churned", f"{stats['churn_count']:,}", delta=f"{stats['churn_rate']}%", delta_color="inverse")
    with col3:
        st.metric("Retained", f"{stats['no_churn_count']:,}")
    with col4:
        st.metric("Avg Tenure", f"{stats['avg_tenure']} months")
    
    st.markdown("---")
    
    # Churn distribution pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Churn Distribution")
        fig = go.Figure(data=[go.Pie(
            labels=["Retained", "Churned"],
            values=[stats['no_churn_count'], stats['churn_count']],
            hole=0.4,
            marker=dict(colors=["#48bb78", "#f56565"])
        )])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Financial Metrics")
        st.metric("Avg Monthly Charges", f"{stats['avg_monthly']}")
        st.metric("Avg Total Charges", f"{stats['avg_total']}")
        
        # Model performance summary
        st.markdown("### 🤖 Model Performance (XGBoost)")
        xgb = stats['xgb_metrics']
        st.metric("Accuracy", f"{xgb['accuracy']*100:.2f}%")
        st.metric("ROC-AUC", f"{xgb['roc_auc']:.4f}")
    
    st.markdown("---")
    
    # Churn by contract type
    st.markdown("### 📋 Churn Rate by Contract Type")
    contract_data = stats['contract_churn']
    fig = px.bar(
        x=list(contract_data.keys()),
        y=[v*100 for v in contract_data.values()],
        labels={"x": "Contract Type", "y": "Churn Rate (%)"},
        color=[v*100 for v in contract_data.values()],
        color_continuous_scale="Reds"
    )
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# 🔍 SINGLE PREDICTION
# ═══════════════════════════════════════════════════════════
elif menu == "🔍 Single Prediction":
    st.markdown("### 👤 Enter Customer Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Demographics**")
        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior Citizen?", ["No", "Yes"])
        partner = st.selectbox("Has Partner?", ["No", "Yes"])
        dependents = st.selectbox("Has Dependents?", ["No", "Yes"])
    
    with col2:
        st.markdown("**📞 Services**")
        phone_service = st.selectbox("Phone Service?", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines?", ["No", "Yes", "No phone service"])
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        online_security = st.selectbox("Online Security?", ["No", "Yes", "No internet service"])
        online_backup = st.selectbox("Online Backup?", ["No", "Yes", "No internet service"])
        device_protection = st.selectbox("Device Protection?", ["No", "Yes", "No internet service"])
        tech_support = st.selectbox("Tech Support?", ["No", "Yes", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV?", ["No", "Yes", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies?", ["No", "Yes", "No internet service"])
    
    with col3:
        st.markdown("**💰 Billing & Contract**")
        tenure = st.number_input("Tenure (Months)", min_value=1, max_value=72, value=12)
        monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=70.0, step=0.1, format="%.2f")
        total_charges = monthly_charges * tenure
        st.number_input("Total Charges", value=total_charges, step=1.0, format="%.2f", disabled=True)
        contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing?", ["Yes", "No"])
        payment_method = st.selectbox("Payment Method", [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ])
    
    st.markdown("---")
    
    if st.button("🚀 Predict Churn Risk"):
        # Build input dataframe
        input_data = {
            "gender": gender,
            "SeniorCitizen": senior_citizen,
            "Partner": partner,
            "Dependents": dependents,
            "tenure": tenure,
            "PhoneService": phone_service,
            "MultipleLines": multiple_lines,
            "InternetService": internet_service,
            "OnlineSecurity": online_security,
            "OnlineBackup": online_backup,
            "DeviceProtection": device_protection,
            "TechSupport": tech_support,
            "StreamingTV": streaming_tv,
            "StreamingMovies": streaming_movies,
            "Contract": contract,
            "PaperlessBilling": paperless_billing,
            "PaymentMethod": payment_method,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges
        }
        
        # Feature engineering (same as training)
        if tenure <= 12:
            tenure_group = "0-1 yr"
        elif tenure <= 24:
            tenure_group = "1-2 yr"
        elif tenure <= 48:
            tenure_group = "2-4 yr"
        else:
            tenure_group = "4-6 yr"
        
        if monthly_charges <= 35:
            charge_tier = "Low"
        elif monthly_charges <= 65:
            charge_tier = "Medium"
        elif monthly_charges <= 95:
            charge_tier = "High"
        else:
            charge_tier = "Premium"
        
        # Count services
        service_vals = [phone_service, multiple_lines, internet_service, online_security,
                       online_backup, device_protection, tech_support, streaming_tv, streaming_movies]
        num_services = sum(1 for v in service_vals if v.lower() in ["yes", "dsl", "fiber optic"])
        
        spend_per_service = monthly_charges / num_services if num_services > 0 else monthly_charges
        is_high_value = 1 if monthly_charges > 70 else 0
        
        input_data["tenure_group"] = tenure_group
        input_data["charge_tier"] = charge_tier
        input_data["num_services"] = num_services
        input_data["spend_per_service"] = spend_per_service
        input_data["is_high_value"] = is_high_value
        
        # Convert to dataframe and encode
        input_df = pd.DataFrame([input_data])
        input_df = pd.get_dummies(input_df, drop_first=True)
        input_df = input_df.reindex(columns=feature_columns, fill_value=0)
        
        # Scale numeric features
        input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])
        
        # Predict
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        st.markdown("---")
        st.markdown("### 🎯 Prediction Result")
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=probability*100,
            title={"text": "Churn Risk %", "font": {"size": 28}},
            delta={"reference": 50},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkred"},
                "steps": [
                    {"range": [0, 30], "color": "lightgreen"},
                    {"range": [30, 70], "color": "orange"},
                    {"range": [70, 100], "color": "red"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 70
                }
            }
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics
        colA, colB, colC = st.columns(3)
        
        with colA:
            st.metric("Churn Probability", f"{probability*100:.1f}%")
        
        with colB:
            if probability < 0.3:
                risk_level = "Low"
                color = "🟢"
            elif probability < 0.7:
                risk_level = "Medium"
                color = "🟡"
            else:
                risk_level = "High"
                color = "🔴"
            st.metric("Risk Level", f"{color} {risk_level}")
        
        with colC:
            retention_score = int((1-probability)*100)
            st.metric("Retention Score", f"{retention_score}%")
        
        st.markdown("---")
        
        # Recommendations
        if probability < 0.3:
            st.success("✅ **Low Risk Customer** - Likely to stay with the service")
            st.markdown("""
            <div class='insight-box'>
            <b>Recommended Actions:</b>
            <ul>
                <li>Continue standard engagement</li>
                <li>Consider upselling premium services</li>
                <li>Maintain service quality</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        elif probability < 0.7:
            st.warning("⚠️ **Medium Risk Customer** - Consider retention strategies")
            st.markdown("""
            <div class='insight-box'>
            <b>Recommended Actions:</b>
            <ul>
                <li>Offer loyalty discounts or promotions</li>
                <li>Reach out with personalized offers</li>
                <li>Survey for satisfaction feedback</li>
                <li>Highlight value-added services</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("🚨 **High Churn Risk** - Immediate action recommended!")
            st.markdown("""
            <div class='insight-box'>
            <b>Urgent Actions Required:</b>
            <ul>
                <li>Immediate outreach by retention team</li>
                <li>Offer contract upgrade with discount</li>
                <li>Provide free premium services trial</li>
                <li>Assign dedicated account manager</li>
                <li>Investigate service quality issues</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# 📂 BULK PREDICTION
# ═══════════════════════════════════════════════════════════
elif menu == "📂 Bulk Prediction":
    st.markdown("### 📤 Upload Customer Dataset")
    
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing data..."):
                data = pd.read_csv(uploaded_file)
                
                st.success(f"✅ Loaded {len(data)} customer records")
                
                # Show sample
                with st.expander("📋 View Sample Data"):
                    st.dataframe(data.head(10))
                
                # Feature engineering for bulk data
                data_processed = data.copy()
                
                # Add tenure_group
                data_processed['tenure_group'] = pd.cut(
                    data_processed['tenure'],
                    bins=[0, 12, 24, 48, 72],
                    labels=["0-1 yr", "1-2 yr", "2-4 yr", "4-6 yr"]
                )
                
                # Add charge_tier
                data_processed['charge_tier'] = pd.cut(
                    data_processed['MonthlyCharges'],
                    bins=[0, 35, 65, 95, 200],
                    labels=["Low", "Medium", "High", "Premium"]
                )
                
                # Count services
                def count_services_bulk(row):
                    service_cols = ['PhoneService', 'MultipleLines', 'InternetService',
                                   'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                                   'TechSupport', 'StreamingTV', 'StreamingMovies']
                    count = 0
                    for col in service_cols:
                        if col in row.index:
                            val = str(row[col]).lower()
                            if val in ["yes", "dsl", "fiber optic"]:
                                count += 1
                    return count
                
                data_processed['num_services'] = data_processed.apply(count_services_bulk, axis=1)
                
                # Spend per service
                data_processed['spend_per_service'] = data_processed.apply(
                    lambda r: r['MonthlyCharges'] / r['num_services'] if r['num_services'] > 0 else r['MonthlyCharges'],
                    axis=1
                )
                
                # High value flag
                data_processed['is_high_value'] = (data_processed['MonthlyCharges'] > 70).astype(int)
                
                # Encode and predict
                data_encoded = pd.get_dummies(data_processed, drop_first=True)
                data_encoded = data_encoded.reindex(columns=feature_columns, fill_value=0)
                
                # Scale numeric features
                data_encoded[numeric_cols] = scaler.transform(data_encoded[numeric_cols])
                
                predictions = model.predict(data_encoded)
                probabilities = model.predict_proba(data_encoded)[:, 1]
                
                data["Churn_Prediction"] = predictions
                data["Churn_Probability"] = probabilities
                data["Risk_Level"] = pd.cut(
                    probabilities,
                    bins=[0, 0.3, 0.7, 1.0],
                    labels=["Low", "Medium", "High"]
                )
            
            # Summary metrics
            st.markdown("### 📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Customers", len(data))
            with col2:
                churn_count = data["Churn_Prediction"].sum()
                st.metric("Predicted Churns", churn_count)
            with col3:
                churn_rate = (churn_count/len(data))*100
                st.metric("Churn Rate", f"{churn_rate:.1f}%")
            with col4:
                avg_prob = data["Churn_Probability"].mean()*100
                st.metric("Avg Risk", f"{avg_prob:.1f}%")
            
            st.markdown("---")
            
            # Risk distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Churn Risk Distribution")
                fig = px.histogram(
                    data,
                    x="Churn_Probability",
                    nbins=30,
                    title="Customer Churn Risk Distribution",
                    labels={"Churn_Probability": "Churn Probability"},
                    color_discrete_sequence=["#667eea"]
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🎯 Risk Level Breakdown")
                risk_counts = data["Risk_Level"].value_counts()
                fig = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    color=risk_counts.index,
                    color_discrete_map={"Low": "#48bb78", "Medium": "#ed8936", "High": "#f56565"}
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Show results table
            st.markdown("### 📋 Detailed Results")
            st.dataframe(
                data[["Churn_Prediction", "Churn_Probability", "Risk_Level"]].head(100),
                use_container_width=True
            )
            
            # Download button
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="churn_predictions.csv",
                mime="text/csv"
            )
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please ensure your CSV has the correct columns matching the training data.")

# ═══════════════════════════════════════════════════════════
# 📊 MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════
elif menu == "📊 Model Performance":
    st.markdown("### 🤖 Model Comparison")
    
    # Create comparison dataframe
    comparison_df = pd.DataFrame(model_comparison).T
    comparison_df = comparison_df[["accuracy", "precision", "recall", "f1", "roc_auc"]]
    comparison_df = comparison_df.round(4)
    
    st.dataframe(comparison_df, use_container_width=True)
    
    st.markdown("---")
    
    # Bar chart comparison
    st.markdown("### 📊 Metric Comparison Across Models")
    
    metric_choice = st.selectbox("Select Metric", ["accuracy", "precision", "recall", "f1", "roc_auc"])
    
    fig = px.bar(
        x=comparison_df.index,
        y=comparison_df[metric_choice],
        labels={"x": "Model", "y": metric_choice.upper()},
        title=f"{metric_choice.upper()} Comparison",
        color=comparison_df[metric_choice],
        color_continuous_scale="Viridis"
    )
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Confusion matrix — let user pick model
    st.markdown("### 🎯 Confusion Matrix")
    cm_model = st.selectbox("Select Model for Confusion Matrix", list(model_comparison.keys()), index=list(model_comparison.keys()).index("XGBoost"))
    cm = model_comparison[cm_model]["confusion_matrix"]
    
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=["Predicted No Churn", "Predicted Churn"],
        y=["Actual No Churn", "Actual Churn"],
        colorscale="Blues",
        text=cm,
        texttemplate="%{text}",
        textfont={"size": 20}
    ))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Feature importance
    st.markdown("### 🔍 Top 20 Most Important Features")
    
    feat_df = pd.DataFrame({
        "Feature": list(feature_importance.keys()),
        "Importance": list(feature_importance.values())
    })
    
    fig = px.bar(
        feat_df,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Feature Importance (XGBoost)",
        color="Importance",
        color_continuous_scale="Purples"
    )
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════
# 💡 BUSINESS INSIGHTS
# ═══════════════════════════════════════════════════════════
elif menu == "💡 Business Insights":
    st.markdown("### 💡 Key Business Insights & Recommendations")
    
    st.markdown("""
    <div class='insight-box'>
    <h4>🎯 Top Churn Drivers Identified</h4>
    <ol>
        <li><b>Contract Type:</b> Month-to-month contracts have the highest churn rate</li>
        <li><b>Tenure:</b> Customers with less than 1 year tenure are at highest risk</li>
        <li><b>Internet Service:</b> Fiber optic customers churn more than DSL</li>
        <li><b>Payment Method:</b> Electronic check users have higher churn</li>
        <li><b>Services:</b> Lack of online security and tech support increases churn</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Contract type analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Churn by Contract Type")
        contract_data = stats['contract_churn']
        fig = px.bar(
            x=list(contract_data.keys()),
            y=[v*100 for v in contract_data.values()],
            labels={"x": "Contract Type", "y": "Churn Rate (%)"},
            color=[v*100 for v in contract_data.values()],
            color_continuous_scale="Reds",
            text=[f"{v*100:.1f}%" for v in contract_data.values()]
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🌐 Churn by Internet Service")
        internet_data = stats['internet_churn']
        fig = px.bar(
            x=list(internet_data.keys()),
            y=[v*100 for v in internet_data.values()],
            labels={"x": "Internet Service", "y": "Churn Rate (%)"},
            color=[v*100 for v in internet_data.values()],
            color_continuous_scale="Oranges",
            text=[f"{v*100:.1f}%" for v in internet_data.values()]
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class='insight-box'>
    <h4>📈 Strategic Recommendations</h4>
    
    <h5>1. Contract Strategy</h5>
    <ul>
        <li>Incentivize long-term contracts with discounts</li>
        <li>Offer contract upgrade bonuses</li>
        <li>Implement early renewal rewards</li>
    </ul>
    
    <h5>2. Service Bundling</h5>
    <ul>
        <li>Bundle online security with internet plans</li>
        <li>Offer tech support as a value-add</li>
        <li>Create premium service packages</li>
    </ul>
    
    <h5>3. Payment Method Optimization</h5>
    <ul>
        <li>Encourage automatic payment methods</li>
        <li>Offer discounts for credit card/bank transfer</li>
        <li>Reduce friction in payment process</li>
    </ul>
    
    <h5>4. Early Intervention Program</h5>
    <ul>
        <li>Target customers in first 12 months</li>
        <li>Proactive outreach for high-risk segments</li>
        <li>Personalized retention offers</li>
    </ul>
    
    <h5>5. Service Quality Focus</h5>
    <ul>
        <li>Investigate fiber optic service issues</li>
        <li>Improve customer support for new users</li>
        <li>Regular satisfaction surveys</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class='insight-box'>
    <h4>💰 Estimated Business Impact</h4>
    <p>Based on the model's performance (ROC-AUC: {:.4f}):</p>
    <ul>
        <li><b>Potential Churn Reduction:</b> 15-25% with targeted interventions</li>
        <li><b>Customer Lifetime Value Increase:</b> 20-30% for retained customers</li>
        <li><b>ROI on Retention Programs:</b> Estimated 3-5x return</li>
    </ul>
    </div>
    """.format(stats['xgb_metrics']['roc_auc']), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("---")

