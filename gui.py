import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from src.planner import CoursePlanner
from src.scraper import read_csv
from src.utils import *


tab1, tab2, tab3, tab4 = st.tabs(['Home', 'Major Courses and Information', 'Course Planner', 'About'])


def load_data() -> dict:
    df = pd.read_csv('data\courses.csv')
    course_dict = {}
    for _, row in df.iterrows():
        course_id = row['CoursesID']
        title = row['Title']
        prereq = row['Prerequisites']
        units = row['Units']
        prereq_list = [] if pd.isnull(prereq) else prereq.split('+')
        course_dict[course_id] = (title, prereq_list, units)
    return course_dict


with st.sidebar:
    st.sidebar.title('Major')
    st.session_state['major'] = st.sidebar.selectbox(
        'Select your major', 
        ['Software Engineering', 'Computer Science', 'Data Science', 'Informatics']
    )

    st.sidebar.title('Start Year')
    st.session_state['start_year'] = st.sidebar.text_input('Enter your start year', '2023')

    st.sidebar.title('Planned Years')
    st.session_state['planned_year'] = st.sidebar.slider('How many years do you plan to take?', 1, 6, 4)

    st.sidebar.title('Max Units per Semester')
    st.session_state['max_units'] = st.sidebar.slider('How many units do you plan to take per semester?', 1, 20, 12)


with tab1:
    st.title('UCI Course Plan Optimizer')
    st.write('This is a course planner for UCI students. It is designed to help students plan out their courses for the next few years.')
    st.write('This app will create the optimal academic year plan for students. This tool uses Bayesian networks, DFS, Topological sorting to build DAGs that prevent class conflicts, considering prerequisites, corequisites, units & course likeness. Streamline your course planning with ease. GitHub repo for efficient scheduling.')
    st.image('https://media.tenor.com/CYE3MnKr2nQAAAAd/dog-huh.gif')


with tab2:
    # TEMPORARY
    st.subheader('Course Information for ' + st.session_state['major'])
    df = pd.read_csv('data\courses.csv')
    st.table(df)

    st.subheader('Direct Acyclic Graphs')
    st.write('The following is the prerequisite DAG for the major courses')
    graph_relationship({k: l for k, (_, l, _) in load_data().items()})