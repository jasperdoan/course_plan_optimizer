import pandas as pd
from dataclasses import dataclass
from typing import Callable


@dataclass
class CoursePlanner:
    data_path: str
    planned_years: int
    max_units_per_sem: int
    completed_courses: list = None
    sessions: list = None
    _cdict: dict = None
    _pdag: dict = None
    _fdag: dict = None
    _session_val: dict = None
    _schedule: dict = None
    _visited: set = None

    @property
    def course_dict(self) -> dict:
        return self._cdict
    
    @property
    def prereq_dag(self) -> dict:
        return self._pdag
    
    @property
    def forward_dag(self) -> dict:
        return self._fdag
    
    @property
    def schedule(self) -> dict:
        return self._schedule

    def __post_init__(self):
        self._cdict = self.__read_csv_to_dict()
        self._pdag = self.__build_pdag(self._cdict)
        self._fdag = self.__build_fdag(self._cdict)
        self._session_val = {
            f'{s}{i}': i*3 + idx 
                for i in range(self.planned_years)
                for idx, s in enumerate(self.sessions) 
        }
        self._schedule = {k: [] for k in self._session_val.keys()}

        self._visited = set()
        if self.completed_courses:
            for course in self.completed_courses:
                self._visited.add(course)


    def __read_csv_to_dict(self) -> dict:
        df = pd.read_csv(self.data_path)
        return {
            row['CoursesID']: 
                (row['Title'], 
                 [] if pd.isnull(row['Prerequisites']) else row['Prerequisites'].split('+'), 
                 row['Units']) 
            for _, row in df.iterrows()
        }


    def __build_pdag(self, course_dict: dict) -> dict:
        return {k: v[1] for k, v in course_dict.items()}


    def __build_fdag(self, course_dict: dict) -> dict:
        dag = {} 
        for cid, (_, prereqs, _) in course_dict.items():
            dag.setdefault(cid, [])
            for p in prereqs:
                dag.setdefault(p, [])
                dag[p].append(cid)
        return dag
    
    
    def __build_plan_dfs(self, course: str, courses_avail: dict) -> None:
        # Base case
        if course in self._visited:
            return
        self._visited.add(course)

        # Find further node (core course / course with no prereq)
        if self._pdag[course]:
            for prereq in self._pdag[course]:
                if prereq not in self._visited:
                    self.__build_plan_dfs(prereq, courses_avail)

        # Lambda functions
        def check_max_units(k: str) -> bool:
            total_units = sum([self._cdict[c][2] for c in self._schedule[k]])
            return total_units + self._cdict[course][2] <= self.max_units_per_sem
        
        def get_score(base: int, dag: dict, extrema: Callable[[int, int], int]) -> int:
            score = base
            for n in dag[course]:
                for k, v in self._schedule.items():
                    if n in v:
                        score = extrema(score, self._session_val[k])
            return score

        # Add course to schedule logic
        min_window = get_score(-1, self._pdag, max)
        max_window = get_score(self.planned_years * 3, self._fdag, min)

        for i in range(self.planned_years):
            for session in courses_avail[course]:
                k = f'{session}{i}'
                score = self._session_val[k]
                if check_max_units(k) and min_window < score < max_window:
                    self._schedule[k].append(course)
                    return
    
    
    def fixed_core_course(self, semester: str, courses: list) -> None:
        self._schedule[f'{semester}'] = courses
        for course in courses:
            self._visited.add(course)


    def build_plan(self, courses_avail: dict) -> None:
        for k in courses_avail.keys():
            self.__build_plan_dfs(k, courses_avail)
                
                
    def display_schedule(self) -> None:
        print('-'*50, '\n')
        for k, v in self._schedule.items():
            print(f'{k}: {v}')
        print()
        print('-'*50, '\n')