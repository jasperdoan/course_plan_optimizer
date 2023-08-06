import streamlit as st
import pandas as pd
from src.planner import CoursePlanner
from src.utils import load_availability
from src.config import Config, setup_page, setup_home_page, setup_planner_page


CONFIG = Config()
setup_page()
tab1, tab2, tab3 = st.tabs(CONFIG.tabs)


with st.sidebar:
    ID = 'CoursesID'
    core = pd.read_csv(CONFIG.swe)
    electives = pd.read_csv(CONFIG.swe_ext)
    all_courses = pd.concat([core, electives], ignore_index=True).sort_values(by=['CoursesID'])
    

    st.sidebar.title('Major')
    major = st.sidebar.selectbox(*CONFIG.majors)

    st.sidebar.title('Start Year')
    start_year = st.sidebar.text_input(*CONFIG.academic_years)

    st.sidebar.title('Planned Years')
    years = st.sidebar.slider(*CONFIG.s_years)

    st.sidebar.title('Max Units per Semester')
    max_units = st.sidebar.slider(*CONFIG.s_units)

    st.sidebar.title('Sessions')
    sessions = st.sidebar.multiselect(
        'Select the sessions you plan to take courses in',
        CONFIG.quarters,
        default=CONFIG.quarters[:-1]
        )

    st.sidebar.title(f'Course Information for {major}')
    st.dataframe(all_courses, hide_index=True)

    st.subheader('Electives Courses')
    elective_selected = st.sidebar.multiselect(
        CONFIG.elective_label, 
        [k.get(ID) for k in electives.to_dict('index').values()]
        )

    st.subheader('Completed Courses')
    completion = st.sidebar.multiselect(
        CONFIG.completed_label, 
        [k.get(ID) for k in all_courses.to_dict('index').values()]
        )


    # Trim electives to only the selected courses
    electives = electives[electives[ID].isin(elective_selected)]
    all_courses = pd.concat([core, electives], ignore_index=True).sort_values(by=['CoursesID'])
    all_courses.to_csv(CONFIG.student_pick, index=False)


    st.session_state['student_plan'] = CoursePlanner(
        data_path=CONFIG.student_pick,
        planned_years=years,
        max_units_per_sem=max_units,
        completed_courses=completion,
        sessions=sessions
        )
    


with tab1:
    t1_lcol, t1_rcol = st.columns(CONFIG.thirds)
    setup_home_page(t1_lcol, t1_rcol, CONFIG, st.session_state['student_plan'])
    

with tab2:
    student_plan = st.session_state['student_plan']
    years = student_plan.planned_years
    quarter_seasons = student_plan.sessions

    t2_lcol, t2_rcol = st.columns(CONFIG.sixths)
    setup_planner_page(t2_rcol, CONFIG)
    
    # Keep for @cache_data
    availability_list = load_availability(CONFIG.availability)

    courses_avail = {}
    for k in student_plan.course_dict.keys():
        if k in availability_list:
            courses_avail[k] = availability_list[k]
        else:
            t2_rcol.warning(
                f'Looks like {k} is not offered this school year, pick another elective', 
                icon="⚠️"
                )

    session = {f'{s}{i}': [] for i in range(years) for s in quarter_seasons}

    for i in range(years):
        for season in quarter_seasons:
            k = f'{season}{i}'
            session[k] = t2_rcol.multiselect(
                f'**{k}**',
                [k for k, v in courses_avail.items() if season in v],
                key=k
            )

    courses_avail = {k: v for k, v in sorted(courses_avail.items(), key=lambda item: len(item[1]))}
    
    if t2_rcol.button('Generate Plan'):
        t2_rcol.success('Successfully generated!', icon="✅")
        st.balloons()
        for i in range(years):
            for season in quarter_seasons:
                k = f'{season}{i}'
                if k in st.session_state:
                    student_plan.fixed_core_course(k, session[k])

        student_plan.build_plan(courses_avail) 
        t2_lcol.header('Potential Plan(s)')
        t2_lcol.table(student_plan.schedule)
        

with tab3:
    st.snow()
    st.title('Your mom')