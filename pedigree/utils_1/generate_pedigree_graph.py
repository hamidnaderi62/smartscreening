import graphviz
from pedigree.models import Individual


def generate_pedigree_graph(family_id):
    individuals = Individual.objects.filter(family_id=family_id)

    dot = graphviz.Digraph(format='svg')

    for ind in individuals:
        # Customize shape and color based on gender and affected status
        shape = 'square' if ind.gender == 'M' else 'circle'
        color = 'red' if ind.affected else 'black'

        dot.node(str(ind.id), ind.name, shape=shape, color=color)

        # Add edges for parent-child relationships
        if ind.mother:
            dot.edge(str(ind.mother.id), str(ind.id))
        if ind.father:
            dot.edge(str(ind.father.id), str(ind.id))

    return dot