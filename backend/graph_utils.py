import networkx as nx
import pandas as pd

def create_graph(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        caller = row["Caller_ID"]
        receiver = row["Receiver_ID"]
        call_type = row["Call_Type"]

        G.add_node(caller, location=row["Location"])
        G.add_node(receiver, location=row["Location"])

        if call_type == "Outgoing":
            G.add_edge(caller, receiver, duration=row["Duration"])
        else:
            G.add_edge(receiver, caller, duration=row["Duration"])
    return G
