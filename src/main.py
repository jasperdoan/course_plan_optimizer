
from planner import CoursePlanner
from scraper import *
from utils import *


SESSION_VAL = {
    f'{s}{i}': i*3 + idx 
        for i in [0, 1]
        for idx, s in enumerate(['Fall', 'Winter', 'Spring']) 
}

def dfs(course: str, visited: set, prereq_dag: dict, forward_dag: dict, schedule: dict, courses_avail: dict) -> None:
    if course in visited:
        return
    visited.add(course)

    if prereq_dag[course]:
        for prereq in prereq_dag[course]:
            if prereq not in visited:
                dfs(prereq, visited, prereq_dag, forward_dag, schedule, courses_avail)
    else:
        for i in [0, 1]:
            for session in courses_avail[course]:
                if len(schedule[f'{session}{i}']) < 4:
                    schedule[f'{session}{i}'].append(course)
                    return

    # If the course has prerequisites
    min_score_window = -1
    for prereq in prereq_dag[course]:
        for k, v in schedule.items():
            if prereq in v:
                min_score_window = max(min_score_window, SESSION_VAL[k])
    # Check forwards dag
    max_score_window = 6
    for next_course in forward_dag[course]:
        for k, v in schedule.items():
            if next_course in v:
                max_score_window = min(max_score_window, SESSION_VAL[k])
    
    for i in [0, 1]:
        for session in courses_avail[course]:
            window = SESSION_VAL[f'{session}{i}'] > min_score_window and SESSION_VAL[f'{session}{i}'] < max_score_window
            if len(schedule[f'{session}{i}']) < 4 and window:
                schedule[f'{session}{i}'].append(course)
                return
            

def main():
    p = CoursePlanner('data\courses.csv')

    schedule = {k: [] for k in SESSION_VAL.keys()}

    availability_list = read_csv('data\course_avail.csv')

    
    courses_avail = {k: availability_list[k] for k, _ in p.course_dict.items()}
    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}
    visited = set()


    # Completed courses
    completed = ['ICS 6N', 'ICS 31', 'ICS 32', 'ICS 33', 'ICS 45C', 'ICS 45J', 'ICS 46', 'ICS 51']

    for course in completed:
        visited.add(course)
        
    # Hard picked core classes
    schedule['Fall0'] = ['ICS 6B', 'CS 122A', 'INF 43', 'STATS 67']
    schedule['Winter0'] = ['ICS 6D', 'ICS 139W', 'INF 101', 'INF 113']
    schedule['Winter1'] = ['CS 161']

    for _, v in schedule.items():
        for course in v:
            visited.add(course)            


    for x, _ in courses_avail.items():
        dfs(x, visited, p.prereq_dag, p.forward_dag, schedule, courses_avail)



    print('-'*50, '\n')
    for k, v in schedule.items():
        print(f'{k}: {v}')
    print()
    print('-'*50, '\n')


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