import pandas as pd
from utils import (
    read_csv_to_dict,
    prereq_adjlist,
    create_dag,
    label_levels,
    graph_relationship,
    topological_sort
)

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = prereq_adjlist(course_dict)
    # dag = create_dag(course_dict)

    print(adj_list)
    
    mult_dag = []
    al_copy = adj_list.copy()

    try:
        for curr in adj_list:
            mult_dag.append(label_levels(al_copy))
            al_copy.pop(curr)
    except KeyError:
        pass


    for d in mult_dag:
        print(d)



    

if __name__ == '__main__':
    main()