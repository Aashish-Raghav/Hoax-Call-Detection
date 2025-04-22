# 📞 Hoax Call Detection in Social Network Graphs

A powerful Streamlit-based dashboard to analyze suspicious calling patterns using graph theory, community detection, and centrality-based risk scoring.

---

## 🔍 Project Overview

This project analyzes a dataset of hoax calls and visualizes the calling network as a graph. Using **NetworkX**, **Louvain community detection**, and **centrality metrics**, the system identifies:

- 📊 Influential nodes  
- 🧠 Communities within the call network  
- 🚨 High-risk callers (based on composite centrality)  
- 🌐 Heatmaps & visualizations of call behavior

---

## 🗂️ Project Structure
```text
hoax_call_detection/
│
├── frontend/
│   └── app.py               # CLI or Streamlit/Gradio interface
│
├── backend/
│   ├── __init__.py
│   ├── graph_utils.py       # Graph creation and adjacency matrix
│   ├── centrality.py        # Centrality metrics
│   ├── pagerank.py          # PageRank computation
│   ├── community.py         # Louvain method community detection
│   ├── risk_analysis.py     # Risk scoring based on centralities
│   └── visualizations.py    # Graph plots and heatmaps
│
├── data/
│   └── hoax_call_data.csv
│
└── requirements.txt
```


---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/hoax_call_detection.git
cd hoax_call_detection
```
### 2. Clone the repository
```bash
pip install -r requirements.txt
```
### 3. Run the Streamlit app
```bash
streamlit run frontend/app.py
```

## 📈 Features

- **Graph Building**: Converts call logs into a directed network.
- **Community Detection**: Uses Louvain method to identify clusters.
- **Centrality & PageRank**: Computes betweenness, out-degree, and influence scores.
- **Risk Scoring**: Combines multiple metrics into a composite risk level.
- **Interactive Visualizations**: Choose from heatmaps, top high-risk nodes, and community graphs.

---

## 📌 Dependencies

- Streamlit  
- Pandas  
- NetworkX  
- Matplotlib  
- Scikit-learn  
- Python-Louvain  

---

## 📬 Dataset Format (`hoax_call_data.csv`)

| Caller_ID | Receiver_ID | Timestamp           | Location        |
|-----------|-------------|---------------------|------------------|
| A123      | B456        | 2023-04-10 14:23:00 | New York         |
| C789      | A123        | 2023-04-10 15:45:00 | San Francisco    |

---

