import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import os

class CourseDAGVisualizer:
    def __init__(self, json_file='course_data_with_logical_prereqs.json'):
        """Initialize the visualizer with the course data."""
        self.courses = self.load_course_data(json_file)
        self.G = nx.DiGraph()
        self.or_groups = []
        self.group_counter = 0
        self.processed_courses = set()
        
    def load_course_data(self, json_file):
        """Load course data from JSON file."""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading course data: {e}")
            return {}
    
    def build_prereq_tree(self, target_course, max_depth=10):
        """
        Build a complete prerequisite tree for the target course.
        This recursively adds all prerequisites and their prerequisites.
        
        Args:
            target_course: The course to build the tree for
            max_depth: Maximum recursion depth to prevent infinite loops
        """
        # Reset the graph and tracking variables
        self.G = nx.DiGraph()
        self.or_groups = []
        self.group_counter = 0
        self.processed_courses = set()
        
        # Add the target course as the root node
        self.G.add_node(target_course)
        
        # Start the recursive process
        self._add_course_prerequisites(target_course, current_depth=0, max_depth=max_depth)
        
        # Return True if we found any prerequisites
        return len(self.G.nodes()) > 1
    
    def _add_course_prerequisites(self, course_id, current_depth=0, max_depth=10):
        """
        Recursively add prerequisites for a course to the graph.
        
        Args:
            course_id: Course ID to add prerequisites for
            current_depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent infinite loops
        """
        # Prevent infinite recursion or excessive depth
        if current_depth > max_depth or course_id in self.processed_courses:
            return
        
        self.processed_courses.add(course_id)
        
        # Skip if course doesn't exist in the data
        if course_id not in self.courses:
            print(f"Warning: Course {course_id} not found in the data.")
            return
        
        # Get the prerequisites structure for this course
        prereq_structure = self.courses[course_id].get("parsed_prerequisites", "N/A")
        
        # If no prerequisites, we're done with this branch
        if prereq_structure == "N/A" or not prereq_structure:
            return
        
        # Parse the prerequisites structure
        prereq_nodes = self._parse_prerequisites(prereq_structure, course_id)
        
        # Add edges from each prerequisite to the current course
        for prereq_node in prereq_nodes:
            self.G.add_edge(prereq_node, course_id)
            
            # If this is a real course (not an OR group), recursively add its prerequisites
            if not prereq_node.startswith("OR_GROUP_"):
                self._add_course_prerequisites(prereq_node, current_depth + 1, max_depth)
    
    def _parse_prerequisites(self, prereq_structure, target_course):
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
                    nodes = self._parse_prerequisites(prereq, target_course)
                    prereq_nodes.extend(nodes)
                return prereq_nodes
                
            elif "or" in prereq_structure:
                # OR relationship: any one course satisfies the requirement
                self.group_counter += 1
                group_name = f"OR_GROUP_{self.group_counter}"
                
                or_members = []
                for prereq in prereq_structure["or"]:
                    member_nodes = self._parse_prerequisites(prereq, target_course)
                    or_members.extend(member_nodes)
                
                # Store OR group for visualization
                if or_members:
                    self.or_groups.append((group_name, or_members))
                    return [group_name]  # Return the group as a single node
                return []
        
        print(f"Warning: Unknown prerequisite structure: {prereq_structure}")
        return []
    
    def visualize(self, target_course, output_file=None):
        """Visualize the prerequisite graph."""
        if not self.G.nodes():
            print("No graph to visualize. Build the graph first.")
            return
        
        plt.figure(figsize=(14, 10))
        
        # Use a hierarchical layout to better show the prerequisite flow
        # pos = nx.spring_layout(self.G, seed=42)  # Random layout
        # pip install pygraphviz networkx matplotlib numpy
        pos = nx.nx_agraph.graphviz_layout(self.G, prog='dot')  # Hierarchical layout
        
        # Draw regular nodes (courses)
        course_nodes = [node for node in self.G.nodes() if not node.startswith("OR_GROUP_")]
        nx.draw_networkx_nodes(self.G, pos, 
                               nodelist=course_nodes,
                               node_color='skyblue', 
                               node_size=2000, 
                               alpha=0.8)
        
        # Highlight the target course
        if target_course in self.G.nodes():
            nx.draw_networkx_nodes(self.G, pos,
                                  nodelist=[target_course],
                                  node_color='green',
                                  node_size=2000,
                                  alpha=0.8)
        
        # Draw edges with arrows pointing TO the course that requires the prerequisite
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
        
        plt.title(f"Full Prerequisite Tree for {target_course}")
        plt.axis('off')
        
        if output_file:
            directory = os.path.dirname(output_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
            print(f"Graph saved to {output_file}")
        else:
            plt.tight_layout()
            plt.show()

# Main code
if __name__ == "__main__":
    # MODIFY THIS SECTION TO SPECIFY THE COURSE YOU WANT TO VISUALIZE
    course_to_visualize = "IN4MATX 191B"  # Replace with your desired course ID
    output_file = "course_graphs/full_prereq_tree.png"  # Optional: specify None to display instead of saving
    max_depth = 10  # Maximum depth for recursion
    
    # Initialize the visualizer
    visualizer = CourseDAGVisualizer()
    
    # Build and visualize the complete prerequisite tree
    if visualizer.build_prereq_tree(course_to_visualize, max_depth):
        visualizer.visualize(course_to_visualize, output_file)
    else:
        print(f"Unable to build prerequisite tree for {course_to_visualize}")
