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
        """Visualize the prerequisite graph with improved layout."""
        if not self.G.nodes():
            print("No graph to visualize. Build the graph first.")
            return
        
        plt.figure(figsize=(16, 12))
        
        # Choose a better layout algorithm based on graph size
        num_nodes = len(self.G.nodes())
        
        if num_nodes <= 15:
            # For small graphs, use a hierarchical layout
            try:
                # Try to use graphviz for best hierarchical layout
                pos = nx.nx_agraph.graphviz_layout(self.G, prog='dot', args='-Grankdir=LR')
            except:
                # Fall back to a custom layered approach if graphviz is not available
                pos = self._custom_layered_layout(target_course)
        else:
            # For larger graphs, use specialized layouts
            if num_nodes <= 30:
                # Medium-sized graphs use Kamada-Kawai for nice spacing
                pos = nx.kamada_kawai_layout(self.G)
            else:
                # Large graphs use ForceAtlas2 inspired layout
                pos = nx.spring_layout(self.G, k=1.5/np.sqrt(num_nodes), iterations=100, seed=42)
        
        # Increase spacing between nodes
        pos = {node: (x*1.5, y*1.5) for node, (x, y) in pos.items()}
        
        # Draw regular nodes (courses)
        course_nodes = [node for node in self.G.nodes() if not node.startswith("OR_GROUP_")]
        nx.draw_networkx_nodes(self.G, pos, 
                               nodelist=course_nodes,
                               node_color='skyblue', 
                               node_size=2500, 
                               alpha=0.8)
        
        # Highlight the target course
        if target_course in self.G.nodes():
            nx.draw_networkx_nodes(self.G, pos,
                                  nodelist=[target_course],
                                  node_color='green',
                                  node_size=3000,
                                  alpha=0.8)
        
        # Draw edges with arrows pointing TO the course that requires the prerequisite
        nx.draw_networkx_edges(self.G, pos, 
                               arrows=True,
                               arrowstyle='-|>',
                               width=1.5,
                               arrowsize=20,
                               edge_color='gray',
                               alpha=0.7)
        
        # Draw labels for all nodes with improved readability
        node_labels = {node: self._format_node_label(node) for node in self.G.nodes()}
        nx.draw_networkx_labels(self.G, pos, labels=node_labels, font_size=11, font_weight='bold')
        
        # Draw OR groups as dashed outlines with better formatting
        for group_name, members in self.or_groups:
            if group_name in self.G.nodes():
                # Get positions of all members in the group
                member_positions = [pos[member] for member in members if member in pos]
                
                if member_positions:
                    # Create a polygon around all members with more padding
                    x_coords = [p[0] for p in member_positions]
                    y_coords = [p[1] for p in member_positions]
                    
                    # Add generous padding
                    padding = 0.15
                    min_x, max_x = min(x_coords) - padding, max(x_coords) + padding
                    min_y, max_y = min(y_coords) - padding, max(y_coords) + padding
                    
                    # Create rounded rectangle corners
                    rect_coords = np.array([
                        [min_x, min_y],
                        [max_x, min_y],
                        [max_x, max_y],
                        [min_x, max_y]
                    ])
                    
                    # Draw the rectangle with dashed lines
                    polygon = Polygon(rect_coords, closed=True, 
                                    fill=True, 
                                    facecolor='mistyrose',
                                    linestyle='dashed',
                                    edgecolor='red',
                                    linewidth=2,
                                    alpha=0.2)
                    plt.gca().add_patch(polygon)
                    
                    # Add a more visible label for the OR group
                    center_x = (min_x + max_x) / 2
                    center_y = (min_y + max_y) / 2
                    plt.text(center_x, min_y - 0.1, "OR", 
                             fontsize=14, color='red', fontweight='bold',
                             bbox=dict(facecolor='white', alpha=0.7, edgecolor='red', boxstyle='round,pad=0.3'),
                             horizontalalignment='center')
        
        # Add title and improve overall appearance
        plt.title(f"Prerequisite Tree for {target_course}", fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout(pad=2.0)
        
        # Add a legend or explanation
        legend_text = "Green: Target Course\nBlue: Prerequisite Courses\nRed Dashed Box: 'OR' Relationship (any one course satisfies the requirement)"
        plt.figtext(0.01, 0.01, legend_text, fontsize=11, 
                   bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5'))
        
        if output_file:
            directory = os.path.dirname(output_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
            print(f"Graph saved to {output_file}")
        else:
            plt.tight_layout()
            plt.show()
    
    def _format_node_label(self, node):
        """Format node labels for better readability."""
        if node.startswith("OR_GROUP_"):
            return ""
        return node
    
    def _custom_layered_layout(self, target_course):
        """Create a custom layered layout when graphviz is not available."""
        # Create layers based on distance from target course
        layers = {}
        visited = set()
        
        # BFS to determine distance from target
        queue = [(target_course, 0)]  # (node, distance)
        visited.add(target_course)
        
        while queue:
            node, distance = queue.pop(0)
            if distance not in layers:
                layers[distance] = []
            layers[distance].append(node)
            
            # Process neighbors (prerequisites)
            for prereq in self.G.predecessors(node):
                if prereq not in visited:
                    queue.append((prereq, distance + 1))
                    visited.add(prereq)
        
        # Create positions based on layers
        pos = {}
        max_layer = max(layers.keys()) if layers else 0
        
        for layer_num, nodes in layers.items():
            # Reverse the layers so target is on the right
            x_pos = 1 - (layer_num / (max_layer + 1))
            
            # Distribute nodes vertically in their layer
            n_nodes = len(nodes)
            for i, node in enumerate(nodes):
                if n_nodes == 1:
                    y_pos = 0.5
                else:
                    y_pos = i / (n_nodes - 1) if n_nodes > 1 else 0.5
                pos[node] = (x_pos, y_pos)
        
        return pos

# Main code
if __name__ == "__main__":
    # Choose a course to visualize
    course_to_visualize = "IN4MATX 191B"  # Popular course with prerequisites
    output_dir = "course_graphs"
    output_file = os.path.join(output_dir, f"{course_to_visualize.replace(' ', '_')}_prereqs.png")
    max_depth = 10  # Maximum depth for recursion
    
    # Initialize the visualizer
    visualizer = CourseDAGVisualizer()
    
    # Build and visualize the complete prerequisite tree
    if visualizer.build_prereq_tree(course_to_visualize, max_depth):
        visualizer.visualize(course_to_visualize, output_file)
    else:
        print(f"Unable to build prerequisite tree for {course_to_visualize}")
        
    # Try another example with more complex prerequisites
    course_to_visualize = "COMPSCI 143B"
    output_file = os.path.join(output_dir, f"{course_to_visualize.replace(' ', '_')}_prereqs.png")
    
    if visualizer.build_prereq_tree(course_to_visualize, max_depth):
        visualizer.visualize(course_to_visualize, output_file)
    else:
        print(f"Unable to build prerequisite tree for {course_to_visualize}")
