
from planner import CoursePlanner
from scraper import *
from utils import *


def main():
    p = CoursePlanner('data\courses.csv')

    SESSION_VAL = {
        'Fall0': 0, 'Winter0': 1, 'Spring0': 2, 
        'Fall1': 3, 'Winter1': 4, 'Spring1': 5
    }
    schedule = {
        f'{s}{y}': [] 
            for y in [0, 1] 
            for s in ['Fall', 'Winter', 'Spring']
    }
    availability_list = read_csv('data\course_avail.csv')

    
    courses_avail = {k: availability_list[k] for k, _ in p.course_dict.items()}
    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}
    visited = set()


    for k, v in courses_avail.items():
        print(f'{k}: {v}')

    
    def dfs(course: str, visited: set, prereq_dag: dict, schedule: dict, courses_avail: dict) -> None:
        if prereq_dag[course]:
            for prereq in prereq_dag[course]:
                if prereq not in visited:
                    dfs(prereq, visited, prereq_dag, schedule, courses_avail)

        if course in visited:
            return

        flag = False
        if not prereq_dag[course]:
            for i in [0, 1]:
                for session in courses_avail[course]:
                    if len(schedule[f'{session}{i}']) < 4:
                        schedule[f'{session}{i}'].append(course)
                        flag = True
                        break
                if flag:
                    break
        else:
            # Grab latest point in schedule where all prereqs are satisfied
            # and add course to that point
            session_score = 0
            for prereq in prereq_dag[course]:
                for k, v in schedule.items():
                    if prereq in v:
                        session_score = max(session_score, SESSION_VAL[k])

            for i in [0, 1]:
                for session in courses_avail[course]:
                    if len(schedule[f'{session}{i}']) < 4 and SESSION_VAL[f'{session}{i}'] > session_score:
                        schedule[f'{session}{i}'].append(course)
                        flag = True
                        break
                if flag:
                    break         

        visited.add(course)
            


    for x, _ in courses_avail.items():
        dfs(x, visited, p.prereq_dag, schedule, courses_avail)



    print('-'*50, '\n')
    for k, v in schedule.items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()


# TODO:
# [ ] DFS within DFS --> Check for prereq while building schedule
#       Rn its just filling in earliest available slot without prereq check
# [ ] Construct all a possible (DFS) based on availability
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