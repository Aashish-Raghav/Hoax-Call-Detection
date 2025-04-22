import pandas as pd
import networkx as nx
from sklearn.preprocessing import MinMaxScaler


def compute_centralities(G):
    """
    Compute out-degree, betweenness, and PageRank centrality measures.
    """
    out_degree = nx.out_degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, normalized=True, weight='weight')
    pagerank = nx.pagerank(G, alpha=0.85, weight='weight')

    return out_degree, betweenness, pagerank


def build_risk_dataframe(G, out_degree, betweenness, pagerank):
    """
    Normalize metrics and compute a composite risk score.
    """
    scaler = MinMaxScaler()

    df = pd.DataFrame({
        'Node': list(G.nodes()),
        'Out_Degree': [out_degree.get(node, 0) for node in G.nodes()],
        'Betweenness': [betweenness.get(node, 0) for node in G.nodes()],
        'PageRank': [pagerank.get(node, 0) for node in G.nodes()]
    })

    # Normalize centrality scores
    df[['Out_Degree', 'Betweenness', 'PageRank']] = scaler.fit_transform(
        df[['Out_Degree', 'Betweenness', 'PageRank']]
    )

    # Weighted composite risk score
    df['Risk_Score'] = (
        0.4 * df['PageRank'] +
        0.35 * df['Betweenness'] +
        0.25 * df['Out_Degree']
    )

    # Label high-risk nodes (top 5%)
    threshold = df['Risk_Score'].quantile(0.95)
    df['Risk_Label'] = df['Risk_Score'].apply(lambda x: 'High-Risk' if x >= threshold else 'Normal')

    return df


def analyze_risk(df):
    """
    High-level wrapper to create graph from dataframe and compute risk analysis.
    """
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['Caller_ID'], row['Receiver_ID'], weight=1)

    out_deg, btw, pr = compute_centralities(G)
    risk_df = build_risk_dataframe(G, out_deg, btw, pr)

    return risk_df.sort_values("Risk_Score", ascending=False)
