import streamlit as st
from src.planner import CoursePlanner
from src.utils import *


COURSE_DATA_PATH = 'data\software_engineering.csv'
COURSE_EXT_DATA_PATH = 'data\software_engineering_ext.csv'
AVAILABILITY_PATH = 'data\courses_availability.csv'
TEMP_PATH = 'data\\temp.csv'

st.set_page_config(
    page_title='UCI Course Optimizer',
    page_icon='📚',
    layout='wide',
    initial_sidebar_state='auto'
)
tab1, tab2, tab3 = st.tabs(['Home', 'Course Planner', 'About'])





with st.sidebar:
    core = pd.read_csv(COURSE_DATA_PATH)
    electives = pd.read_csv(COURSE_EXT_DATA_PATH)
    all_courses = pd.concat([core, electives], ignore_index=True).sort_values(by=['CoursesID'])


    st.sidebar.title('Major')
    major = st.sidebar.selectbox(
        'Select your major', 
        ['Software Engineering', 'Computer Science', 'Data Science']
    )

    st.sidebar.title('Start Year')
    start_year = st.sidebar.text_input('Enter your start year', '2023')

    st.sidebar.title('Planned Years')
    st.session_state['planned_years'] = st.sidebar.slider('How many years do you plan to take?', 1, 6, 2)

    st.sidebar.title('Max Units per Semester')
    max_units = st.sidebar.slider('How many units do you plan to take per semester?', 1, 20, 16)

    st.sidebar.title(f'Course Information for {major}')
    st.dataframe(all_courses, hide_index=True)

    st.subheader('Electives Courses')
    elective_selected = st.sidebar.multiselect(
        'Select the elective courses you are interested in taking',
        [k for k, (_, _, _) in load_courses(COURSE_EXT_DATA_PATH).items()],
    )

    st.subheader('Completed Courses')
    completed_courses = st.sidebar.multiselect(
        'Select the courses you have already completed/are going to transfer over',
        [k for k, (_, _, _) in {**load_courses(COURSE_DATA_PATH), **load_courses(COURSE_EXT_DATA_PATH)}.items()],
    )



    # For every course picked in elective_selected, create a temp.csv file with the core courses + the selected elective course
    # Trim electives to only the selected courses
    electives = electives[electives['CoursesID'].isin(elective_selected)]
    all_courses = pd.concat([core, electives], ignore_index=True).sort_values(by=['CoursesID'])

    # Create a temp.csv file with the core courses + the selected elective course
    all_courses.to_csv(TEMP_PATH, index=False)



    st.session_state['student_plan'] = CoursePlanner(
        data_path=TEMP_PATH,
        planned_years=st.session_state['planned_years'],
        max_courses_per_sem=4,
        completed_courses=completed_courses,
    )
    


with tab1:
    tab1_col1, tab1_col2 = st.columns([1, .3])
    tab1_col1.title('UCI Course Plan Optimizer')
    tab1_col1.write('This is a course planner for UCI students. It is designed to help students plan out their courses for the next few years.')
    tab1_col1.write('This app will create the optimal academic year plan for students. This tool uses Bayesian networks, DFS, Topological sorting to build DAGs that prevent class conflicts, considering prerequisites, corequisites, units & course likeness. Streamline your course planning with ease. GitHub repo for efficient scheduling.')
    tab1_col2.image('https://media.tenor.com/CYE3MnKr2nQAAAAd/dog-huh.gif')
    
    st.subheader('Major Pathway: Direct Acyclic Graphs for Major')
    st.write('The following is the prerequisite DAG for your major courses based on your sidebar inputs.')
    try:
        pdag = st.session_state['student_plan'].prereq_dag.copy()
        for course in st.session_state['student_plan'].completed_courses:
            pdag.pop(course)
            for k, v in pdag.items():
                if course in v:
                    pdag[k].remove(course)
        plot_dag(pdag)
    except:
        st.warning('Slow down - Add one course at a time', icon="⚠️")
    

with tab2:
    tab2_col1, tab2_col2 = st.columns([1, .6])
    tab2_col2.header('Add Fixed Core Courses')
    tab2_col2.write('If there\'s a course you want to take in a specific quarter, add it here.')
    tab2_col2.info('Note: These are TENTATIVE course listings schedule. Department Chairs may provide updated information regarding course offerings or faculty assignments throughout the year.', icon="ℹ️")
    
    availability_list = load_availability(AVAILABILITY_PATH)

    courses_avail = {}
    for k, _ in st.session_state['student_plan'].course_dict.items():
        if k in availability_list:
            courses_avail[k] = availability_list[k]
        else:
            tab2_col2.warning(f'Looks like {k} is not offered this school year, pick another elective', icon="⚠️")

    session = {
        f'{s}{i}': [] 
            for i in range(st.session_state['planned_years'])
            for s in ['Fall', 'Winter', 'Spring'] 
    }

    for i in range(st.session_state['planned_years']):
        for season in ['Fall', 'Winter', 'Spring']:
            session[f'{season}{i}'] = tab2_col2.multiselect(
                f'**{season} {i}**',
                [k for k, v in courses_avail.items() if season in v],
                key=f'{season}{i}'
            )

    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}
    
    if tab2_col2.button('Generate Plan'):
        tab2_col2.success('Successfully generated a plan!', icon="✅")
        st.balloons()
        for i in range(st.session_state['planned_years']):
            for season in ['Fall', 'Winter', 'Spring']:
                if f'{season}{i}' in st.session_state:
                    st.session_state['student_plan'].fixed_core_course(
                        f'{season}{i}',
                        session[f'{season}{i}']
                    )

        st.session_state['student_plan'].build_plan(courses_avail) 
        schedule = st.session_state['student_plan'].schedule
        tab2_col1.header('Potential Plan(s)')
        tab2_col1.table(schedule)
        

with tab3:
    st.snow()
    st.title('Your mom')