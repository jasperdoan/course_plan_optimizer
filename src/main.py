import pandas as pd

from utils import read_csv_to_dict, class_tree_adj_list, graph_relationships

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = class_tree_adj_list(course_dict)

    graph_relationships(adj_list)


if __name__ == '__main__':
    main()