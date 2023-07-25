
from enum import Enum
from planner import CoursePlanner
from scraper import *
from utils import *


# TODO: Try to add DFS field snake to logic to see which session makes most sense
class Session(Enum):
    FALL0 = 0
    WINTER0 = 1
    SPRING0 = 2
    FALL1 = 3
    WINTER1 = 4
    SPRING1 = 5


def main():
    p = CoursePlanner('data\courses.csv')

    schedule = {
        f'{s}{y}': [] 
            for y in [0, 1] 
            for s in ['Fall', 'Winter', 'Spring']
    }
    availability_list = read_csv('data\course_avail.csv')
    dlvl = dag_leveler(p.forward_dag)

    
    courses_avail = {k: availability_list[k] for k, _ in p.course_dict.items()}
    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}

    for k, v in courses_avail.items():
        print(f'{k}: {v}')

    # Hard picked core courses
    schedule['Fall0'] = ['ICS 6B', 'CS 122A', 'INF 43', 'STATS 67']
    schedule['Winter0'] = ['ICS 6D', 'ICS 139W']


    for x, session in courses_avail.items():
        for s in session:
            i = int(bool(p.prereq_dag[x]))
            schedule[f'{s}{i}'].append(x)

            # DFS logic here


        if x == 'CS 145':
            break
        

    print('-'*50, '\n')
    for k, v in schedule.items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()


# TODO:
# [X] Grab all core courses
# [X] Add core courses to planner first
# [ ] Construct all a possible (DFS) based on availability
# [ ] Add it to a list in [Fall, Winter, Spring]
# [ ] Display all possible schedules

# [ ] Webscape prerequisites instead of manually adding them in csv file
#       https://www.reg.uci.edu/cob/prrqcgi?term=202392&dept=IN4MATX&action=view_by_term#43
#       https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/softwareengineering_bs/#requirementstext

# [ ] CLI




# for item in dlvl:
#     for k, i in item.items():
#         print('    '*i + f'{i}: {k}: {availability_list[k]}' )
#     print('-'*50)

# for k, v in availability_list.items():
#     print(f'{k}: {v}')