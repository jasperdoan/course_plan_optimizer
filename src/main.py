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
    # graph_relationship(bup_dag)

    # BFS Grab levels of each dags
    levels = dag_leveler(bup_dag)
    for it in levels:
        print(it)

    ## Topological Sort
    # print(topological_sort(bup_dag))


if __name__ == '__main__':
    main()

'''
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
'''