# 📊 B-vista

> **Exploratory Data Analysis tool. Built for scale, clarity, and real-time workflows.**

<!-- Placeholder for logo or product screenshot -->
<!-- ![B-vista banner](docs/assets/banner.png) -->

---

**B-vista** is a full-stack interactive Exploratory Data Analysis (EDA) tool that pairs a Python (Flask) backend with a modern React frontend — built specifically for working with **pandas DataFrames**. It enables users to explore, clean, analyze, and transform data through a rich visual interface, with **real-time updates** and **deep statistical insight**.

Currently, B-vista supports:
- `pandas.DataFrame` objects
- Notebook-native integration (Jupyter, Colab)
- Local or hosted web-based usage


Whether you’re working in a Jupyter notebook or launching a live web session, B-vista gives you deep control over your data — from statistical summaries to real-time collaboration and missing data diagnostics, etc.

---

> 🛠️ Built with: Python · Flask · WebSockets · React · ECharts ·plotly · Pandas · NumPy



---

## ✨ Features

<!-- Placeholder for an animated GIF or UI walkthrough -->
<!-- ![B-vista in action](docs/assets/overview-demo.gif) -->

- **📈 Descriptive Statistics**
  - Instantly view count, mean, std, min, max, percentiles, and more for all numeric columns.

- **📊 Correlation Matrix**
  - Visualize Pearson/Spearman correlation across all numerical features, with heatmap-style UI.

- **📉 Distribution Analysis**
  - Generate histogram, KDE, and box plot visualizations of column distributions.

- **🧼 Missing Data Analysis**
  - Detect and categorize missingness (MCAR, MAR, NMAR) with built-in visual diagnostics.

- **🛠️ Data Cleaning & Imputation**
  - Clean your DataFrame using forward fill, backward fill, interpolation, mean/median/mode, or custom logic.

- **🔁 Data Transformation**
  - Apply column-level operations (standardization, normalization, type casting, etc.)

- **📡 Real-time Sync**
  - WebSocket-powered updates for collaborative usage or multiple views into the same data.

- **🧪 Notebook Integration**
  - Call `bvista.show(df)` to launch the B-vista interface directly inside Jupyter or Colab.

- **📂 File Handling**
  - Upload CSVs or interactively manage DataFrames without restarting your Python session.

- **🌐 Web-based UI**
  - Full React-based interface with tabs, sidebar navigation, dynamic tables, and customizable themes.

<!-- Placeholder for static feature screenshots -->
<!-- ![Feature: correlation](docs/assets/feature-correlation.png) -->
<!-- ![Feature: missing data](docs/assets/feature-missing.png) -->
<!-- ![Feature: interactive cleaning](docs/assets/feature-cleaning.png) -->
