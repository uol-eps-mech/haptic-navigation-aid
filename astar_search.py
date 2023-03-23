import numpy as np
from random import randint
from warnings import warn
import heapq


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


def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path


def Origin_Offset():
    # Find the minimum x and y coord values from anchors JSON
    # HardCode for now
    Min_x = -2.3
    Min_y = -0.8
    return (Min_x, Min_y)


def get_currentlocation(maze, node_density):
    # TODO: will need to pull from Rego's data
    rand_start = (randint(0, (len(maze) - 1))*2, randint(0, (len(maze) - 1))*2)
    start = (rand_start[0]//node_density, rand_start[1]//node_density)
    return start


def get_goal(maze, node_density):
    # TODO: will need to pull from Kaif's data
    incomplete = True
    while incomplete:
        rand_end = (randint(0, (len(maze) - 1))*2,
                    randint(0, (len(maze) - 1))*2)
        end = (rand_end[0]//node_density, rand_end[1]//node_density)

        if maze[end[0]][end[1]] != 0:
            continue
        else:
            incomplete = False

    return end


def get_current_heading():
    heading = randint(0, 360)
    return heading


def get_heading_needed(path):
    if len(path) == 1:
        target_heading = 0
    else:
        required_movement_direction_x = path[1][0] - path[0][0]
        required_movement_direction_y = path[1][1] - path[0][1]
        required_movement_direction = (
            required_movement_direction_x, required_movement_direction_y)

        if required_movement_direction == (0, 1):
            target_heading = 0
        elif required_movement_direction == (1, 1):
            target_heading = 45
        elif required_movement_direction == (1, 0):
            target_heading = 90
        elif required_movement_direction == (1, -1):
            target_heading = 135
        elif required_movement_direction == (0, -1):
            target_heading = 180
        elif required_movement_direction == (-1, -1):
            target_heading = 225
        elif required_movement_direction == (-1, 0):
            target_heading = 270
        elif required_movement_direction == (-1, 1):
            target_heading = 315
    return target_heading


def Regos_function(maze):

    Location_x = randint(0, (len(maze)-1)*10/2)/10
    Location_y = randint(0, (len(maze[0])-1)*10/2)/10
    Heading = randint(0, 360)

    return (Location_x, Location_y, Heading)


# def convert_to_map(path, x_max, y_max):
#     iteration = 0
#     for step in path:
#         path[iteration][0] = path[iteration][0]
#         path[iteration][1] =

#         iteraion += 1


def astar(maze, start, end, allow_diagonal_movement=True):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    :param maze:
    :param start:
    :param end:
    :return:
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list)
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = 512  # (len(maze[0]) * len(maze) // 2)

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
            return return_path(current_node)

        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Generate children
        children = []

        for new_position in adjacent_squares:  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[0]) - 1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Check diagonal movement is valid (i.e. they don't need to walk through a wall)
            if abs(new_position[0]) == abs(new_position[1]):  # Diagonal move
                left_node_x = node_position[0] - new_position[0]
                left_node_y = node_position[1]
                right_node_x = node_position[0]
                right_node_y = node_position[1] - new_position[1]

                # Check validity of nodes next to diagnonal
                if maze[left_node_x][left_node_y] != 0 or maze[right_node_x][right_node_y] != 0:
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

            # Create the f, g, and h values
            if abs(child.position[0]) == abs(child.position[1]):  # Diagonal move
                child.g = current_node.g + 1.414
            else:
                child.g = current_node.g + 1
            # child.g = current_node.g + 1 #TODO change to if statement for diagonals to be sqrt(2)

            child.h = (((child.position[0] - end_node.position[0]) **
                       2) + ((child.position[1] - end_node.position[1]) ** 2)) ** 0.5  # TODO the issue is there's a much greater bias towards h than g
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    warn("Couldn't get a path to destination")
    return None


def example(print_maze=False, print_path=False):
    destination_reached = False
    maze = [[0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],]

    node_density = 2

    # Start and end override for testing
    # start = (6, 0)
    # end = (1, 9)

    # Get X,Y,H from Rego's function
    # maze input only necessary for the rand gen
    [X, Y, H] = Regos_function(maze)

    start = (int(round(X*node_density, 0)), int(round(Y*node_density, 0)))

    end = get_goal(maze, node_density)

    # print("Start location is: {}".format(start))
    # print("End location is: {}".format(end))

    if start == end:
        destination_reached = True

    path = astar(maze, start, end)

    if print_maze:
        for step in path:
            maze[step[0]][step[1]] = 2

        maze[start[0]][start[1]] = 3
        maze[end[0]][end[1]] = 4

        for col in maze:
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
                    line.append(" X ")
            print("".join(line))

    # path = convert_to_map(path, len(maze[0]), len(maze))

    if print_path:
        print(path)

    # Heading calculations - Dont Delete

    required_heading = get_heading_needed(path)
    heading_change = round(8*(required_heading - H)/360, 0)
    # current_heading = round(8*get_heading()/360, 0)

    if heading_change == 0 or heading_change == 8 or heading_change == -8:
        turn_direction = 'N'
    elif heading_change == 1 or heading_change == -7:
        turn_direction = 'NE'
    elif heading_change == 2 or heading_change == -6:
        turn_direction = 'E'
    elif heading_change == 3 or heading_change == -5:
        turn_direction = 'SE'
    elif heading_change == 4 or heading_change == -4:
        turn_direction = 'S'
    elif heading_change == 5 or heading_change == -3:
        turn_direction = 'SW'
    elif heading_change == 6 or heading_change == -2:
        turn_direction = 'W'
    elif heading_change == 7 or heading_change == -1:
        turn_direction = 'NW'

    # print("current heading is: {} ".format(H))
    # print("desired heading is: {} ".format(required_heading))
    # print("heading change required is: {} ".format(heading_change))

    return (turn_direction, destination_reached)


Output = example()
print(Output)
