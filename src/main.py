from planner import CoursePlanner
from scraper import scape_read_csv
from utils import *
            

def main():
    transferred_courses = ['ICS 6N', 'ICS 31', 'ICS 32', 'ICS 33', 'ICS 45C', 'ICS 45J', 'ICS 46', 'ICS 51']

    p = CoursePlanner(
        data_path='data\software_engineering.csv',
        planned_years=2,
        max_units_per_sem=16,
        completed_courses=transferred_courses
    )

    availability_list = scape_read_csv('data\courses_availability.csv')

    courses_avail = {k: availability_list[k] for k, _ in p.course_dict.items()}
    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}
    

    # Hard picked core classes
    p.fixed_core_course('Fall0', ['ICS 6B', 'CS 122A', 'INF 43', 'STATS 67'])
    p.fixed_core_course('Winter0', ['ICS 6D', 'ICS 139W', 'INF 101', 'INF 113'])
    p.fixed_core_course('Winter1', ['CS 161'])

    p.build_plan(courses_avail)

    p.display_schedule()


if __name__ == '__main__':
    main()


# TODO:
# [ ] Display multiple possible schedules

# [ ] Webscape prerequisites instead of manually adding them in csv file
#       https://www.reg.uci.edu/cob/prrqcgi?term=202392&dept=IN4MATX&action=view_by_term#43
#       https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/softwareengineering_bs/#requirementstext

# [ ] Refine GUI

# [ ] Change implementation to MAX UNITS instead of MAX COURSES per semester