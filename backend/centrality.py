import networkx as nx

def compute_centrality(G):
    return {
        'in_degree': nx.in_degree_centrality(G),
        'out_degree': nx.out_degree_centrality(G),
        'betweenness': nx.betweenness_centrality(G),
        'closeness': nx.closeness_centrality(G),
        'eigenvector': nx.eigenvector_centrality(G, max_iter=1000)
    }
