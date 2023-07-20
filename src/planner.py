import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from dataclasses import dataclass


@dataclass
class CoursePlanner:
    planned_years: int
    semesters_per_year: int
    max_units_per_semester: int
    data_path: str
    _cdict: dict = None
    _pdag: dict = None
    _fdag: dict = None

    @property
    def course_dict(self) -> dict:
        return self._cdict
    
    @property
    def prereq_dag(self) -> dict:
        return self._pdag
    
    @property
    def forward_dag(self) -> dict:
        return self._fdag

    def __post_init__(self):
        self._cdict = self.__read_csv_to_dict()
        self._pdag = self.__build_pdag(self._cdict)
        self._fdag = self.__build_fdag(self._cdict)

    def __read_csv_to_dict(self) -> dict:
        df = pd.read_csv(self.data_path)
        course_dict = {}

        for _, row in df.iterrows():
            course_id = row['CoursesID']
            title = row['Title']
            prereq = row['Prerequisites']
            units = row['Units']
            prereq_list = [] if pd.isnull(prereq) else prereq.split('+')
            course_dict[course_id] = (title, prereq_list, units)

        return course_dict


    def __build_pdag(self, course_dict: dict) -> dict:
        return {k: l for k, (_, l, _) in course_dict.items()}


    def __build_fdag(self, course_dict: dict) -> dict:
        dag = {}
        
        for cid, (_, prereqs, _) in course_dict.items():
            dag.setdefault(cid, [])
            for p in prereqs:
                dag.setdefault(p, [])
                dag[p].append(cid)

        return dag
    
    def topological_sort(self, dag: dict) -> dict:
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


    def dag_leveler(self) -> list:
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
        al_copy = self._fdag.copy()

        for i, (k, v) in enumerate(self._fdag.items()):
            mult_dag.append(bfs(al_copy))
            al_copy.pop(k)
            al_copy[k] = v
            if i > len(self._fdag):
                break
        mult_dag = [dag for dag in mult_dag if len(dag) > 1]

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


    def graph_relationship(self) -> None:
        dag = self.topological_sort(self._pdag)

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


