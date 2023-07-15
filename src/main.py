import pandas as pd
from utils import (
    read_csv_to_dict,
    prereq_dag,
    forward_dag,
    dag_leveler,
    graph_relationship,
    topological_sort
)

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    tdown_dag = prereq_dag(course_dict)
    bup_dag = forward_dag(course_dict)

    ## Graph the relationship between courses
    graph_relationship(bup_dag)

    ## BFS Grab levels of each dags
    # levels = dag_leveler(bup_dag)
    # for it in levels:
    #     print(it)

    ## Topological Sort
    # print(topological_sort(bup_dag))


if __name__ == '__main__':
    main()