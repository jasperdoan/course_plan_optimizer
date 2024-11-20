import networkx as nx
import streamlit as st
from typing import Type
from collections import deque
from functools import lru_cache
from src.scraper import scape_read_csv
from src.planner import CoursePlanner



@st.cache_data
def load_availability(path: str) -> dict:
    return scape_read_csv(path)


@st.cache_data
def topological_sort(dag: dict) -> dict:
    @lru_cache(maxsize=10)
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


@st.cache_resource
def plot_dag(pdag: dict):
    dag = topological_sort(pdag)
    G = nx.Graph()

    G.add_nodes_from(dag.keys())
    for n, edges in dag.items():
        for e in edges:
            G.add_edge(n, e)
    layout_options = {'k': .5, 'iterations': 50}
    pos = nx.spring_layout(G, **layout_options)

    nx.draw(G, pos, 
        with_labels=True, 
        font_size=5.5, 
        arrows=True, 
        arrowstyle='->', 
        arrowsize=12, 
        node_color=[
            'lightblue' if node[:2] == 'CS' else 
            'lightgreen' if node[:3] == 'INF' else 
            'lightcoral' for node in G.nodes()
        ],
        node_size=750
    )
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()


@st.cache_data
def update_plot_dag(plan: Type[CoursePlanner]) -> None:
    try:
        pdag = plan.prereq_dag.copy()
        for course in plan.completed_courses:
            pdag.pop(course)
            for k, v in pdag.items():
                if course in v:
                    pdag[k].remove(course)
        plot_dag(pdag)
    except:
        st.warning('Slow down - Add one course at a time', icon="⚠️")


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
