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

📸 *Screenshot Placeholder* — Example of descriptive stats UI  
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

🎮 *GIF Placeholder* — Switching correlation types dynamically  
📸 *Screenshot Placeholder* — Heatmap of robust correlation  
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

📸 *Screenshot Placeholder* — Boxplot with skewness indicator  
🎮 *GIF Placeholder* — Dynamic histogram rendering  

---

## 🦼️ 4. Missing Data Detection & Diagnostics

Uncover hidden patterns and structure in your missing data.

### Visual Tools:
- Missing pattern matrix
- Correlation heatmap of null values
- Hierarchical dendrogram clustering
- Distribution bar chart of missing % per column

### Diagnostic Methods:
- **MCAR** — Little's test
- **MAR** — Logistic Regression on null masks
- **NMAR** — Expectation-Maximization & LRT

📸 *Screenshot Placeholder* — Missingno heatmap  
🎮 *GIF Placeholder* — Missing data clustering  

---

## 🧪 5. Data Cleaning Engine

Choose from **13+ imputation strategies** or drop missing rows entirely.

### Supported Cleaning Methods:
- Drop rows
- Fill with: Mean, Median, Mode
- Forward Fill, Backward Fill
- Interpolation: Linear, Spline, Polynomial
- **Advanced:** KNN, Iterative (MICE), Regression, Deep Autoencoder

🎮 *GIF Placeholder* — Cleaning via dropdown and live preview  
📸 *Screenshot Placeholder* — Comparison before vs after cleaning  
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

📸 *Screenshot Placeholder* — Column rename + type casting  
🔗 Related: [Update Cell API](https://github.com/Baci-Ak/b-vista/blob/main/backend/routes/data_routes.py) 

---

## 📂 7. Upload & Session Management

Manage multiple datasets with isolated sessions via secure upload.

### Capabilities:
- Upload CSV or pickled pandas DataFrames
- Unique session ID per dataset
- Supports column type introspection, NaN-safe JSON export


---

## 🧬 8. Duplicate Handling

Automatically find and remove duplicates with detailed summaries.

### Functions:
- Detect all duplicate rows
- Option to keep first, last, or drop all
- Summary of removed rows with row count

 
📸 *Screenshot Placeholder* — Before/after duplicates table

---

## 💡 9. Cell-Level Editing (Live Sync)

Edit cells directly and broadcast changes across all connected clients using WebSockets.

### Features:
- In-place editing
- WebSocket sync per session
- Only changed value is transmitted (not whole DataFrame)

📸 *Screenshot Placeholder* — Cell editing and real-time broadcast  
🔗 [Update Cell API](https://github.com/Baci-Ak/b-vista/blob/main/backend/routes/data_routes.py) 

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

> 🎮 *[Insert GIF or Video Demo Here]*  
> **Demo Workflow** – Upload → Explore → Clean → Analyze → Transform → Export

---

## ⏭️ What’s Next

- ✔️ Model interpretability (SHAP, LIME)
- ⏳ Feature importance scoring
- ⏳ Time-series specific modules

---

