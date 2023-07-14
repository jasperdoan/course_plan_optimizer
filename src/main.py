import pandas as pd
from utils import (
    read_csv_to_dict,
    prereq_adjlist,
    create_dag,
    level_order_traversal,
    graph_relationship,
    topological_sort
)

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = prereq_adjlist(course_dict)
    dag = create_dag(course_dict)

    print(adj_list)

    

if __name__ == '__main__':
    main()