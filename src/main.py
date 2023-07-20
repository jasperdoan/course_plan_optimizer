from planner import CoursePlanner
from scraper import CourseScraper

def main():
    plan = CoursePlanner(
        planned_years=2,
        semesters_per_year=3,
        max_units_per_semester=18,
        data_path='data\courses.csv'
    )

    # dag = plan.topological_sort(plan.prereq_dag)
    # for course, info in dag.items():
    #     print(course, info)

    # plan.graph_relationship()


    cs_2023 = CourseScraper(year=2023, level='ALL', department='CS', program='ALL')
    inf_2023 = CourseScraper(year=2023, level='ALL', department='INF', program='ALL')

    avail_dict = {**cs_2023.course_availability, **inf_2023.course_availability}
    course_dict = plan.course_dict

    # Display Info
    print('All Courses:\n', '-'*100)
    for course, (title, preq, units) in course_dict.items():
        print(f'{course}: {title} ({units} units)')
        print(f'\tPrerequisites: {preq}')
        print(f'\tAvailability: {avail_dict[course] if course in avail_dict else []}')
        print('-'*75)


if __name__ == '__main__':
    main()