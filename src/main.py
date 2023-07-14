import pandas as pd
from utils import (
    read_csv_to_dict,
    prereq_adjlist,
    create_dag,
    create_mult_dag,
    graph_relationship,
    topological_sort
)

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = prereq_adjlist(course_dict)
    # comb_dag = create_dag(course_dict)
    mult_dag = create_mult_dag(adj_list)

    for dag in mult_dag:
        print(dag)



if __name__ == '__main__':
    main()