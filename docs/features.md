# 📚 B-vista Features

Welcome to the full feature overview of **B-vista**—a powerful, browser-based EDA toolkit designed for pandas DataFrames.

Explore each capability grouped by functionality:

---

## 📊 1. Descriptive Statistics

B-vista offers enhanced summary statistics far beyond `df.describe()`.

### Features:
- Full summary for all data types (numeric, categorical, bool, datetime)
- Additional metrics: skewness, kurtosis, variance
- Shapiro-Wilk test for normality
- Z-score calculations per column
- Detects missing values per column


![Untitled design (2)](https://github.com/user-attachments/assets/511e124c-c1c4-45db-87a1-5424eb26fbfc)





![descriptive stats_Gifs](https://github.com/user-attachments/assets/78dc17f3-5ff3-47ae-a9be-34ff637a14c5)



🔗 [View API →](https://github.com/Baci-Ak/b-vista/blob/main/backend/models/descriptive_stats.py)
---

## 🔗 2. Correlation Matrix Explorer

Visualize relationships using **7 correlation types** with intuitive heatmaps.

### Available Correlation Types:
| Method              | Description |
|---------------------|-------------|
| Pearson             | Linear correlation |
| Spearman            | Rank-based correlation |
| Kendall             | Ordinal correlation |
| Partial             | Controls for other variables |
| Distance Correlation| Non-linear detection |
| Mutual Information  | Dependency via information theory |
| Robust              | Outlier-resistant (Winsorized + Spearman) |

![correlation_matrix_gifs](https://github.com/user-attachments/assets/8e59a3bf-d6a1-4eb8-a255-190dc4106abc)

### Image export of the Correlation Matrix
![correlation_heatmap](https://github.com/user-attachments/assets/0a3e8623-c132-4416-84b1-a949fe6266b7)

🔗 Related APIs:  
- [View API →](https://github.com/Baci-Ak/b-vista/blob/main/backend/routes/data_routes.py)  
---

## 📈 3. Distribution Analysis

Dive into variable distributions with automated visual summaries.

### Visualizations:
- Histograms with KDE overlays
- Boxplots with smart outlier detection
- QQ plots for normality inspection

### Highlights:
- Smart binning for histograms
- Log-scaling for skewed data
- Auto-handling of single-value and missing-only columns

 ![Untitled design](https://github.com/user-attachments/assets/faf457b3-2d1d-48f2-a3bf-696541b40e91)

![distrubution_gifs](https://github.com/user-attachments/assets/912bdfe3-82e9-42d9-81ff-1eb3dd851e71)



---

## 🦼️ 4. Missing Data Analysis & Diagnostics

Uncover hidden patterns and structure in your missing data.

### Visual Tools:
- Missing pattern matrix
- Correlation heatmap of null values
- Hierarchical dendrogram clustering
- Distribution bar chart of missing % per column

![missinga-data_gifs](https://github.com/user-attachments/assets/fa2a8b08-d6d7-4551-9eea-a57768b34fe3)


### Diagnostic Methods:
- **MCAR** — Little's test
- **MAR** — Logistic Regression on null masks
- **NMAR** — Expectation-Maximization & LRT

 

---

## 🧪 5. Data Cleaning Engine

Choose from **13+ imputation strategies** or drop missing rows entirely.

### Supported Cleaning Methods:
- Drop rows
- Fill with: Mean, Median, Mode
- Forward Fill, Backward Fill
- Interpolation: Linear, Spline, Polynomial
- **Advanced:** KNN, Iterative (MICE), Regression, Deep Autoencoder


![Untitled design (1)](https://github.com/user-attachments/assets/bba2612e-0f48-46d8-89e0-d9ea657805f5)


🔗 [View API →](https://github.com/Baci-Ak/b-vista/blob/main/backend/routes/data_routes.py) 

---

## 🔁 6. Data Transformation

Transform columns safely and visually with these tools:

### Supported Transformations:
- Rename columns
- Reorder columns
- Cast datatypes (numeric, bool, datetime, etc.)
- Normalize, standardize
- Format as currency or time

---

## 📂 7. Upload & Session Management

Manage multiple datasets with isolated sessions via secure upload.

### Capabilities:
- Upload CSV or pandas DataFrames
- Unique session ID per dataset
- Supports column type introspection, NaN-safe JSON export


---

## 🧬 8. Duplicate Handling

Automatically find and remove duplicates with detailed summaries.

### Functions:
- Detect all duplicate rows
- Option to keep first, last, or drop all
- Summary of removed rows with row count

 
![Untitled design (3)](https://github.com/user-attachments/assets/2409c6fe-5cbb-444c-9dab-6bc22f21d5ad)

---

## 💡 9. Cell-Level Editing (Live Sync)

Edit cells directly and broadcast changes across all connected clients using WebSockets.

### Features:
- In-place editing
- WebSocket sync per session
- Only changed value is transmitted (not whole DataFrame)

---

## 🧪 10. Notebook Launch Support

Launch B-vista directly from your Jupyter notebook:

```python
import bvista
bvista.show(df)
```

---

## 📊 11. Performance Optimized

- Smart downsampling for large datasets (>50K rows)
- Lazy rendering of plots
- Batch processing support

---

## 📸 Visual Showcase


> **Demo Workflow** – Upload → Explore → Clean → Analyze → Transform → Export

---

## ⏭️ What’s Next

- ✔️ Model interpretability (SHAP, LIME)
- ⏳ Feature importance scoring
- ⏳ Time-series specific modules

---

