import numpy as np
from random import randint
from warnings import warn
import heapq
from path_planning.map import load_map


class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
        return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
        return self.f < other.f

    # defining greater than for purposes of heap queue
    def __gt__(self, other):
        return self.f > other.f


class PathPlanner:

    def __init__(self, map_name):
        map, node_density = load_map(map_name)
        self.map = map
        self.node_density = node_density

    def change_map(self, new_map):
        self.map = new_map

    def astar(self, start, end, allow_diagonal_movement=True):
        """
        Returns a list of tuples as a path from the given start to the given end in the given map
        :param map:
        :param start:
        :param end:
        :return:
        """

        # Create start and end node
        # If start is an obstacle, set start to nearest open node
        if self.map[start[0]][start[1]] != 0:
            start = self.find_closest_open_node(start)

        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0

        # If end is an obstacle, set end to nearest open node
        if self.map[end[0]][end[1]] != 0:
            end = self.find_closest_open_node(end)

        end_node = Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # heapify the open_list and Add the start node
        heapq.heapify(open_list)
        heapq.heappush(open_list, start_node)

        # Adding a stop condition
        outer_iterations = 0
        max_iterations = 20000  # (len(self.map[0]) * len(self.map) // 2)

        # what squares do we search
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
        if allow_diagonal_movement:
            adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),
                                (-1, -1), (-1, 1), (1, -1), (1, 1),)

        # Loop until you find the end
        while len(open_list) > 0:
            outer_iterations += 1

            if outer_iterations > max_iterations:
                # if we hit this point return the path such as it is
                # it will not contain the destination
                warn("giving up on pathfinding too many iterations")
                return self.__return_path(current_node)

            # Get the current node
            current_node = heapq.heappop(open_list)
            closed_list.append(current_node)

            # Found the goal
            if current_node == end_node:
                return self.__return_path(current_node)

            # Generate children
            children = []

            for new_position in adjacent_squares:  # Adjacent squares

                # Get node position
                node_position = (
                    current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                # Make sure within range
                if node_position[0] > (len(self.map) - 1) or node_position[0] < 0 or node_position[1] > (len(self.map[0]) - 1) or node_position[1] < 0:
                    continue

                # Make sure walkable terrain
                if self.map[node_position[0]][node_position[1]] != 0:
                    continue

                # Check diagonal movement is valid (i.e. they don't need to walk through a wall)
                # Diagonal move
                if abs(new_position[0]) - abs(node_position[0]) != 0 and abs(new_position[1]) - abs(node_position[1]) != 0:
                    left_node_x = node_position[0] - new_position[0]
                    left_node_y = node_position[1]
                    right_node_x = node_position[0]
                    right_node_y = node_position[1] - new_position[1]

                    # Check validity of nodes next to diagnonal
                    if self.map[left_node_x][left_node_y] != 0 or self.map[right_node_x][right_node_y] != 0:
                        continue

                # Create new node
                new_node = Node(current_node, node_position)

                # Append
                children.append(new_node)

            # Loop through children
            for child in children:

                # Child is on the closed list
                if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                    continue

                # Create the g, h and f values
                child.h = (((child.position[0] - end_node.position[0]) ** 2) + (
                    (child.position[1] - end_node.position[1]) ** 2)) ** 0.5

                # Diagonal move
                if abs(child.position[0]) - abs(child.parent.position[0]) != 0 and abs(child.position[1]) - abs(child.parent.position[1]) != 0:
                    child.g = current_node.g + 1.414
                else:
                    child.g = current_node.g + 1

                for cell in self.get_cell_radius(child.position[0], child.position[1]):
                    try:
                        if self.map[cell[0]][cell[1]] == 0:
                            child.f += 0.5
                    except:
                        pass

                child.f += child.g + child.h

                # Child is already in the open list
                if len([open_node for open_node in sorted(open_list) if child.position == open_node.position and child.f >= open_node.f]) > 0:
                    continue

                # Add the child to the open list
                heapq.heappush(open_list, child)

        warn("Couldn't get a path to destination")
        return None

    def get_cell_radius(self, x, y, distance=1):
        neighbours = []
        radius = np.array([(0, 1), (1, 0), (1, 1), (-1, -1),
                           (-1, 0), (0, -1), (1, -1), (-1, 1)]) * distance
        for elm in radius:
            neighbours.append((x+elm[0], y+elm[1]))
        return neighbours

    def find_closest_open_node(self, node):
        for distance in range(min(len(self.map), len(self.map[0]))):
            neighbours = self.get_cell_radius(node[0], node[1], distance)
            for neighbour in neighbours:
                try:
                    if self.map[neighbour[0]][neighbour[1]] == 0:
                        return neighbour
                except:
                    continue

    def __return_path(self, current_node):
        path = []
        current = current_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1]

    def __get_target_heading(self, node1, node2):
        # 0 degrees is toward right on printed map
        # +1 y is downwards
        # +1 x is towards right

        required_movement_direction_y = (node2[0] - node1[0])
        required_movement_direction_x = (node2[1] - node1[1])

        if required_movement_direction_x == 0 and required_movement_direction_y >= 1:
            target_heading = 270
        elif required_movement_direction_x >= 1 and required_movement_direction_y >= 1:
            target_heading = 315
        elif required_movement_direction_x >= 1 and required_movement_direction_y == 0:
            target_heading = 0
        elif required_movement_direction_x >= 1 and required_movement_direction_y <= -1:
            target_heading = 45
        elif required_movement_direction_x == 0 and required_movement_direction_y <= -1:
            target_heading = 90
        elif required_movement_direction_x <= -1 and required_movement_direction_y <= -1:
            target_heading = 135
        elif required_movement_direction_x <= -1 and required_movement_direction_y == 0:
            target_heading = 180
        elif required_movement_direction_x <= -1 and required_movement_direction_y >= 1:
            target_heading = 225

        return target_heading

    def __print_map(self, path, start, end):
        for step in path:
            self.map[step[0]][step[1]] = 2

            self.map[start[0]][start[1]] = 3
            self.map[end[0]][end[1]] = 4

        for col in self.map:
            line = []
            for row in col:
                if row == 1:
                    line.append("\u2588"*3)
                elif row == 0:
                    line.append(" . ")
                elif row == 2:
                    line.append(" # ")
                elif row == 3:
                    line.append(" O ")
                elif row == 4:
                    line.append(" x ")
                elif row == 5:
                    line.append(" L ")
            print("".join(line))

    def __map_angle_to_direction(self, heading_change):
        heading_change = round(8*(heading_change)/360, 0)

        if heading_change == 0 or heading_change == 8 or heading_change == -8:
            turn_direction = 'N'
        elif heading_change == 1 or heading_change == -7:
            turn_direction = 'NW'
        elif heading_change == 2 or heading_change == -6:
            turn_direction = 'W'
        elif heading_change == 3 or heading_change == -5:
            turn_direction = 'SW'
        elif heading_change == 4 or heading_change == -4:
            turn_direction = 'S'
        elif heading_change == 5 or heading_change == -3:
            turn_direction = 'SE'
        elif heading_change == 6 or heading_change == -2:
            turn_direction = 'E'
        elif heading_change == 7 or heading_change == -1:
            turn_direction = 'NE'

        return (turn_direction)

    def __translate_path(self, path):
        translated_path = []
        for step in path:
            translated_path.append(self.__translate_node(step))
        return (translated_path)

    def __translate_node(self, node):
        x_origin, y_origin = (0, 0)
        translated_x = ((node[1] + 1)/self.node_density)-x_origin
        translated_y = ((len(self.map)-node[0])/self.node_density)-y_origin
        translated_node = (translated_x, translated_y)
        return translated_node

    def calculate_next_direction(self, start, end, heading, offset, print_map=False, print_path=False):
        destination_reached = False

        # If user is within one cell of destination
        if end in self.get_cell_radius(start[0], start[1]):
            # User has arrived
            destination_reached = True
            return (None, destination_reached)

        # Determine Optimal Path
        path = self.astar(start, end)

        # Determine Required Heading
        # if user is not at start (due to start being obstacle)
        if start != path[0]:
            # required heading is towards start
            required_heading = self.__get_target_heading(start, path[0])
        else:
            # else required heading is towards next step
            required_heading = self.__get_target_heading(path[0], path[1])

        # Apply offset to current heading
        heading = heading + offset
        if heading >= 360:
            heading -= 360

        # Calculate change in heading required
        heading_change = required_heading - heading

        # Map change in heading to direction
        turn_direction = self.__map_angle_to_direction(heading_change)

        if print_map:
            self.__print_map(path, path[0], path[-1])

        if print_path:
            # Translate path back from nodes to location
            print(self.__translate_path(path))

        return (turn_direction, destination_reached)

# Usage Example
# pp = PathPlanner("foyer")
# pp.calculate_next_direction(start=(2, 14), heading=0, end=(31, 8), offset=0, print_map=True, print_path=True)
