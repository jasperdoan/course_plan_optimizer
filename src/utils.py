import networkx as nx
import matplotlib.pyplot as plt
from collections import deque


def display_info(course_dict: dict, avail_dict: dict) -> None:
    print('All Courses:\n', '-'*100)
    for course, (title, preq, units) in course_dict.items():
        print(f'{course}: {title} ({units} units)')
        print(f'\tPrerequisites: {preq}')
        print(f'\tAvailability: {avail_dict[course] if course in avail_dict else []}')
        print('-'*75)


def display_dag(dag: dict) -> None:
    for k, v in dag.items():
        print(f'{k}: {v}')


def topological_sort(dag: dict) -> dict:
    def dfs(course: str) -> None:
        visited.add(course)
        for prereq in dag[course]:
            if prereq not in visited:
                dfs(prereq)
        topo_order[course] = dag[course]

    visited = set()
    topo_order = {}

    for course in dag:
        if course not in visited:
            dfs(course)

    return topo_order


def graph_relationship(pdag: dict) -> None:
    dag = topological_sort(pdag)

    G = nx.Graph()
    G.add_nodes_from(dag.keys())

    for n, edges in dag.items():
        for e in edges:
            G.add_edge(n, e)

    # Set node spacing options
    layout_options = {'k': .5, 'iterations': 50}

    # Draw the graph with customizations
    pos = nx.spring_layout(G, **layout_options)
    nx.draw(G, pos, 
        with_labels=True, 
        font_size=7.5, 
        arrows=True, 
        arrowstyle='->', 
        arrowsize=15, 
        node_color=[
            'lightblue' if node[:2] == 'CS' else 'lightgreen' if node[:3] == 'INF' else 'lightcoral' for node in G.nodes()],
        node_size=1000
    )
    plt.show()


def dag_leveler(dag) -> list:
    def bfs(adj_list: dict) -> dict:
        levels = {}
        visited = set()
        q = deque()

        snode = next(iter(adj_list.keys()))
        q.append((snode, 0))  # Add the start node with level 0
        visited.add(snode)
        levels[snode] = 0

        while q:
            node, i = q.popleft()
            for n in adj_list[node]:
                if n not in visited:
                    q.append((n, i + 1))
                    visited.add(n)
                    levels[n] = i + 1
                    
        return levels
    
    mult_dag = []
    al_copy = dag.copy()

    for i, (k, v) in enumerate(dag.items()):
        mult_dag.append(bfs(al_copy))
        al_copy.pop(k)
        al_copy[k] = v
        if i > len(dag):
            break

    idxs = []
    for i, d1 in enumerate(mult_dag):
        for j, d2 in enumerate(mult_dag):
            if i == j:
                continue
            
            if set(d1.keys()).issubset(set(d2.keys())):
                idxs.append(i)
                break

    for idx in reversed(idxs):
        mult_dag.pop(idx)

    return mult_dag