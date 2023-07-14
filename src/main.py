import pandas as pd
from utils import (
    read_csv_to_dict, 
    prereq_tree,
    course_option_tree,
    graph_prereq_relationship,
    topological_sort
)

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = prereq_tree(course_dict)
    # graph_prereq_relationship(adj_list)

    course_tree = course_option_tree(adj_list)
    sorted_list = topological_sort(course_tree)


    for i in range(0, len(sorted_list), 4):
        print(sorted_list[i:i+4])

    

if __name__ == '__main__':
    main()