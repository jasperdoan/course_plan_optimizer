from planner import CoursePlanner

def main():
    plan = CoursePlanner(
        planned_years=2,
        semesters_per_year=3,
        max_units_per_semester=18,
        data_path='data\courses.csv'
    )

    dag = plan.topological_sort(plan.prereq_dag)
    for course, info in dag.items():
        print(course, info)

    plan.graph_relationship()


if __name__ == '__main__':
    main()