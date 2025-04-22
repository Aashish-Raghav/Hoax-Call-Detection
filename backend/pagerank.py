import networkx as nx

def compute_pagerank(G, alpha=0.85):
    return nx.pagerank(G, alpha=alpha)
