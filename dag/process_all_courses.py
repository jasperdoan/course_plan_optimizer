import os
import json
from course_dag_visualizer import CoursePrereqVisualizer

def process_all_courses(output_dir='all_course_graphs', json_file='course_data_with_logical_prereqs.json', depth=2):
    """Generate graphs for all courses with prerequisites."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    visualizer = CoursePrereqVisualizer(json_file)
    
    # Load the course data
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            courses = json.load(f)
    except Exception as e:
        print(f"Error loading course data: {e}")
        return
    
    # Count courses with actual prerequisites
    courses_with_prereqs = [
        course_id for course_id, data in courses.items() 
        if data.get("parsed_prerequisites") not in ["N/A", None, ""]
    ]
    
    print(f"Found {len(courses_with_prereqs)} courses with prerequisites.")
    
    # Process each course
    for i, course_id in enumerate(courses_with_prereqs):
        print(f"Processing {i+1}/{len(courses_with_prereqs)}: {course_id}")
        try:
            output_path = visualizer.save_course_graph(course_id, output_dir, depth)
            print(f"  Saved to {output_path}")
        except Exception as e:
            print(f"  Error processing {course_id}: {e}")
    
    print(f"Completed processing {len(courses_with_prereqs)} courses.")

if __name__ == "__main__":
    process_all_courses()
