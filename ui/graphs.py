import networkx as nx
import plotly.graph_objects as go

def network_figure(graph, members, height=500, color="#d85a65"):
    subgraph = graph.subgraph(members)
    position = nx.spring_layout(subgraph, seed=42)

    edge_x, edge_y = [], []
    for u, v in subgraph.edges():
        edge_x.extend([position[u][0], position[v][0], None])
        edge_y.extend([position[u][1], position[v][1], None])

    node_x = [position[n][0] for n in subgraph.nodes()]
    node_y = [position[n][1] for n in subgraph.nodes()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1, color="#414852"), hoverinfo="none"
    ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers",
        text=list(subgraph.nodes()), hoverinfo="text",
        marker=dict(size=16, color=color, line=dict(width=1, color="#dfe3e8"))
    ))
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

def replay_figure(graph, members, active_nodes, height=500):
    full = graph.subgraph(members)
    active = graph.subgraph(active_nodes)
    position = nx.spring_layout(full, seed=42)

    edge_x, edge_y = [], []
    for u, v in active.edges():
        edge_x.extend([position[u][0], position[v][0], None])
        edge_y.extend([position[u][1], position[v][1], None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1, color="#414852"), hoverinfo="none"
    ))

    if active_nodes:
        fig.add_trace(go.Scatter(
            x=[position[n][0] for n in active_nodes],
            y=[position[n][1] for n in active_nodes],
            mode="markers",
            text=active_nodes, hoverinfo="text",
            marker=dict(size=16, color="#d85a65", line=dict(width=1, color="#dfe3e8"))
        ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

def precision_recall_figure(metrics):
    thresholds, precisions, recalls = metrics["curve"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recalls, y=precisions, mode="lines",
        line=dict(width=2.2, color="#8aaed1"),
        hovertemplate="Recall %{x:.2f}<br>Precision %{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[metrics["recall"]], y=[metrics["precision"]], mode="markers",
        marker=dict(size=10, color="#d85a65", line=dict(width=1.5, color="#e6e9ed")),
        hovertemplate="Selected operating point<extra></extra>",
    ))
    fig.update_layout(
        height=460,
        margin=dict(l=55, r=20, t=15, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(title="Recall", range=[0, 1.02], gridcolor="#292f38"),
        yaxis=dict(title="Precision", range=[0, 1.02], gridcolor="#292f38"),
    )
    return fig
