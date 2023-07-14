import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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


def prereq_tree(course_dict: dict) -> dict:
    adj_list = {}

    for course_id, (_, prerequisites_list, _) in course_dict.items():
        adj_list[course_id] = prerequisites_list

    return adj_list


def course_option_tree(adj_list: dict) -> dict:
    course_tree = adj_list.copy()        

    for course, prereq_list in adj_list.items():
        course_tree[course] = []
        for prereq in prereq_list:
            course_tree[prereq].append(course)
        
    return course_tree


def graph_prereq_relationship(adj_list: dict) -> None:
    G = nx.Graph()

    G.add_nodes_from(adj_list.keys())

    for node, prerequisites_list in adj_list.items():
        for prerequisite in prerequisites_list:
            G.add_edge(node, prerequisite)

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


def topological_sort(adj_list):
    graph = nx.DiGraph(adj_list)
    sorted_classes = list(nx.topological_sort(graph))
    return sorted_classes