import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

import streamlit as st

def visualize_full_network(G, title="Complete Hoax Call Network", show_labels=False):
    """
    Visualizes the entire network graph.
    
    Args:
        G (networkx.Graph): The full graph to visualize.
        title (str): Title of the plot.
        show_labels (bool): Whether to show node labels.
    """
    if G.number_of_nodes() == 0:
        st.warning("The graph is empty. Cannot display visualization.")
        return

    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.3, seed=42)  # Layout positioning

    nx.draw_networkx_nodes(G, pos, node_size=80, node_color="skyblue", ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color="gray", ax=ax)

    if show_labels:
        nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)

    ax.set_title(title, fontsize=16)
    ax.axis("off")
    st.pyplot(fig)
    plt.clf()


def visualize_risk_heatmap(G, centrality_df, title="Influence Heatmap of Hoax Call Network"):
    influence = centrality_df.set_index('Node')['Risk_Score'].to_dict()
    node_colors = [influence.get(node, 0) for node in G.nodes()]

    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.3, seed=42)

    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.plasma, node_size=100, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color="gray", ax=ax)

    cbar = fig.colorbar(nodes, ax=ax)
    cbar.set_label('Risk Score / Influence Level')

    ax.set_title(title, fontsize=15)
    ax.axis("off")
    st.pyplot(fig)
    plt.clf()


def visualize_selected_communities(G, partition, selected_communities):
    selected_nodes = [node for node, comm in partition.items() if comm in selected_communities]

    if not selected_nodes:
        st.warning(f"⚠️ Selected communities {selected_communities} do not exist in this graph.")
        return

    sub_G = G.subgraph(selected_nodes)
    node_colors = [partition[node] for node in sub_G.nodes()]

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(sub_G, seed=42)
    nx.draw(sub_G, pos, with_labels=True, node_size=300, cmap=plt.cm.Set1,
            node_color=node_colors, edge_color="gray", font_size=6)

    plt.title(f"Visualization of Communities {selected_communities}")
    plt.axis("off")
    plt.tight_layout()
    st.pyplot(plt.gcf())  # ✅ Key line


def visualize_top_high_risk_nodes(G, centrality_df, top_n=10):
    high_risk_nodes = centrality_df.sort_values('Risk_Score', ascending=False).head(top_n)['Node'].tolist()

    sub_G = G.subgraph(high_risk_nodes)
    risk_scores_dict = centrality_df.set_index("Node")["Risk_Score"].to_dict()

    # Get node colors in the exact order of sub_G.nodes
    node_colors = [risk_scores_dict.get(node, 0) for node in sub_G.nodes()]

    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(sub_G, seed=21)
    nodes = nx.draw_networkx_nodes(sub_G, pos, node_color=node_colors, cmap=plt.cm.viridis, node_size=400)
    nx.draw_networkx_edges(sub_G, pos, edge_color="gray", alpha=0.5)
    nx.draw_networkx_labels(sub_G, pos, font_size=8)

    plt.colorbar(nodes, label='Risk Score')
    plt.title(f"Top {top_n} High-Risk Nodes")
    plt.axis("off")
    plt.tight_layout()
    st.pyplot(plt.gcf())

