import streamlit as st
import pandas as pd
import sys
import os
import networkx as nx

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Backend imports
from backend.community import (
    detect_location_communities,
    detect_time_location_communities
)
from backend.graph_utils import create_graph
from backend.centrality import compute_centrality
from backend.pagerank import compute_pagerank
from backend.sentiment import analyze_sentiment
from backend.risk_analysis import analyze_risk

from backend.visualizations import (
    visualize_risk_heatmap,
    visualize_selected_communities,
    visualize_top_high_risk_nodes,
    visualize_full_network,
    visualize_sentiments
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
        "Centrality",
        "PageRank",
        "Community Detection",
        "Risk Analysis",
        "Visualizations",
        "Sentiments Analysis",
    ])

    if section == "Centrality":
        st.header("📊 Centrality Scores")

        centrality_option = st.selectbox(
            "Choose Centrality Measure",
            ["In-Degree", "Out-Degree", "Closeness", "Betweenness", "Eigenvector"]
        )

        top_n = st.slider("Number of top nodes to display", min_value=5, max_value=20, value=10)
        with st.spinner("Processing... Please wait."):
            centrality = compute_centrality(G)

        # Compute centrality based on user selection
        if centrality_option == "In-Degree":
            centrality_scores = centrality['in_degree']
        elif centrality_option == "Out-Degree":
            centrality_scores = centrality['out_degree']
        elif centrality_option == "Closeness":
            centrality_scores = centrality['closeness']
        elif centrality_option == "Betweenness":
            centrality_scores = centrality['betweenness']
        elif centrality_option == "Eigenvector":
            try:
                centrality_scores = centrality['eigenvector']
            except Exception:
                st.error("Eigenvector centrality failed to converge. Try a different measure.")
                centrality_scores = {}

        if centrality_scores:
            sorted_scores = sorted(centrality_scores.items(), key=lambda x: x[1], reverse=True)
            st.dataframe(pd.DataFrame(sorted_scores[:top_n], columns=["Node", f"{centrality_option} Score"]))

    elif section == "PageRank":
        st.header("🔗 PageRank Scores")

        with st.spinner("Processing... Please wait."):
            pagerank_scores = compute_pagerank(G)
        top_n = st.slider("Number of top nodes to display", min_value=5, max_value=20, value=10, key="pagerank_slider")

        sorted_pr = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        st.dataframe(pd.DataFrame(sorted_pr[:top_n], columns=["Node", "PageRank Score"]))


    elif section == "Community Detection":
        st.header("👥 Community Detection")
        community_option = st.selectbox("Community Mode", ["By Location", "By Time + Location"])

        with st.spinner("Processing... Please wait."):
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
        with st.spinner("Processing... Please wait."):
            centrality_df = analyze_risk(df)

        st.subheader("Top High-Risk Nodes (📊 Normalized Scores)")
        st.caption("Note: All scores including Degree, Betweenness, and PageRank are normalized between 0 and 1.")

        top_risk_df = centrality_df[centrality_df["Risk_Label"] == "High-Risk"].sort_values("Risk_Score", ascending=False).head(10)
        st.dataframe(top_risk_df)

    elif section == "Visualizations":
        st.header("📈 Visualizations")

        vis_option = st.selectbox("Choose Visualization Type", [
            "Full Network Graph","Risk Score Heatmap", "Top High-Risk Nodes", "Communities (select manually)"
        ])

        if vis_option == "Risk Score Heatmap":
            with st.spinner("Processing... Please wait."):
                centrality_df = analyze_risk(df)
            with st.spinner("Generating visualization..."):
                visualize_risk_heatmap(G, centrality_df)
        elif vis_option == "Full Network Graph":
            show_labels = st.checkbox("Show Node Labels", value=False)
            with st.spinner("Generating visualization..."):
                visualize_full_network(G, show_labels=show_labels)

        elif vis_option == "Top High-Risk Nodes":
            with st.spinner("Processing... Please wait."):
                centrality_df = analyze_risk(df)
            top_n = st.slider("Number of nodes to visualize", 5, 20, 10)
            with st.spinner("Generating visualization..."):
                visualize_top_high_risk_nodes(G, centrality_df, top_n=top_n)

        elif vis_option == "Communities (select manually)":
            st.subheader("🔍 Community Visualization by Node Selection")

            # Step 1: Select a location (since communities are divided per location)
            locations = df["Location"].unique()
            selected_location = st.selectbox("Select a Location", locations)

            if selected_location:
                location_partitions = detect_location_communities(df)
                partition = location_partitions[selected_location]

                all_nodes = list(partition.keys())
                selected_nodes = st.multiselect("Select Node(s) to visualize their community", all_nodes)

                if selected_nodes:
                    # Step 2: Get community IDs for selected nodes
                    selected_community_ids = set(partition[node] for node in selected_nodes)

                    st.info(f"Visualizing community(s): {', '.join(map(str, selected_community_ids))}")

                    # Step 3: Build full graph for this location
                    sub_df = df[df["Location"] == selected_location]
                    G_location = nx.DiGraph()
                    for _, row in sub_df.iterrows():
                        G_location.add_edge(row["Caller_ID"], row["Receiver_ID"], weight=1)

                    # Step 4: Visualize selected communities
                    with st.spinner("Generating visualization..."):
                        visualize_selected_communities(G_location, partition, selected_community_ids)

    elif section == "Sentiments Analysis":
        st.header("Sentiments Analysis")

        with st.spinner("Processing... Please wait."):
            df, top_dangerous_nodes = analyze_sentiment(df)

        with st.spinner("Generating visualization..."):
            visualize_sentiments(df)

        # User selects how many top dangerous texts to view
        top_n = st.slider("Select number of most dangerous calls to view", min_value=5, max_value=20, value=5)

        st.subheader(f"Top {top_n} Most Dangerous Call Texts")
        st.caption("Ranked by most negative sentiment polarity (potential hoax indicators).")

        # Display selected number of top dangerous calls in a table
        top_df = pd.DataFrame(top_dangerous_nodes[:top_n], columns=["Polarity Score", "Caller ID", "Call Text"])
        st.dataframe(top_df[["Caller ID", "Polarity Score"]].style.format({"Polarity Score": "{:.3f}"}))

        # Optional expander for call text preview
        with st.expander("🔍 View Call Texts of These Calls"):
            for score, caller, text in top_dangerous_nodes[:top_n]:
                st.markdown(f"""
                Caller ID: `{caller}`  
                Polarity Score: `{score:.3f}`  
                Call Text: _{text}_  
                """)

