import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch
import matplotlib.colors as mcolors
from matplotlib.collections import PatchCollection
import numpy as np
import argparse
import re
import os

class CoursePrereqVisualizer:
    def __init__(self, json_file='course_data_with_logical_prereqs.json'):
        """Initialize the visualizer with the course data."""
        self.courses = self.load_course_data(json_file)
        self.G = nx.DiGraph()
        self.or_groups = []  # List to store OR groups for visualization
        self.group_counter = 0  # Counter for generating unique OR group IDs
        
    def load_course_data(self, json_file):
        """Load course data from JSON file."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading course data: {e}")
            return {}
    
    def parse_prerequisites(self, prereq_structure, target_course):
        """
        Parse the prerequisite structure and add appropriate nodes and edges to the graph.
        
        Args:
            prereq_structure: The prerequisite structure (string, dict with AND/OR)
            target_course: The course that requires these prerequisites
            
        Returns:
            List of nodes that represent the immediate prerequisites for target_course
        """
        if prereq_structure == "N/A" or not prereq_structure:
            return []
            
        if isinstance(prereq_structure, str):
            # Simple prerequisite (single course)
            # Don't add self-loops
            if prereq_structure != target_course:
                self.G.add_node(prereq_structure)
                return [prereq_structure]
            return []
            
        if isinstance(prereq_structure, dict):
            if "and" in prereq_structure:
                # AND relationship: all courses are required
                prereq_nodes = []
                for prereq in prereq_structure["and"]:
                    nodes = self.parse_prerequisites(prereq, target_course)
                    prereq_nodes.extend(nodes)
                return prereq_nodes
                
            elif "or" in prereq_structure:
                # OR relationship: any one course satisfies the requirement
                self.group_counter += 1
                group_name = f"OR_GROUP_{self.group_counter}"
                
                or_members = []
                for prereq in prereq_structure["or"]:
                    member_nodes = self.parse_prerequisites(prereq, target_course)
                    or_members.extend(member_nodes)
                
                # Store OR group for visualization
                if or_members:
                    self.or_groups.append((group_name, or_members))
                    return [group_name]  # Return the group as a single node
                return []
        
        print(f"Warning: Unknown prerequisite structure: {prereq_structure}")
        return []
    
    def build_graph_for_course(self, target_course, depth=2):
        """
        Build a directed graph for the prerequisites of the target course.
        
        Args:
            target_course: The course to build the graph for
            depth: How many levels of prerequisites to include (default: 2)
        """
        if target_course not in self.courses:
            print(f"Course {target_course} not found in the data.")
            return
            
        # Reset the graph and OR groups for a new visualization
        self.G = nx.DiGraph()
        self.or_groups = []
        self.group_counter = 0
        
        # Add the target course as a node
        self.G.add_node(target_course)
        
        # Process the immediate prerequisites
        queue = [(target_course, 0)]  # (course, current_depth)
        processed = set()
        
        while queue:
            course, current_depth = queue.pop(0)
            
            if course in processed or current_depth >= depth:
                continue
                
            processed.add(course)
            
            # Skip OR groups in the recursive prerequisite search
            if course.startswith("OR_GROUP_"):
                continue
                
            # Get the prerequisites for this course
            if course in self.courses:
                prereq_structure = self.courses[course].get("parsed_prerequisites", "N/A")
                prereq_nodes = self.parse_prerequisites(prereq_structure, course)
                
                # Connect prerequisites to the course
                for prereq in prereq_nodes:
                    self.G.add_edge(prereq, course)
                    
                    # Add newly found courses to the queue for further processing
                    if not prereq.startswith("OR_GROUP_"):
                        queue.append((prereq, current_depth + 1))
    
    def visualize(self, target_course=None, save_path=None):
        """
        Visualize the prerequisite graph.
        
        Args:
            target_course: The course to highlight as the target
            save_path: Path to save the image instead of displaying it
        """
        if not self.G.nodes():
            print("No graph to visualize. Build the graph first.")
            return
            
        plt.figure(figsize=(12, 10))
        
        # Create a hierarchical layout
        pos = nx.spring_layout(self.G, seed=42)
        
        # Draw regular nodes (courses)
        course_nodes = [node for node in self.G.nodes() if not node.startswith("OR_GROUP_")]
        nx.draw_networkx_nodes(self.G, pos, 
                               nodelist=course_nodes,
                               node_color='skyblue', 
                               node_size=2000, 
                               alpha=0.8)
        
        # Highlight the target course
        if target_course and target_course in self.G.nodes():
            nx.draw_networkx_nodes(self.G, pos,
                                  nodelist=[target_course],
                                  node_color='green',
                                  node_size=2000,
                                  alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(self.G, pos, 
                               arrows=True,
                               arrowstyle='-|>',
                               width=1.5)
        
        # Draw labels for all nodes
        nx.draw_networkx_labels(self.G, pos, font_size=10)
        
        # Draw OR groups as dashed outlines
        for group_name, members in self.or_groups:
            if group_name in self.G.nodes():
                # Get positions of all members in the group
                member_positions = [pos[member] for member in members if member in pos]
                
                if member_positions:
                    # Create a polygon around all members
                    x_coords = [p[0] for p in member_positions]
                    y_coords = [p[1] for p in member_positions]
                    
                    # Add some padding
                    padding = 0.05
                    min_x, max_x = min(x_coords) - padding, max(x_coords) + padding
                    min_y, max_y = min(y_coords) - padding, max(y_coords) + padding
                    
                    # Create rectangle corners
                    rect_coords = np.array([
                        [min_x, min_y],
                        [max_x, min_y],
                        [max_x, max_y],
                        [min_x, max_y]
                    ])
                    
                    # Draw the rectangle with dashed lines
                    polygon = Polygon(rect_coords, closed=True, 
                                    fill=False, 
                                    linestyle='dashed',
                                    edgecolor='red',
                                    linewidth=2)
                    plt.gca().add_patch(polygon)
                    
                    # Add a label for the OR group
                    center_x = (min_x + max_x) / 2
                    center_y = (min_y + max_y) / 2
                    plt.text(center_x, min_y - 0.05, "OR", 
                             fontsize=12, color='red',
                             horizontalalignment='center')
                    
                    # Update the position of the OR group node to be below the group
                    pos[group_name] = (center_x, min_y - 0.1)
        
        plt.title(f"Prerequisite Graph for {target_course}")
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, format='png', dpi=300, bbox_inches='tight')
            print(f"Graph saved to {save_path}")
        else:
            plt.tight_layout()
            plt.show()
            
    def visualize_recursive_prerequisites(self, target_course, depth=2):
        """Convenience method to build and visualize in one step."""
        self.build_graph_for_course(target_course, depth)
        self.visualize(target_course)
        
    def save_course_graph(self, target_course, output_dir='course_graphs', depth=2):
        """Build and save the course graph to a file."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.build_graph_for_course(target_course, depth)
        save_path = os.path.join(output_dir, f"{target_course.replace(' ', '_')}_prereqs.png")
        self.visualize(target_course, save_path=save_path)
        return save_path

