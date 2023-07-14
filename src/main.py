import pandas as pd
from utils import (
    read_csv_to_dict, 
    prereq_tree,
    course_option_tree,
    graph_prereq_relationship
)

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = prereq_tree(course_dict)
    graph_prereq_relationship(adj_list)
    
    adj_list = course_option_tree(adj_list)

    

if __name__ == '__main__':
    main()