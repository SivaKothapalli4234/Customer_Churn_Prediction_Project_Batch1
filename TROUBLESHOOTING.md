# 🔧 Troubleshooting Guide - ChurnSense Pro

## ✅ Your Project is Ready!

All files are created and the model is trained. Here's how to run it:

---

## 🚀 How to Run

### Open Command Prompt and run:
```bash
cd C:\Users\ASUS\OneDrive\Desktop\ChurnSense-Pro
streamlit run app.py
```

The app will open automatically in your browser at: **http://localhost:8501**

---

## 🐛 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError"
**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit pandas numpy scikit-learn xgboost imbalanced-learn plotly joblib
```

---

### Issue 2: "FileNotFoundError: models/churn_model.json"
**Error:** Can't find model files

**Solution:**
```bash
python train_model.py
```
This will create all 7 files in the `/models/` folder.

---

### Issue 3: Port Already in Use
**Error:** `Port 8501 is already in use`

**Solution:**
```bash
streamlit run app.py --server.port 8502
```
Or close the other Streamlit app first.

---

### Issue 4: Bulk Prediction Fails
**Error:** CSV upload doesn't work

**Solution:**
- Make sure your CSV has ALL these columns:
  - gender, SeniorCitizen, Partner, Dependents, tenure
  - PhoneService, MultipleLines, InternetService
  - OnlineSecurity, OnlineBackup, DeviceProtection
  - TechSupport, StreamingTV, StreamingMovies
  - Contract, PaperlessBilling, PaymentMethod
  - MonthlyCharges, TotalCharges

- Use `sample_test.csv` as a template

---

### Issue 5: Unicode Error During Training
**Error:** `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution:**
This is just a display issue on Windows. The model still trains successfully!
Check if `/models/` folder has 7 files:
- churn_model.json
- scaler.pkl
- feature_columns.pkl
- numeric_cols.pkl
- model_comparison.json
- feature_importance.json
- dataset_stats.json

If all 7 files exist, you're good to go!

---

## 📊 How to Test Bulk Prediction

1. Go to "📂 Bulk Prediction" page
2. Click "Browse files"
3. Upload `sample_test.csv` (included in the project)
4. You should see:
   - Summary statistics
   - Risk distribution chart
   - Risk level breakdown
   - Detailed results table
   - Download button

---

## 🎯 Quick Test Checklist

### ✅ After Running `streamlit run app.py`:

1. **Dashboard Page:**
   - [ ] Shows total customers (7,032)
   - [ ] Shows churn rate (26.6%)
   - [ ] Shows pie chart
   - [ ] Shows contract type chart

2. **Single Prediction Page:**
   - [ ] All input fields visible
   - [ ] Can enter customer details
   - [ ] "Predict Churn Risk" button works
   - [ ] Shows gauge chart
   - [ ] Shows risk level
   - [ ] Shows recommendations

3. **Bulk Prediction Page:**
   - [ ] File uploader visible
   - [ ] Can upload sample_test.csv
   - [ ] Shows summary statistics
   - [ ] Shows 2 charts
   - [ ] Shows results table
   - [ ] Download button works

4. **Model Performance Page:**
   - [ ] Shows model comparison table
   - [ ] Shows metric comparison chart
   - [ ] Shows confusion matrix
   - [ ] Shows feature importance

5. **Business Insights Page:**
   - [ ] Shows top churn drivers
   - [ ] Shows 2 charts
   - [ ] Shows strategic recommendations
   - [ ] Shows business impact

---

## 🔍 Verify Model Files

Run this to check if all model files exist:
```bash
dir models
```

You should see:
```
churn_model.json
dataset_stats.json
feature_columns.pkl
feature_importance.json
model_comparison.json
numeric_cols.pkl
scaler.pkl
```

---

## 💡 Tips

### Tip 1: Refresh the App
If something doesn't work, press **R** in the browser to refresh.

### Tip 2: Clear Cache
If data seems wrong, press **C** in the browser to clear cache.

### Tip 3: Check Terminal
Look at the terminal/command prompt for error messages.

### Tip 4: Test with Sample Data
Always test bulk prediction with `sample_test.csv` first before using your own data.

---

## 🆘 Still Having Issues?

### Check These:
1. ✅ Python 3.8+ installed?
2. ✅ All dependencies installed?
3. ✅ In correct folder (ChurnSense-Pro)?
4. ✅ Model files exist in `/models/`?
5. ✅ Internet connection (for Streamlit)?

### Get More Help:
- Read **QUICKSTART.md**
- Read **PROJECT_SUMMARY.md**
- Check error message in terminal

---

## ✅ Everything Working?

If all 5 pages load correctly, you're ready to:
1. ✅ Test all features
2. ✅ Read VIVA_GUIDE.md
3. ✅ Prepare for presentation
4. ✅ Ace your viva! 🎓

---

**Your project is complete and ready to present!** 🚀