def search_courses(course_data, search_term):
    """Search for courses matching the search term."""
    search_term = search_term.upper()
    matches = []
    
    for course_id in course_data.keys():
        if search_term in course_id.upper():
            matches.append(course_id)
    
    return matches

def main():
    parser = argparse.ArgumentParser(description='Visualize course prerequisites.')
    parser.add_argument('course', nargs='?', help='Course ID to visualize (e.g., "COMPSCI 161")')
    parser.add_argument('--depth', type=int, default=2, help='Depth of prerequisite chain to visualize')
    parser.add_argument('--search', action='store_true', help='Search for courses matching the input')
    parser.add_argument('--save', action='store_true', help='Save the graph instead of displaying it')
    args = parser.parse_args()

    visualizer = CoursePrereqVisualizer(json_file='course_data_with_logical_prereqs.json')
    
    if args.search and args.course:
        matches = search_courses(visualizer.courses, args.course)
        if matches:
            print(f"Found {len(matches)} matching courses:")
            for course in matches:
                print(f"- {course}")
        else:
            print(f"No courses found matching '{args.course}'")
        return
    
    if not args.course:
        # Interactive mode
        while True:
            query = input("\nEnter course ID to visualize (or 'search TERM' to search, or 'exit' to quit): ")
            
            if query.lower() == 'exit':
                break
                
            if query.lower().startswith('search '):
                search_term = query[7:].strip()
                matches = search_courses(visualizer.courses, search_term)
                if matches:
                    print(f"Found {len(matches)} matching courses:")
                    for course in matches:
                        print(f"- {course}")
                else:
                    print(f"No courses found matching '{search_term}'")
            else:
                if query in visualizer.courses:
                    if args.save:
                        path = visualizer.save_course_graph(query, depth=args.depth)
                        print(f"Graph saved to {path}")
                    else:
                        print(f"Building graph for {query}...")
                        visualizer.visualize_recursive_prerequisites(query, depth=args.depth)
                else:
                    print(f"Course '{query}' not found. Use 'search' to find courses.")
    else:
        if args.course in visualizer.courses:
            if args.save:
                path = visualizer.save_course_graph(args.course, depth=args.depth)
                print(f"Graph saved to {path}")
            else:
                visualizer.visualize_recursive_prerequisites(args.course, depth=args.depth)
        else:
            print(f"Course '{args.course}' not found.")

if __name__ == "__main__":
    main()
