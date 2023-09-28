import streamlit as st
from typing import NamedTuple
from src.utils import update_plot_dag


class Config(NamedTuple):
    # Paths
    swe = 'data\software_engineering.csv'
    swe_ext = 'data\software_engineering_ext.csv'
    ds = 'data\data_science.csv'
    ds_ext = 'data\data_science_ext.csv'
    availability = 'data\courses_availability.csv'
    student_pick = 'data\\student_pick.csv'

    # Option lists
    quarters = ['Fall', 'Winter', 'Spring', 'Summer']
    tabs = ['Home', 'Course Planner', 'About']

    # Labels
    home_title = 'UCI Course Optimizer'
    home_description = '''
        This is a course planner for UCI students. It is designed to help students plan out their courses for 
        the next few years.\n\nThis app will create the optimal academic year plan for students. This tool uses 
        Bayesian networks, DFS, Topological sorting to build DAGs that prevent class conflicts, considering 
        prerequisites, corequisites, units & course likeness. Streamline your course planning with ease. GitHub 
        repo for efficient scheduling.
        '''
    home_funny_gif = 'https://media.tenor.com/CYE3MnKr2nQAAAAd/dog-huh.gif'
    home_pathway = 'Major Pathway: Direct Acyclic Graphs for Major'
    home_dag_desc = 'The following is the prerequisite DAG for your major courses based on your sidebar inputs.'
    elective_label = 'Select the elective courses you are interested in taking'
    completed_label = 'Select the courses you have already completed/are going to transfer over'

    planner_title = 'Add Fixed Courses'
    planner_description = 'If there\'s a course you want to take in a specific quarter, add it here.'
    planner_info = 'Note: These are TENTATIVE course listings schedule. Department Chairs may provide updated information regarding course offerings or faculty assignments throughout the year.'

    # Spacing/Padding for columns
    thirds = [1, .3]
    sixths = [1, .6]

    # (label, options)
    majors = (
        'Select your major',
        ['Software Engineering', 'Computer Science', 'Data Science']
        )

    # (label, default)
    academic_years = ('Enter your start year', '2023')

    # (label, min, max, default)
    s_years = ('How many years do you plan to take?', 1, 6, 2)
    s_units = ('How many units do you plan to take per semester?', 0, 20, 16)



def setup_page():
    st.set_page_config(
        page_title='UCI Course Optimizer',
        page_icon='📚',
        layout='wide',
        initial_sidebar_state='auto'
        )
    

def setup_home_page(left_col, right_col, config, dag):
    left_col.title(config.home_title)
    left_col.write(config.home_description)
    right_col.image(config.home_funny_gif)

    st.subheader(config.home_pathway)
    st.write(config.home_dag_desc)
    update_plot_dag(dag)


def setup_planner_page(col, config):
    col.header(config.planner_title)
    col.write(config.planner_description)
    col.info(config.planner_info, icon="ℹ️")