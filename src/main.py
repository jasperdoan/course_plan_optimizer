from planner import CoursePlanner
from scraper import *
from utils import *


def main():
    p = CoursePlanner('data\courses.csv')

    schedule = {
        f'{s} {y}': [] 
            for y in ['2023', '2024'] 
            for s in ['Fall', 'Winter', 'Spring']
    }
    avail_dict = read_csv('data\course_avail.csv')
    dlvl = dag_leveler(p.forward_dag)

    for item in dlvl:
        for k, i in item.items():
            print(f'Level {i}: {k}: {avail_dict[k]}')
        print('-'*25)


if __name__ == '__main__':
    main()


# TODO:
# [X] Grab all core courses
# [ ] Add core courses to planner first
# [ ] Construct all a possible (DFS) based on availability
# [ ] Add it to a list in [Fall, Winter, Spring]
# [ ] Display all possible schedules