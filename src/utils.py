import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

def read_csv_to_dict(path: str) -> dict:
    df = pd.read_csv(path)
    course_dict = {}

    for _, row in df.iterrows():
        course_id = row['CoursesID']
        title = row['Title']
        prereq = row['Prerequisites']
        units = row['Units']
        prereq_list = [] if pd.isnull(prereq) else prereq.split('+')
        course_dict[course_id] = (title, prereq_list, units)

    return course_dict


def prereq_dag(course_dict: dict) -> dict:
    return {k: l for k, (_, l, _) in course_dict.items()}


def forward_dag(course_dict: dict) -> dict:
    dag = {}
    
    for cid, (_, prereqs, _) in course_dict.items():
        dag.setdefault(cid, [])
        for p in prereqs:
            dag.setdefault(p, [])
            dag[p].append(cid)

    return dag


def dag_leveler(adjacency_list: dict) -> list:
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
    al_copy = adjacency_list.copy()

    for i, (k, v) in enumerate(adjacency_list.items()):
        mult_dag.append(bfs(al_copy))
        al_copy.pop(k)
        al_copy[k] = v
        if i > len(adjacency_list):
            break
    mult_dag = [dag for dag in mult_dag if len(dag) > 1]

    return mult_dag


def graph_relationship(dag: dict) -> None:
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
            'lightblue' if node[:4] == 'COMP' else 'lightgreen' if node[:4] == 'IN4M' else 'lightcoral' for node in G.nodes()],
        node_size=1000
    )
    plt.show()


def topological_sort(dag: dict) -> list:
    def dfs(course: str) -> None:
        visited.add(course)
        for prereq in dag[course]:
            if prereq not in visited:
                dfs(prereq)
        topo_order.append(course)

    visited = set()
    topo_order = []

    for course in dag:
        if course not in visited:
            dfs(course)

    topo_order.reverse()
    return topo_order


def combine_dags(mult_dag: list) -> list:
    # # Remove duplicate DAGs
    # smallest_dag_idx = [
    #     i for i, dag in enumerate(mult_dag) 
    #     if len(dag) == min(len(d) for d in mult_dag)
    # ]
    
    # for idx in reversed(smallest_dag_idx):
    #     for i, dag in enumerate(mult_dag):
    #         if i == idx:
    #             continue
    #         intersect = list(set(dag).intersection(mult_dag[idx]))
    #         intersect.sort()

    #         if intersect == list(mult_dag[idx].keys()):
    #             mult_dag.pop(idx)
    #             break

    ## Remove duplicate DAGs IMPROVED
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




test = [
    {'I&C SCI 6B': 0, 'COMPSCI 161': 1, 'COMPSCI 165': 2},
    {'I&C SCI 6D': 0, 'COMPSCI 161': 1, 'COMPSCI 165': 2},
    {'STATS 67': 0, 'COMPSCI 132': 1, 'IN4MATX 124': 2},
    {'COMPSCI 132': 0, 'IN4MATX 124': 1},
    {'COMPSCI 161': 0, 'COMPSCI 165': 1},
    {'IN4MATX 43': 0, 'IN4MATX 113': 1, 'IN4MATX 115': 1, 'IN4MATX 151': 1, 'IN4MATX 191A': 2, 'IN4MATX 191B': 3},
    {'IN4MATX 101': 0, 'IN4MATX 102': 1, 'IN4MATX 122': 1},
    {'IN4MATX 113': 0, 'IN4MATX 191A': 1, 'IN4MATX 191B': 2},
    {'IN4MATX 121': 0, 'IN4MATX 191A': 1, 'IN4MATX 191B': 2},
    {'IN4MATX 131': 0, 'IN4MATX 191A': 1, 'IN4MATX 191B': 2},
    {'IN4MATX 151': 0, 'IN4MATX 191A': 1, 'IN4MATX 191B': 2},
    {'IN4MATX 191A': 0, 'IN4MATX 191B': 1}
]

l = combine_dags(test)
for i in l:
    print(i)
