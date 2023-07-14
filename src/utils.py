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
        prerequisites = row['Prerequisites']
        units = row['Units']
        prerequisites_list = [] if pd.isnull(prerequisites) else prerequisites.split('+')
        course_dict[course_id] = (title, prerequisites_list, units)

    return course_dict


def prereq_adjlist(course_dict: dict) -> dict:
    adj_list = {}

    for course_id, (_, prerequisites_list, _) in course_dict.items():
        adj_list[course_id] = prerequisites_list

    return adj_list


def create_dag(course_dict: dict) -> dict:
    dag = {}

    for course_id, (_, prerequisites_list, _) in course_dict.items():
        dag[course_id] = []
        for prereq in prerequisites_list:
            dag[prereq].append(course_id)

    return dag


def create_mult_dag(adjacency_list: dict) -> list:
    def label_levels(adj_list: dict) -> dict:
        levels = {}
        visited = set()
        queue = deque()

        start_node = next(iter(adj_list.keys()))
        queue.append((start_node, 0))  # Add the start node with level 0
        visited.add(start_node)
        levels[start_node] = 0

        while queue:
            node, level = queue.popleft()
            
            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    queue.append((neighbor, level + 1))
                    visited.add(neighbor)
                    levels[neighbor] = level + 1

        return levels
    
    mult_dag = []
    al_copy = adjacency_list.copy()

    for i, (k, v) in enumerate(adjacency_list.items()):
        mult_dag.append(label_levels(al_copy))
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
    def dfs(course):
        visited.add(course)
        for prerequisite in dag[course]:
            if prerequisite not in visited:
                dfs(prerequisite)
        topological_order.append(course)

    visited = set()
    topological_order = []

    for course in dag:
        if course not in visited:
            dfs(course)

    topological_order.reverse()
    return topological_order