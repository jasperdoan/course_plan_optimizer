from planner import CoursePlanner

def main():
    # course_dict = read_csv_to_dict('data\courses.csv')
    # tdown_dag = prereq_dag(course_dict)
    # bup_dag = forward_dag(course_dict)

    ## Graph the relationship between courses
    # graph_relationship(bup_dag)

    # # BFS Grab levels of each dags
    # levels = dag_leveler(bup_dag)
    # for it in levels:
    #     print(it)

    ## Topological Sort
    # print(topological_sort(bup_dag)

    plan = CoursePlanner(
        planned_years=2,
        semesters_per_year=3,
        max_units_per_semester=18,
        data_path='data\courses.csv'
    )

    for course, info in plan.course_dict.items():
        print(course, info)

    plan.graph_relationship()


if __name__ == '__main__':
    main()