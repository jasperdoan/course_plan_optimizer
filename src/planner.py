import pandas as pd
from dataclasses import dataclass


@dataclass
class CoursePlanner:
    data_path: str
    planned_years: int
    completed_courses: list = None
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

    def __post_init__(self):
        self._cdict = self.__read_csv_to_dict()
        self._pdag = self.__build_pdag(self._cdict)
        self._fdag = self.__build_fdag(self._cdict)
        self._session_val = {
            f'{s}{i}': i*3 + idx 
                for i in range(self.planned_years)
                for idx, s in enumerate(['Fall', 'Winter', 'Spring']) 
        }
        self._schedule = {k: [] for k in self._session_val.keys()}

        self._visited = set()
        if self.completed_courses:
            for course in self.completed_courses:
                self._visited.add(course)


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
    

    def __build_plan_dfs(self, course: str, courses_avail: dict) -> None:
        if course in self._visited:
            return
        self._visited.add(course)

        if self._pdag[course]:
            for prereq in self._pdag[course]:
                if prereq not in self._visited:
                    self.__build_plan_dfs(prereq, courses_avail)
        else:
            for i in [0, 1]:
                for session in courses_avail[course]:
                    if len(self._schedule[f'{session}{i}']) < 4:
                        self._schedule[f'{session}{i}'].append(course)
                        return

        # If the course has prerequisites
        min_score_window = -1
        for prereq in self._pdag[course]:
            for k, v in self._schedule.items():
                if prereq in v:
                    min_score_window = max(min_score_window, self._session_val[k])
        # Check forwards dag
        max_score_window = 6
        for next_course in self._fdag[course]:
            for k, v in self._schedule.items():
                if next_course in v:
                    max_score_window = min(max_score_window, self._session_val[k])
        
        for i in [0, 1]:
            for session in courses_avail[course]:
                window = self._session_val[f'{session}{i}'] > min_score_window and self._session_val[f'{session}{i}'] < max_score_window
                if len(self._schedule[f'{session}{i}']) < 4 and window:
                    self._schedule[f'{session}{i}'].append(course)
                    return
    
    
    def fixed_core_course(self, semester: str, year: int, courses: list) -> None:
        self._schedule[f'{semester}{year}'] = courses
        for course in courses:
            self._visited.add(course)
    

    def build_plan(self, courses_avail: dict) -> None:
        for x, _ in courses_avail.items():
            self.__build_plan_dfs(x, courses_avail)
                
                
    def display_schedule(self) -> None:
        print('-'*50, '\n')
        for k, v in self._schedule.items():
            print(f'{k}: {v}')
        print()
        print('-'*50, '\n')