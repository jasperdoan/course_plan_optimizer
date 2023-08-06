import streamlit as st
import pandas as pd
from src.planner import CoursePlanner
from src.utils import load_courses, load_availability, update_plot_dag



COURSE_DATA_PATH = 'data\software_engineering.csv'
COURSE_EXT_DATA_PATH = 'data\software_engineering_ext.csv'
AVAILABILITY_PATH = 'data\courses_availability.csv'
STUDENT_PICK = 'data\\student_pick.csv'
QUARTERS = ['Fall', 'Winter', 'Spring', 'Summer']


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

    st.sidebar.title('Sessions')
    st.session_state['sessions'] = st.sidebar.multiselect(
        'Select the sessions you plan to take courses in',
        QUARTERS,
        default=QUARTERS[:-1]
    )

    st.sidebar.title(f'Course Information for {major}')
    st.dataframe(all_courses, hide_index=True)

    st.subheader('Electives Courses')
    elective_selected = st.sidebar.multiselect(
        'Select the elective courses you are interested in taking',
        [k for k in load_courses(COURSE_EXT_DATA_PATH).keys()],
    )

    st.subheader('Completed Courses')
    st.session_state['completed_courses'] = st.sidebar.multiselect(
        'Select the courses you have already completed/are going to transfer over',
        [k for k in {**load_courses(COURSE_DATA_PATH), **load_courses(COURSE_EXT_DATA_PATH)}.keys()],
    )


    # For every course picked in elective_selected, create a temp.csv file with the core courses + the selected elective course
    # Trim electives to only the selected courses
    electives = electives[electives['CoursesID'].isin(elective_selected)]
    all_courses = pd.concat([core, electives], ignore_index=True).sort_values(by=['CoursesID'])

    # Create a temp.csv file with the core courses + the selected elective course
    all_courses.to_csv(STUDENT_PICK, index=False)


    st.session_state['student_plan'] = CoursePlanner(
        data_path=STUDENT_PICK,
        planned_years=st.session_state['planned_years'],
        max_units_per_sem=max_units,
        completed_courses=st.session_state['completed_courses'],
        sessions=st.session_state['sessions']
    )
    


with tab1:
    t1_lcol, t1_rcol = st.columns([1, .3])
    t1_lcol.title('UCI Course Plan Optimizer')
    t1_lcol.write('This is a course planner for UCI students. It is designed to help students plan out their courses for the next few years.')
    t1_lcol.write('This app will create the optimal academic year plan for students. This tool uses Bayesian networks, DFS, Topological sorting to build DAGs that prevent class conflicts, considering prerequisites, corequisites, units & course likeness. Streamline your course planning with ease. GitHub repo for efficient scheduling.')
    t1_rcol.image('https://media.tenor.com/CYE3MnKr2nQAAAAd/dog-huh.gif')
    
    st.subheader('Major Pathway: Direct Acyclic Graphs for Major')
    st.write('The following is the prerequisite DAG for your major courses based on your sidebar inputs.')
    
    update_plot_dag(st.session_state['student_plan'])
    

with tab2:
    t2_lcol, t2_rcol = st.columns([1, .6])
    t2_rcol.header('Add Fixed Core Courses')
    t2_rcol.write('If there\'s a course you want to take in a specific quarter, add it here.')
    t2_rcol.info('Note: These are TENTATIVE course listings schedule. Department Chairs may provide updated information regarding course offerings or faculty assignments throughout the year.', icon="ℹ️")
    
    availability_list = load_availability(AVAILABILITY_PATH)

    courses_avail = {}
    for k in st.session_state['student_plan'].course_dict.keys():
        if k in availability_list:
            courses_avail[k] = availability_list[k]
        else:
            t2_rcol.warning(f'Looks like {k} is not offered this school year, pick another elective', icon="⚠️")

    session = {
        f'{s}{i}': [] 
            for i in range(st.session_state['planned_years'])
            for s in st.session_state['sessions'] 
    }

    for i in range(st.session_state['planned_years']):
        for season in st.session_state['sessions']:
            k = f'{season}{i}'
            session[k] = t2_rcol.multiselect(
                f'**{k}**',
                [k for k, v in courses_avail.items() if season in v],
                key=k
            )

    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}
    
    if t2_rcol.button('Generate Plan'):
        t2_rcol.success('Successfully generated a plan!', icon="✅")
        st.balloons()
        for i in range(st.session_state['planned_years']):
            for season in st.session_state['sessions']:
                k = f'{season}{i}'
                if k in st.session_state:
                    st.session_state['student_plan'].fixed_core_course(k, session[k])

        st.session_state['student_plan'].build_plan(courses_avail) 
        schedule = st.session_state['student_plan'].schedule
        t2_lcol.header('Potential Plan(s)')
        t2_lcol.table(schedule)
        

with tab3:
    st.snow()
    st.title('Your mom')