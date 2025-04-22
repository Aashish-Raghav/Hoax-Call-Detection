import streamlit as st
import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Backend imports
from backend.community import (
    detect_location_communities,
    detect_time_location_communities,
    extract_community_nodes,
)
from backend.graph_utils import create_graph
from backend.centrality import compute_centrality
from backend.pagerank import compute_pagerank
from backend.risk_analysis import (
    analyze_risk,
    build_risk_dataframe,
    compute_centralities
)
from backend.visualizations import (
    visualize_risk_heatmap,
    visualize_selected_communities,
    visualize_top_high_risk_nodes,
    visualize_full_network
)

# --- App UI ---
st.set_page_config(layout="wide", page_title="Hoax Call Network Analyzer")
st.title("📞 Hoax Call Network Analyzer Dashboard")

uploaded_file = st.file_uploader("Upload Hoax Call CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Data uploaded successfully!")

    # Create base graph
    G = create_graph(df)

    st.sidebar.title("🔍 Select Analysis Section")
    section = st.sidebar.radio("Choose a section:", [
        "Centrality & PageRank",
        "Community Detection",
        "Risk Analysis",
        "Visualizations"
    ])

    if section == "Centrality & PageRank":
        st.header("📊 Centrality & PageRank Scores")
        centrality = compute_centrality(G)
        pagerank = compute_pagerank(G)

        st.dataframe(pd.DataFrame({
            "Node": list(centrality.keys()),
            "Out-Degree": list(centrality.values()),
            "PageRank": [pagerank.get(node, 0) for node in centrality.keys()]
        }).sort_values("PageRank", ascending=False).head(10))

    elif section == "Community Detection":
        st.header("👥 Community Detection")
        community_option = st.selectbox("Community Mode", ["By Location", "By Time + Location"])

        if community_option == "By Location":
            partitions = detect_location_communities(df)
        else:
            partitions = detect_time_location_communities(df)

        st.write("🧠 Communities Detected (sorted by size):")

        if not partitions:
            st.warning("⚠️ No community data available.")
        else:
            community_sizes = {}
            for key, partition in partitions.items():
                community_sizes[key] = len(set(partition.values()))
            
            # Sort communities by size descending
            sorted_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)
            for key, size in sorted_communities:
                st.markdown(f"**{key}** - {size} communities")
    
                
    elif section == "Risk Analysis":
        st.header("🚨 Risk Analysis")
        centrality_df = analyze_risk(df)

        st.write("Top High-Risk Nodes:")
        st.dataframe(centrality_df[centrality_df["Risk_Label"] == "High-Risk"].sort_values("Risk_Score", ascending=False).head(10))

    elif section == "Visualizations":
        st.header("📈 Visualizations")
        centrality_df = analyze_risk(df)

        vis_option = st.selectbox("Choose Visualization Type", [
            "Full Network Graph","Risk Score Heatmap", "Top High-Risk Nodes", "Communities (select manually)"
        ])

        if vis_option == "Risk Score Heatmap":
            visualize_risk_heatmap(G, centrality_df)
        elif vis_option == "Full Network Graph":
            show_labels = st.checkbox("Show Node Labels", value=False)
            visualize_full_network(G, show_labels=show_labels)

        elif vis_option == "Top High-Risk Nodes":
            top_n = st.slider("Number of nodes to visualize", 5, 20, 10)
            visualize_top_high_risk_nodes(G, centrality_df, top_n=top_n)

        elif vis_option == "Communities (select manually)":
            partition = detect_location_communities(df)["All"]  # Adjust this based on your structure
            selected_comms = st.multiselect("Select community IDs", list(set(partition.values())), default=[0, 1])
            if selected_comms:
                visualize_selected_communities(G, partition, selected_comms)
