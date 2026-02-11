import plotly.graph_objects as go
from pedigree.models import Individual


def create_interactive_pedigree(family_id):
    individuals = Individual.objects.filter(family_id=family_id)

    # Create a network graph
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []
    node_text = []

    # Position nodes (this is a simplified approach)
    for i, ind in enumerate(individuals):
        node_x.append(i % 5)  # Simple grid positioning
        node_y.append(i // 5)
        node_text.append(f"{ind.name}<br>{'Affected' if ind.affected else ''}")

        if ind.mother:
            edge_x.extend([i % 5, ind.mother.id % 5, None])
            edge_y.extend([i // 5, ind.mother.id // 5, None])
        if ind.father:
            edge_x.extend([i % 5, ind.father.id % 5, None])
            edge_y.extend([i // 5, ind.father.id // 5, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        marker=dict(
            size=20,
            color=['red' if ind.affected else 'blue' for ind in individuals],
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    return fig.to_html(full_html=False)




from graphviz import Digraph
from pedigree.models import Individual


def generate_pedigree_graph(family_id):
    individuals = Individual.objects.filter(family_id=family_id)
    dot = Digraph(format='svg')

    for ind in individuals:
        shape = 'square' if ind.gender == 'M' else 'circle'
        color = 'red' if ind.affected else 'black'
        dot.node(str(ind.id), ind.name, shape=shape, color=color)

        if ind.mother:
            dot.edge(str(ind.mother.id), str(ind.id))
        if ind.father:
            dot.edge(str(ind.father.id), str(ind.id))

    return dot