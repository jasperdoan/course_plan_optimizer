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


def level_order_traversal(adj_list: dict) -> list:
    dags = []
    visited = set()

    def bfs(course):
        dag = {}
        queue = deque([(course, 0)])

        while queue:
            current, level = queue.popleft()

            if current not in dag:
                dag[current] = level
            visited.add(current)

            for prerequisite in adj_list[current]:
                if prerequisite not in visited:
                    queue.append((prerequisite, level + 1))

        return dag

    for course in adj_list:
        if course not in visited:
            dag = bfs(course)
            dags.append(dag)

    return dags


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