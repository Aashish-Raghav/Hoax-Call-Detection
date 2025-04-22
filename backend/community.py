import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain
import matplotlib.pyplot as plt


def get_time_slot(timestamp):
    """Categorize time of day based on hour."""
    if pd.isnull(timestamp):
        return "Unknown"
    hour = timestamp.hour
    if 0 <= hour < 6:
        return "Late Night"
    elif 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    else:
        return "Evening"


def detect_location_communities(df):
    """Detect communities per location using Louvain method."""
    communities = {}
    for location in df["Location"].unique():
        sub_df = df[df["Location"] == location]
        sub_G = nx.DiGraph()

        for _, row in sub_df.iterrows():
            sub_G.add_edge(row["Caller_ID"], row["Receiver_ID"], weight=1)

        if len(sub_G.nodes) > 1:
            partition = community_louvain.best_partition(nx.Graph(sub_G))
            communities[location] = partition
            print(f"{location}: {len(set(partition.values()))} communities detected.")
    return communities


def detect_time_location_communities(df):
    """Detect communities grouped by both time slot and location."""
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
    df["Time_Slot"] = df["Timestamp"].apply(get_time_slot)

    combined_communities = {}
    for _, row in df.iterrows():
        key = (row["Time_Slot"], row["Location"])
        caller, receiver = row["Caller_ID"], row["Receiver_ID"]

        if key not in combined_communities:
            combined_communities[key] = nx.DiGraph()

        combined_communities[key].add_edge(caller, receiver, weight=1)

    result = {}
    for key, sub_G in combined_communities.items():
        if len(sub_G.nodes) > 1:
            partition = community_louvain.best_partition(nx.Graph(sub_G))
            result[key] = partition
            print(f"{key}: {len(set(partition.values()))} communities detected.")
    return result


def extract_community_nodes(partition, community_id):
    """Return list of nodes belonging to a specific community ID."""
    return [node for node, comm in partition.items() if comm == community_id]


def visualize_selected_communities(df, selected_community_ids):
    """
    Visualize specific communities by IDs (e.g., [2, 3, 6]).
    """
    G = nx.DiGraph()

    for _, row in df.iterrows():
        G.add_edge(row["Caller_ID"], row["Receiver_ID"], weight=1)

    if len(G.nodes) <= 1:
        print("⚠️ Not enough data to form a graph.")
        return

    partition = community_louvain.best_partition(nx.Graph(G))

    selected_nodes = [node for node, comm in partition.items() if comm in selected_community_ids]

    if not selected_nodes:
        print(f"⚠️ Selected communities {selected_community_ids} do not exist.")
        return

    sub_G = G.subgraph(selected_nodes)
    node_colors = [partition[node] for node in sub_G.nodes()]

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(sub_G, seed=42)
    nx.draw(sub_G, pos, with_labels=True, node_size=300, cmap=plt.cm.Set1,
            node_color=node_colors, edge_color="gray", font_size=6)
    plt.title(f"Visualization of Communities {selected_community_ids}")
    plt.show()
