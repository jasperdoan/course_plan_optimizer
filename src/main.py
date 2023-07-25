from planner import CoursePlanner
from scraper import scrape_avail_listings
from utils import *


def main():
    p = CoursePlanner(
        planned_years=2,
        semesters_per_year=3,
        max_units_per_semester=18,
        data_path='data\courses.csv'
    )

    avail_dict = {
        **scrape_avail_listings(year=2023, department='CS'), 
        **scrape_avail_listings(year=2023, department='INF')
    }

    course_dict = p.course_dict             # Course Dictionary
    pdag = topological_sort(p.prereq_dag) # Prerequisite DAG
    dlvl = dag_leveler(p.forward_dag)     # DAG Levels

    # Display Info
    display_info(course_dict, avail_dict)

    # Graph Relationships
    graph_relationship(pdag)

    # Display DAGs
    for k, v in pdag.items():
        print(f'{k}: {v}')

    # Display DAG Levels to find all core courses
    for item in dlvl:
        print(item)
    

if __name__ == '__main__':
    main()


# TODO:
# - Grab all core courses
# - Add core courses to planner first
# - Construct all a possible (DFS) based on availability
# - Add it to a list in [Fall, Winter, Spring]
# - Display all possible schedules