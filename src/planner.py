import pandas as pd
from dataclasses import dataclass


@dataclass
class CoursePlanner:
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