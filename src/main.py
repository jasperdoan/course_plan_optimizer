import pandas as pd

from utils import read_csv_to_dict, create_adj_list, graph_prereq_relationship

def main():
    course_dict = read_csv_to_dict('data\courses.csv')
    adj_list = create_adj_list(course_dict)

    graph_prereq_relationship(adj_list)


if __name__ == '__main__':
    main()