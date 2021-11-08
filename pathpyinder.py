# Gui wrapper library for tkinter
from modules import PySimpleGUI as sg
# Data structure used in A* algorithm
from modules import priority_queue as pq
# Data structure used as a queue/stack for BFS/DFS algorithms
from collections import deque
# Used to slow down pathfinding algos
from time import sleep
# Used in maze generation
from random import choice as random_choice
# Used to read and write settings.cfg
from json import (load as jsonload, dump as jsondump)
# Used to read and write settings.cfg
from os import (path as path, name as operating_system)



"""
 ######   ##        #######  ########     ###    ##        ######
##    ##  ##       ##     ## ##     ##   ## ##   ##       ##    ##
##        ##       ##     ## ##     ##  ##   ##  ##       ##
##   #### ##       ##     ## ########  ##     ## ##        ######
##    ##  ##       ##     ## ##     ## ######### ##             ##
##    ##  ##       ##     ## ##     ## ##     ## ##       ##    ##
 ######   ########  #######  ########  ##     ## ########  ######
"""
VERSION = '1.7.1'
OS = operating_system

MAZE_WIDTH = 51
MAZE_HEIGHT = 51
NODE_SIZE = 10

NODES = {}         # Dictionary of nodes in the grid with (x,y) tuples as keys
START_NODE = None  # Instance of Node. The node from which the algorithm starts
END_NODE = None    # Instance of Node. The node at which the maze is 'solved'

ALGO = 'Breadth-First Search'   # Pathfinding algorithm to use.
MODE = 'wall'                   # None, 'wall', 'path', 'start', 'end'
TEMP_DELAY = None               # Temporary variable to store original DELAY
DELAY = 0                       # Algorithm iteration delay (in milliseconds)
SPEED = None                    # Value of the speed slider
PAUSED = False                  # Flipped if the pause button is clicked

# Checking for user input on every loop iteration slows down the algorithms
# To avoid this, we will only check for user input every LOOP_CHECK iterations
# Because lower speeds require lower LOOP_CHECK values to avoid input delay,
# The speed slider will adjust LOOP_CHECK on a per-speed basis
LOOP_COUNT = 0
LOOP_CHECK = 0


COLORS = {                      # Dictionary of colors to use in Node.style()
    'empty': '#CCCCCC',         # Grey
    'wall': '#003333',          # Black
    'start': '#00CC00',         # Green
    'start_border': '#006000',  # Dark Green
    'end': '#FF3366',           # Red
    'end_border': '#890F1F',    # Dark Red
    'active': '#EFC700',        # Yellow
    'visited': '#999966',       # Olive
    'neighbor': '#96E8FF',      # Light Blue
    'solution': '#009900',      # Dark Green
    'error': '#FF6D70',         # Light red
    'black': '#000000',
    'white': '#FFFFFF',
}

DEFAULT_SETTINGS = {
    "default_maze": "None",
    "default_algorithm": "Breadth-First Search",
    "default_speed": 4,
    "maze_width": 51,
    "maze_height": 51,
    "node_size": 10
}



"""
##     ## ####
##     ##  ##
##     ##  ##
##     ##  ##
##     ##  ##
##     ##  ##
 #######  ####
 
##     ## ######## ##       ########  ######## ########   ######
##     ## ##       ##       ##     ## ##       ##     ## ##    ##
##     ## ##       ##       ##     ## ##       ##     ## ##
######### ######   ##       ########  ######   ########   ######
##     ## ##       ##       ##        ##       ##   ##         ##
##     ## ##       ##       ##        ##       ##    ##  ##    ##
##     ## ######## ######## ##        ######## ##     ##  ######
"""
def set_algo(new_algo: str) -> None:
    """Establishes which algorithm to use for the pathfinder. 
    Valid values for `new_algo` are: 
    `'Breadth-First Search'`: Breadth-first
    `'Depth-First Search'`: Depth-first
    `'Dijkstra'`: Dijkstra
    `'A* (A Star)'`: A*
    """
    global ALGO
    ALGO = new_algo
    algo_ref = {
        'Breadth-First Search': 'bfs',
        'Depth-First Search': 'dfs',
        'Dijkstra': 'dijkstra',
        'A* (A Star)': 'astar',
    }
    # Select the appropriate radio
    window[f'radio_algo_{algo_ref[new_algo]}'].update(value=True)
    # Print event
    print(f"Algorithm set to {algo_ref[new_algo].upper()}")
    
    
def set_draw_mode(draw_mode: str) -> None:
    """Establishes a draw mode. Valid values for draw_mode are:
    `'wall'`: Draw walls in the maze by clicking and dragging on the grid.
    `'path'`: Erase walls in the maze by clicking and dragging on the grid.
    `'start'`: Click somewhere on the grid to set a start point.
    `'end'`: Click somewhere on the grid to set an end point.
    """
    global MODE
    MODE = draw_mode
    # Depress all draw mode buttons
    window['maze_tools_wall'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_path'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_start'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_end'].update(button_color=('#000', '#f0f0f0'))
    # Windows only button relief styles:
    if OS == 'nt':
        window['maze_tools_wall'].Widget.configure(relief='raised')
        window['maze_tools_path'].Widget.configure(relief='raised')
        window['maze_tools_start'].Widget.configure(relief='raised')
        window['maze_tools_end'].Widget.configure(relief='raised')
        window['maze_tools_'+draw_mode].Widget.configure(relief='sunken')
    # Press the selected draw mode button
    window['maze_tools_'+draw_mode].update(button_color='white on grey')
    # Print event
    print(f"Draw mode set to '{draw_mode}'")


def reset() -> None:
    """
    Clears the solution from the maze and sets all nodes' `is_visited`, 
    and `is_active` flags to `False` via the `Node.reset()` method.
    """
    global PAUSED
    PAUSED = False
    for node in NODES.values():
        node.reset_node()
    MAZE.clear_solution()
    MAZE.bring_start_and_end_nodes_to_front()
    disable_element('controls_pause')
    disable_element('controls_next')
    enable_drawing_tools()
    enable_algo_radios()
    raise_button('controls_pause')
    enable_element('controls_solve')
    raise_button('controls_solve')
    set_draw_mode('wall')
    enable_menu(window)
    

def clear() -> None:
    """Empties the entire grid, leaving only path/empty nodes."""
    for node in NODES.values():
        node.make_empty_node()
    MAZE.clear_solution()
    disable_element('controls_pause')
    disable_element('controls_next')
    enable_drawing_tools()
    enable_algo_radios()
    global PAUSED
    PAUSED = False
    raise_button('controls_pause')
    enable_element('controls_solve')
    raise_button('controls_solve')
    set_draw_mode('wall')
    enable_menu(window)
    
    
def set_speed(speed: float) -> None:
    """Sets a delay (in milliseconds) between each algorithm iteration"""
    global DELAY
    global TEMP_DELAY
    global LOOP_CHECK
    global SPEED
    SPEED = int(speed)
    window['controls_speed_label'].update(value=f'Speed: {SPEED}')
    if SPEED == 1:
        DELAY = 1500
        TEMP_DELAY = 1500
        LOOP_CHECK = -1
    elif SPEED == 2:
        DELAY = 500
        TEMP_DELAY = 500
        LOOP_CHECK = -1
    elif SPEED == 3:
        DELAY = 100
        TEMP_DELAY = 100
        LOOP_CHECK = -1
    elif SPEED == 4:
        DELAY = 25
        TEMP_DELAY = 25
        LOOP_CHECK = -1
    elif SPEED == 5:
        DELAY = 0
        TEMP_DELAY = 0
        LOOP_CHECK = 10
    print(f'Delay set to: {DELAY}ms.')
    

def disable_menu(window) -> None:
    """Disables the window menu."""
    #menu = [['!File', ['Nothing']], 
    #       ['!Tools', ['Nothing']],
    #       ['!Settings', ['Nothing']]]
    #if window['main_menu'].MenuDefinition != menu:
    #    window['main_menu'].update(menu_definition=menu)
    #    window.refresh()
    pass
    
    
def enable_menu(window) -> None:
    """Enables the window menu."""
    #menu = [['File', ['Open Maze', 'Save Maze', 'Exit']], 
    #       ['Tools', ['Generate Maze', 'Fill Maze']],
    #       ['Settings', ['Runtime Info', 'Maze Dimensions', 'Defaults']]]
    #if window['main_menu'].MenuDefinition != menu:
    #    window['main_menu'].update(menu_definition=menu)
    #    window.refresh()
    pass


def raise_button(sg_key, colors=('#000', '#f0f0f0')) -> None:
    """
    Styles a button to be de-pressed.
    
    Args:
        `sg_key` (str): The PySimpleGUI Key for the button
        `button_color` (tuple or str): Colors for the button text and background
            Example: 'white on grey', ('#000', '#f0f0f0')
    """
    window[sg_key].update(button_color=colors)
    if OS == 'nt':
        window[sg_key].Widget.configure(relief='raised')
    

def recess_button(sg_key, colors=('#000', '#f0f0f0')) -> None:
    """
    Styles a button to be pressed
    
    Args:
        `sg_key` (str): The PySimpleGUI Key for the button
        `button_color` (tuple or str): Colors for the button text and background
            Example: 'white on grey', ('#000', '#f0f0f0')
    """
    window[sg_key].update(button_color=colors)
    if OS == 'nt':
        window[sg_key].Widget.configure(relief='sunken')
    
    
def disable_element(sg_key) -> None:
    """Disables a button."""
    window[sg_key].update(disabled=True)


def enable_element(sg_key) -> None:
    """Enables a button."""
    window[sg_key].update(disabled=False)
    
    
def enable_drawing_tools() -> None:
    """Enables the `wall`, `path`, `start, and `end` buttons in the UI and sets 
    the draw mode to 'wall'."""
    for button in ['maze_tools_wall', 'maze_tools_path', 
                   'maze_tools_start', 'maze_tools_end']: 
        enable_element(button)
    
    
def disable_drawing_tools() -> None:
    """Disables the `wall`, `path`, `start, and `end` buttons in the UI and sets
    the draw mode to `None`."""
    for button in ['maze_tools_wall', 'maze_tools_path', 
                   'maze_tools_start', 'maze_tools_end']: 
        window[button].update(disabled=True, button_color=('#000', '#f0f0f0'))


def enable_algo_radios() -> None:
    """Enables the algorithm selection radios."""
    for radio in ['radio_algo_bfs', 'radio_algo_dfs', 'radio_algo_astar']:
        enable_element(radio)


def disable_algo_radios() -> None:
    """Disables the algorithm selection radios."""
    for radio in ['radio_algo_bfs', 'radio_algo_dfs', 'radio_algo_astar']:
        disable_element(radio)



"""
   ###    ##        ######    ####### 
  ## ##   ##       ##    ##  ##     ##
 ##   ##  ##       ##        ##     ##
##     ## ##       ##   #### ##     ##
######### ##       ##    ##  ##     ##
##     ## ##       ##    ##  ##     ##
##     ## ########  ######    ####### 

#### ##    ## ########  ##     ## ########
 ##  ###   ## ##     ## ##     ##    ##
 ##  ####  ## ##     ## ##     ##    ##
 ##  ## ## ## ########  ##     ##    ##
 ##  ##  #### ##        ##     ##    ##
 ##  ##   ### ##        ##     ##    ##
#### ##    ## ##         #######     ##
"""
def read_algo_controls(timeout=None) -> tuple:
    """
    Reads inputs from the control panel while the algorithm is running.
    Returns `(False, event)` to continue running. 
    Returns `(True, event)` to break out of the algorithm loop.
    """
    event, values = window.read(timeout)
    # Break out of the function if it's just a timeout event
    if event == '__TIMEOUT__':
        return (False, event)
    
    global TEMP_DELAY
    global DELAY
    DELAY = TEMP_DELAY
    
    # Pause Button
    if event == 'controls_pause':
        print('Pause button clicked.')
        global PAUSED
        # Update button style
        if PAUSED:
            raise_button('controls_pause')
        elif not PAUSED:
            recess_button('controls_pause', 'white on grey')
        # Toggle the PAUSED boolean
        PAUSED = not PAUSED
        if PAUSED:
            # If paused, wait for additional input
            enable_element('controls_next')
            return read_algo_controls(timeout=None)
        else:
            disable_element('controls_next')
        return (False, event)
        
    # Next Button
    elif event == 'controls_next':
        TEMP_DELAY = DELAY
        DELAY = None
        return (False, event)
    
    # Speed Slider
    elif event == 'controls_speed_slider':
        set_speed(values['controls_speed_slider'])
        if PAUSED:
            return read_algo_controls(timeout=None)
        return (False, event)
        
    # Reset/Clear Buttons
    elif event == 'maze_tools_clear':
        clear()
        return (True, event)
    elif event == 'maze_tools_reset':
        reset()
        return (True, event)
    
    # Menu items will do nothing
    elif event in ('File', 'Tools', 'Settings', 
                   'Open Maze', 'Save Maze',
                   'Generate Maze', 'Fill Maze',
                   'Runtime Info', 'Maze Dimension', 'Defaults'):
        return (False, '__TIMEOUT__')
    
    # Log window event and values
    print("Event: \t", event)
    print("Values: ", values)
    return (False, event)


def check_for_input() -> bool:
    """
    Checks for and processes user input during maze solving.
    Also slows down the algorithm to the desired speed.
    """
    global LOOP_COUNT
    global LOOP_CHECK
    if LOOP_COUNT > LOOP_CHECK:
        interrupted, event = read_algo_controls(timeout=DELAY)
        if interrupted:
            LOOP_COUNT = 0
            return True
        if event in ('controls_next' or 'controls_speed_slider'):
            # Make sure controls are read on the next loop iteration
            LOOP_COUNT = LOOP_CHECK+1
        else:
            # Algorithm controls have been checked, reset LOOP_COUNT
            LOOP_COUNT = 0
    else:
        LOOP_COUNT += 1
        # Slow algorithm down according to delay
        sleep(DELAY/1000)
    window.refresh()
    return False


"""
########  ########  ######       ####       ########  ########  ######
##     ## ##       ##    ##     ##  ##      ##     ## ##       ##    ##
##     ## ##       ##            ####       ##     ## ##       ##
########  ######    ######      ####        ##     ## ######    ######
##     ## ##             ##    ##  ## ##    ##     ## ##             ##
##     ## ##       ##    ##    ##   ##      ##     ## ##       ##    ##
########  ##        ######      ####  ##    ########  ##        ######
"""
def bfs_dfs() -> None:
    """
    Traverses the maze using a breadth-first or depth-first search algorithm.
    The two are the same except for the underlying data structure used. 
    Breadth-first uses a queue (first in, first out).
    Depth first uses a stack (last in, first out).
    """
    global LOOP_COUNT
    global LOOP_CHECK
    interrupted = False
    # use a stack suitable for both bfs and dfs, 
    # allowing for both lifo and fifo operations
    stack = deque([])
    # add the starting node to the stack
    stack.append(START_NODE)
    
    # as long as the stack has a node
    while stack:
        # set the top node as the currently active node
        current_node = stack.pop()
        current_node.make_active_node()
        
        # Checks for and processes user input 
        # every LOOP_CHECK iterations of this loop
        interrupted = check_for_input()
        if interrupted:
            break
        
        # flag the current node as active
        # check if it's the end node
        if current_node.is_end_node:
            break
        # for all valid neighbor nodes:
        # (in-bound nodes that are not walls, and have not been visited)
        neighbors = current_node.get_neighbors()
        if not neighbors:
            print(f'No neighbors at {current_node.loc}')
            current_node.make_visited_node()
        else:
            for neighbor in neighbors:
                # mark the neighbor as visited and style as neighbor
                neighbor.make_neighbor_node()
                # mark the current node as visited
                current_node.make_visited_node()
                # print(f'{current_node.loc} visited.')
                neighbor.parent = current_node
                
                # add the neighbor to a queue
                if ALGO[0] == 'B': # BFS, use queue: first in, first out
                    stack.appendleft(neighbor)
                else: # DFS, use stack: last in, first out
                    stack.append(neighbor)
    
    # Mark the solution path
    if not interrupted: MAZE.highlight_solution(current_node)



"""
########  ####       ## ##    ##  ######  ######## ########     ###
##     ##  ##        ## ##   ##  ##    ##    ##    ##     ##   ## ##
##     ##  ##        ## ##  ##   ##          ##    ##     ##  ##   ##
##     ##  ##        ## #####     ######     ##    ########  ##     ##
##     ##  ##  ##    ## ##  ##         ##    ##    ##   ##   #########
##     ##  ##  ##    ## ##   ##  ##    ##    ##    ##    ##  ##     ##
########  ####  ######  ##    ##  ######     ##    ##     ## ##     ##
"""
def dijkstra() -> None:
    """Finds the solution to the maze using Dijkstra's algorithm.
    """
    interrupted = False
    
    # Initialize an updateable priority queue with the start node, at priority 0
    # The 'keys' for the queue will be the coordinates for the nodes
    queue = pq.UpdateableQueue()
    queue.push(START_NODE.loc, 0)
    
    # As long as the queue isn't empty:
    while queue.__len__() > 0:
        
        # Get the highest priority node
        current_node = NODES[queue.pop()[0]]
        # Check to see if it's the end node
        if current_node.is_end_node:
            break
        # Mark it as visited
        current_node.make_active_node()
        window.refresh()
        
        # Checks for and processes user input 
        # every LOOP_CHECK iterations of this loop
        interrupted = check_for_input()
        if interrupted:
            break
        
        # Get all valid neighbor nodes of that node
        neighbors = current_node.get_neighbors()
        # If there are no neighbors, mark that node as visited
        if not neighbors:
            print(f'No neighbors at {current_node.loc}')
            current_node.make_visited_node()
        # If there are neighbors,
        else:
            # For each neighbor:
            for neighbor in neighbors:
                # Mark that neighbor as visited, and color it blue
                neighbor.make_neighbor_node()
                # Calculate the distance of that node to the start node
                min_distance = min(neighbor.distance, current_node.distance + 1)
                if min_distance != neighbor.distance:
                    neighbor.distance = min_distance
                    # Change queue priority for nieghbor since it's now closer
                    queue.push(neighbor.loc, neighbor.distance)
                    # Set the current node as the parent node for each neighbor
                    neighbor.parent = current_node
        # Mark the current node as visited
        current_node.make_visited_node()
            
    # Mark the solution path
    if not interrupted: MAZE.highlight_solution(current_node)



"""
   ###             ######  ########    ###    ########
  ## ##           ##    ##    ##      ## ##   ##     ##
 ##   ##          ##          ##     ##   ##  ##     ##
##     ## #######  ######     ##    ##     ## ########
#########               ##    ##    ######### ##   ##
##     ##         ##    ##    ##    ##     ## ##    ##
##     ##          ######     ##    ##     ## ##     ##
"""
def astar() -> None:
    """Finds the solution to the maze using the A-star (A*) algorithm."""
    interrupted = False
    
    # Initialize an updateable priority queue with the start node, at priority 0
    # The 'keys' for the queue will be the coordinates for the nodes
    queue = pq.UpdateableQueue()
    queue.push(START_NODE.loc, 0)
    
    # As long as the queue isn't empty:
    while queue.__len__() > 0:
        
        # Get the highest priority node
        current_node = NODES[queue.pop()[0]]
        # Check to see if it's the end node
        if current_node.is_end_node:
            break
        # Mark it as visited
        current_node.make_active_node()
        window.refresh()
        
        # Checks for and processes user input 
        # every LOOP_CHECK iterations of this loop
        interrupted = check_for_input()
        if interrupted:
            break
        
        # Get all valid neighbor nodes of that node
        neighbors = current_node.get_neighbors()
        # If there are no neighbors, mark that node as visited
        if not neighbors:
            print(f'No neighbors at {current_node.loc}')
            current_node.make_visited_node()
        # If there are neighbors,
        else:
            # For each neighbor:
            for neighbor in neighbors:
                # Mark that neighbor as visited, and color it blue
                neighbor.make_neighbor_node()
                # Set distance to be distance from the neighbor to end node
                neighbor.distance = (abs(END_NODE.x - neighbor.x) + 
                                     abs(END_NODE.y - neighbor.y))
                # Update the queue with the new distance. 
                # queue.push() ADDS a new entry, OR UPDATES an existing one
                queue.push(neighbor.loc, neighbor.distance)
                # Establish parent node
                neighbor.parent = current_node
                
        # Mark the current node as visited
        current_node.make_visited_node()
            
    # Mark the solution path
    if not interrupted: MAZE.highlight_solution(current_node)


"""
 ######   #######  ##       ##     ## ######## ########
##    ## ##     ## ##       ##     ## ##       ##     ##
##       ##     ## ##       ##     ## ##       ##     ##
 ######  ##     ## ##       ##     ## ######   ########
      ## ##     ## ##        ##   ##  ##       ##   ##
##    ## ##     ## ##         ## ##   ##       ##    ##
 ######   #######  ########    ###    ######## ##     ##
"""
        
def solve_maze() -> None:
    """Solves the current maze using the selected algorithm."""
    # Check to make sure there's a start and end node
    if START_NODE and END_NODE:
        # Disable UI elements that can't be used while solving
        disable_menu(window)
        disable_element('controls_solve')
        disable_drawing_tools()
        disable_algo_radios()
        # Enable UI elements that can only be used while solving
        enable_element('controls_pause')
        recess_button('controls_solve')
        
        print('*'*40)
        print(f'Solve started via {ALGO.upper()} algorithm.')
        print('*'*40)
        
        # Run algorithm
        if ALGO in ('Breadth-First Search', 'Depth-First Search'):
            bfs_dfs()
        elif ALGO == 'Dijkstra':
            dijkstra()
        elif ALGO == 'A* (A Star)':
            astar()
            
        # Disable elements that can't be used while not solving
        disable_element('controls_pause')
        raise_button('controls_pause')
        disable_element('controls_next')
        
        # Enable elements that can only be used while not solving
        enable_menu(window)
                
    # Show a popup message if there's not both a start and end node
    else:
        sg.popup('The maze needs a start and and end node for a solvable maze.', 
                 'Set these nodes with the "Start Node" and "End Node" buttons')




"""
 #######  ########  ######## ##    ##    ##     ##    ###    ######## ########
##     ## ##     ## ##       ###   ##    ###   ###   ## ##        ##  ##
##     ## ##     ## ##       ####  ##    #### ####  ##   ##      ##   ##
##     ## ########  ######   ## ## ##    ## ### ## ##     ##    ##    ######
##     ## ##        ##       ##  ####    ##     ## #########   ##     ##
##     ## ##        ##       ##   ###    ##     ## ##     ##  ##      ##
 #######  ##        ######## ##    ##    ##     ## ##     ## ######## ########
"""
def open_maze_file(filename: str) -> bool:
    """
    Loads a maze from a txt file. 
    Integer values represent nodes types:
    `'█'`: Path node
    `' '`: Wall node
    `'S'`: Start node
    `'E'`: End node
    """
    
    # TODO: parse maze file and make sure it's valid
    def valid_maze_file(filename: str):
        """Checks for validity of the maze file."""
        if filename and filename != 'None':
            return True
        else:
            return False
    
    if valid_maze_file(filename):
        try:
            print(f'Open maze file: {filename}')
            # clear out the existing maze
            clear()
            
            # get the width and height of the new maze
            with open(f'{filename}', 'r', encoding='utf8') as new_maze:
                # Read the first line
                # Subtract 1 from line length to account for newline character
                width = len(new_maze.readline())-1  
                # Read the total number of lines
                # add 1 to account for last line already being read
                height = len(new_maze.readlines())+1
            
            # resize the graph to accommodate new maze size
            MAZE.resize_maze(width, height)
            
            # modify nodes based on characters read from maze file
            with open(f'{filename}', 'r', encoding='utf8') as new_maze:
                x = 0 # x coordinate
                y = 0 # y coordinate
                for line in new_maze.readlines():
                    for char in line:
                        if char == ' ':
                            NODES[(x,y)].make_empty_node()
                        elif char == '█':
                            NODES[(x,y)].make_wall_node()
                        elif char == 'S':
                            NODES[(x,y)].make_start_node()
                        elif char == 'E':
                            NODES[(x,y)].make_end_node()
                        # reset the x coordinate at the end of each line
                        x = x+1 if x < width else 0
                    y += 1
            MAZE.bring_start_and_end_nodes_to_front()
        except:
            sg.popup('Error loading maze.')
            clear()



"""
 ######     ###    ##     ## ########    ##     ##    ###    ######## ########
##    ##   ## ##   ##     ## ##          ###   ###   ## ##        ##  ##
##        ##   ##  ##     ## ##          #### ####  ##   ##      ##   ##
 ######  ##     ## ##     ## ######      ## ### ## ##     ##    ##    ######
      ## #########  ##   ##  ##          ##     ## #########   ##     ##
##    ## ##     ##   ## ##   ##          ##     ## ##     ##  ##      ##
 ######  ##     ##    ###    ########    ##     ## ##     ## ######## ########
"""
def save_maze_file(filename: str) -> bool:
    """Saves the maze to a .txt file."""
    if not filename:
        return False
    
    # list that stores the maze
    maze_to_write = []
    for col in range(MAZE_HEIGHT):
        row_list = []
        for row in range(MAZE_WIDTH):
            if NODES[(row, col)].is_start_node:
                row_list.append('S')
            elif NODES[(row, col)].is_end_node:
                row_list.append('E')
            elif NODES[(row, col)].is_empty:
                row_list.append(' ')
            elif NODES[(row, col)].is_wall:
                row_list.append('█')
        maze_to_write.append(row_list)
    
    # remove trailing space from the last node in each row
    for row in maze_to_write:
        row[MAZE_WIDTH-1] = row[MAZE_WIDTH-1][0]
        
    # write maze_to_write to a file
    with open(f'{filename.name}', 'w', encoding="utf-8") as file_to_write:
        for row in range(MAZE_HEIGHT):
            file_to_write.writelines(maze_to_write[row])
            # write a new line at the end of each row, 
            # but not at the end of the last line
            if row != MAZE_HEIGHT-1:
                file_to_write.write('\n')
            
    print(f'Save maze to: {filename}')
    
    
    
"""
 ######   ######## ##    ## ######## ########     ###    ######## ########
##    ##  ##       ###   ## ##       ##     ##   ## ##      ##    ##
##        ##       ####  ## ##       ##     ##  ##   ##     ##    ##
##   #### ######   ## ## ## ######   ########  ##     ##    ##    ######
##    ##  ##       ##  #### ##       ##   ##   #########    ##    ##
##    ##  ##       ##   ### ##       ##    ##  ##     ##    ##    ##
 ######   ######## ##    ## ######## ##     ## ##     ##    ##    ########
 
##     ##    ###    ######## ########
###   ###   ## ##        ##  ##
#### ####  ##   ##      ##   ##
## ### ## ##     ##    ##    ######
##     ## #########   ##     ##
##     ## ##     ##  ##      ##
##     ## ##     ## ######## ########
"""
def generate_maze() -> None:
    """
    Generates a new maze via depth-first search algorithm, 
    starting at a random point in the maze.
    """
    print('Generate Maze')
    clear()
    
    
    def pick_maze_generator_starting_point() -> tuple:
        """Picks and returns a starting point for the maze generator."""
        # List of permissible starting points for the x and y coordinates
        coords_x = [x for x in range(1, MAZE_WIDTH-1, 2)]
        coords_y = [x for x in range(1, MAZE_HEIGHT-1, 2)]
        return (random_choice(coords_x), random_choice(coords_y))
    
    
    def connect_nodes(current_node, old_node) -> None:
        """Draws a path between two nodes."""
        x_diff = current_node.x - old_node.x
        y_diff = current_node.y - old_node.y
        if x_diff == -2:
            NODES[(current_node.x+1, current_node.y)].make_empty_node()
        elif x_diff == 2:
            NODES[(current_node.x-1, current_node.y)].make_empty_node()
        elif y_diff == -2:
            NODES[(current_node.x, current_node.y+1)].make_empty_node()
        elif y_diff == 2:
            NODES[(current_node.x, current_node.y-1)].make_empty_node()
        
        
    # Populates existing maze with wall nodes
    MAZE.clear_solution()
    MAZE.fill_maze()
    # Set a start node
    NODES[(1,0)].make_start_node()
    # Set an end node
    if MAZE_WIDTH % 2 == 0: # If the maze width is an even number
        # The last two columns of nodes will be walls, 
        # so the end node has to be two nodes away from the rightmost edge
        NODES[(MAZE_WIDTH-3, MAZE_HEIGHT-1)].make_end_node()
    else:
        NODES[(MAZE_WIDTH-2, MAZE_HEIGHT-1)].make_end_node()
    # Make sure a path to the end node exists
    if MAZE_HEIGHT % 2 == 0:
        NODES[(END_NODE.x, END_NODE.y-1)].make_empty_node()
    
    # Initialize stack
    stack = []
    stack.append(NODES[pick_maze_generator_starting_point()])
    
    # Tracks what the previous node was
    old_node = None
    
    # As long as there's a node in the stack
    while stack:
        # Use the last node in the stack
        current_node = stack[len(stack)-1]
        # Connect the current node and old node with a path
        if old_node:
            connect_nodes(old_node, current_node)
        current_node.make_empty_node()
        window.refresh()
        
        # Store the current node
        old_node = current_node
        
        # Get the potential directions to go in
        directions = current_node.get_directions_to_dig()
        
        # If there's nowhere for the current node to go, 
        # remove it from the stack and restart the loop
        if not directions:
            stack.pop()
            continue
        
        # Choose a random direction to go in
        direction = random_choice(directions)
        
        # Append the node one farther than the chosen node to the stack
        x_diff = current_node.x - direction.x
        y_diff = current_node.y - direction.y
        if x_diff == -1: # append the right node
            stack.append(NODES[(current_node.x+2, current_node.y)])
        elif x_diff == 1: # append left node
            stack.append(NODES[(current_node.x-2, current_node.y)])
        elif y_diff == -1: # append bottom node
            stack.append(NODES[(current_node.x, current_node.y+2)])
        elif y_diff == 1: # append top node
            stack.append(NODES[(current_node.x, current_node.y-2)])
    
    MAZE.bring_start_and_end_nodes_to_front()
            
            
            
"""
 ######     ###    ##     ## ########       ###    ##    ## ########
##    ##   ## ##   ##     ## ##            ## ##   ###   ## ##     ##
##        ##   ##  ##     ## ##           ##   ##  ####  ## ##     ##
 ######  ##     ## ##     ## ######      ##     ## ## ## ## ##     ##
      ## #########  ##   ##  ##          ######### ##  #### ##     ##
##    ## ##     ##   ## ##   ##          ##     ## ##   ### ##     ##
 ######  ##     ##    ###    ########    ##     ## ##    ## ########
 
##        #######     ###    ########
##       ##     ##   ## ##   ##     ##
##       ##     ##  ##   ##  ##     ##
##       ##     ## ##     ## ##     ##
##       ##     ## ######### ##     ##
##       ##     ## ##     ## ##     ##
########  #######  ##     ## ########

 ######  ######## ######## ######## #### ##    ##  ######    ######
##    ## ##          ##       ##     ##  ###   ## ##    ##  ##    ##
##       ##          ##       ##     ##  ####  ## ##        ##
 ######  ######      ##       ##     ##  ## ## ## ##   ####  ######
      ## ##          ##       ##     ##  ##  #### ##    ##        ##
##    ## ##          ##       ##     ##  ##   ### ##    ##  ##    ##
 ######  ########    ##       ##    #### ##    ##  ######    ######
"""
def read_settings():
    """
    Reads settings from settings.cfg. 
    Resorts to DEFAULT_SETTINGS if settings.cfg is not found.
    """
    # Try loading settings.cfg from pathypyinder.py's directory
    settings_file_path = path.join(path.dirname(__file__), 'settings.cfg')
    try:
        with open(settings_file_path, 'r') as settings_file:
            current_saved_settings = jsonload(settings_file)
    # If there's a problem, show a popup saying there was no setting file found
    # and write settings.cfg file to that directory with the default settings
    except Exception as e:
        settings_file_path = path.join(path.dirname(__file__), 'settings.cfg')
        sg.popup('No settings file found.',
                 'New file automatically created at:', 
                 f'{settings_file_path}', keep_on_top=True)
        with open(settings_file_path, 'w') as settings_file:
            jsondump(DEFAULT_SETTINGS, settings_file, indent=4)
        current_saved_settings = DEFAULT_SETTINGS
    return current_saved_settings


def save_settings(settings):
    """Saves user inputted settings to settings.cfg"""
    # Reference dictionary that links the settings dict passed to the function 
    # to valid settings keys that can be read on initialization
    settings_dict = {
        # The passed settings parameter will have the below keys:
        "default_settings_default_maze": "default_maze",
        "default_settings_default_algorithm": "default_algorithm",
        "default_settings_default_speed": "default_speed",
        "default_settings_maze_width": "maze_width",
        "default_settings_maze_height": "maze_height",
        "default_settings_maze_node_size": "node_size"
    }
    # Populate a new settings dictionary
    parsed_settings = {}
    # For every setting in settings
    for setting in settings:
        # If that setting is a key in settings_dict
        if setting in settings_dict:
            # If that setting has a value
            if settings[setting]:
                # Add it to parsed_settings
                parsed_settings[settings_dict[setting]] = settings[setting]
            else:
                # Otherwise, add that setting to parsed_settings 
                # from the default settings global variable
                parsed_settings[settings_dict[setting]] = DEFAULT_SETTINGS[settings_dict[setting]]
    
    # Write the settings in pathypinder.py's directory to settings.cfg
    with open(path.join(path.dirname(__file__), 'settings.cfg'), 'w') as settings_file:
        jsondump(parsed_settings, settings_file, indent=4)
        
        
def apply_settings(settings_file, defaults):
    """Loads settings used to initialize the grid."""
    try:
        with open(settings_file, 'r') as f:
            read_settings = jsonload(f)
        print(f'Opening settings: {settings_file}')
        print(read_settings)
        final_settings = read_settings
    except:
        print(f'Could not open settings file: {settings_file}',
              '\nResorting to defaults...')
        print(defaults)
        final_settings = defaults
    
    # Set speed
    window['controls_speed_slider'].update(value=final_settings["default_speed"])
    set_speed(final_settings["default_speed"])
    # Set algorithm
    set_algo(final_settings["default_algorithm"])
    # Open maze
    if final_settings["default_maze"] != "None":
        open_maze_file(final_settings["default_maze"])
    else:
        MAZE.resize_maze(final_settings["maze_width"], 
                         final_settings["maze_height"], 
                         final_settings["node_size"])



"""
##    ##  #######  ########  ########
###   ## ##     ## ##     ## ##
####  ## ##     ## ##     ## ##
## ## ## ##     ## ##     ## ######
##  #### ##     ## ##     ## ##
##   ### ##     ## ##     ## ##
##    ##  #######  ########  ########

 ######  ##          ###     ######   ######
##    ## ##         ## ##   ##    ## ##    ##
##       ##        ##   ##  ##       ##
##       ##       ##     ##  ######   ######
##       ##       #########       ##       ##
##    ## ##       ##     ## ##    ## ##    ##
 ######  ######## ##     ##  ######   ######
"""
class Node(object):
    """
    Creates a maze node on the window graph at `(location[0], location[1])`.
    Nodes are represented as squares of `NODE_SIZE` pixels wide on the graph.
    """
    def __init__(self, maze: str, location: tuple) -> None:
        self.maze = maze                    # window graph object
        self.x = location[0]                # x coordinate    
        self.y = location[1]                # y coordinate
        self.loc = location                 # tuple of (x,y)
        
        # Status attributes
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = False
        self.is_end_node = False
        self.is_visited = False
        self.is_active = False
        
        # List of all surrounding node locations
        self.surrounding_locations = (
            (self.x, self.y+1),     # top
            (self.x+1, self.y+1),   # top-right
            (self.x+1, self.y),     # right
            (self.x+1, self.y-1),   # bottom-right
            (self.x, self.y-1),     # bottom
            (self.x-1, self.y-1),   # bottom-left
            (self.x-1, self.y),     # left
            (self.x-1, self.y+1),   # top-left
        )
        
        # parent node for backtracking and highlighting maze solution
        self.parent = None
        # distance attribute of the node (used in astar algorithm)
        self.distance = float('inf')
        
        # Draw the node on the graph and store the drawn figure in the self.id
        self.id = maze.draw_rectangle(top_left=(self.x*NODE_SIZE, 
                                                self.y*NODE_SIZE), 
                                      bottom_right=(self.x*NODE_SIZE+NODE_SIZE, 
                                                    self.y*NODE_SIZE+NODE_SIZE),
                                      fill_color=COLORS['empty'],
                                      line_color='#fff',
                                      line_width=1)
        
        # Add the node to the global nodes dictionary
        NODES[(self.x, self.y)] = self
        # print(f'Node created at {self.x}, {self.y}. Node id: {self.id}')


    def get_center(self) -> tuple:
        """Returns the graph coordinates of the center of the node."""
        return (self.x * NODE_SIZE + (NODE_SIZE/2),
                self.y * NODE_SIZE + (NODE_SIZE/2))
        
    
    def is_next_to(self, node) -> bool:
        """Returns `True` if node is next to node passed as parameter."""
        if node:
            if self.loc in node.surrounding_locations:
                return True
        return False
        

    def style(self, color, border_color='#fff', border_width=1, 
              send_to_back=False):
        """
        Updates a node color.

        Args:
            `color` (str: Optional): Hexidecimal string of a color. 
                E.g. `'#FFF'` or `'#2D2D2D'`
            `border_color` (str: Optional): Hexidecimal string of a color.
            `border_width` (int: Optional): Width of the border in pixels.
        """
        self.maze.delete_figure(self.id)
        self.id = self.maze.draw_rectangle(
                        top_left=(self.x*NODE_SIZE, 
                                  self.y*NODE_SIZE), 
                        bottom_right=(self.x*NODE_SIZE+NODE_SIZE, 
                                      self.y*NODE_SIZE+NODE_SIZE),
                        fill_color=color,
                        line_color=border_color,
                        line_width=border_width)
        if send_to_back:
            MAZE.send_figure_to_back(self.id)
    

    def get_neighbors(self) -> list:
        """
        Returns a list in-bound, accessible, non-visited neighbor nodes.
        Neighbor nodes are nodes that are above, below, left, or right 
        of the node this method was called on.
        """
        neighbors = []  
        if self.y != 0:
            neighbors.append(NODES[(self.x, self.y-1)]) # top
        # subtract 1 from MAZE_WIDTH because location indexes start at 0
        if self.x != MAZE_WIDTH-1: 
            neighbors.append(NODES[(self.x+1, self.y)]) # right
        # subtract 1 from MAZE_HEIGHT because location indexes start at 0
        if self.y != MAZE_HEIGHT-1: 
            neighbors.append(NODES[(self.x, self.y+1)]) # bottom
        if self.x != 0:
            neighbors.append(NODES[(self.x-1, self.y)]) # left
        # Prune neighbors list to remove visited nodes and wall nodes
        return [node for node in neighbors if not node.is_wall and not node.is_visited]
    
    
    def get_directions_to_dig(self) -> list:
        """
        Returns a list of nodes that can be emptied during maze generation. 
        Viable node requirements:
            1. Node direction + 1 must not be on the edge of the maze.
            2. Node direction + 1 must not already be an empty node.
        """
        # Immediate neighbor nodes
        neighbors = [
            NODES[(self.x, self.y+1)],  # top
            NODES[(self.x+1, self.y)],  # right
            NODES[(self.x, self.y-1)],  # bottom
            NODES[(self.x-1, self.y)],  # left
            ]
        # Look ahead one node in that direction and check for edges or paths
        # Node direction + 1 must not be on the edge of the maze.
        # Node direction + 1 must not already be an empty node.
        if self.y+2 > MAZE_HEIGHT-2 or NODES[(self.x, self.y+2)].is_empty:
            neighbors[0] = False
        if self.x+2 > MAZE_WIDTH-2 or NODES[(self.x+2, self.y)].is_empty:
            neighbors[1] = False
        if self.y-2 < 1 or NODES[(self.x, self.y-2)].is_empty:
            neighbors[2] = False
        if self.x-2 < 1 or NODES[(self.x-2, self.y)].is_empty:
            neighbors[3] = False
        
        # Return a list of neighbors that haven't been set to false
        return [neighbor for neighbor in neighbors if neighbor]
    

    def make_start_node(self) -> None:
        """Converts the node to a start node."""
        global START_NODE
        # Remove existing start node
        if START_NODE:
            START_NODE.make_empty_node()
        START_NODE = self
        self.style(COLORS['start'], 
                   border_color=COLORS['start_border'], 
                   border_width=4)
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = True
        self.is_end_node = False
        self.distance = 0
        self.start_distance = 0
        self.end_distance = float('inf')
    

    def make_end_node(self) -> None:
        """Converts the node to an end node."""
        global END_NODE
        # Remove existing end node
        if END_NODE:
            END_NODE.make_empty_node()
        END_NODE = self
        self.style(COLORS['end'], 
                   border_color=COLORS['end_border'], 
                   border_width=4)
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = False
        self.is_end_node = True
        self.distance = float('inf')
        self.start_distance = float('inf')
        self.end_distance = float('inf')
        

    def make_wall_node(self) -> None:
        """Converts the node to a wall node."""
        self.style(color=COLORS['wall'], 
                   border_color=COLORS['wall'])
        self.maze.send_figure_to_back(self.id)
        self.is_empty = False
        self.is_wall = True
        self.is_visited = False
        self.is_start_node = False
        self.is_end_node = False
        self.distance = float('inf')
        self.start_distance = float('inf')
        self.end_distance = float('inf')
        

    def make_empty_node(self) -> None:
        """Converts the node to an empty node."""
        self.style(COLORS['empty'])
        self.is_empty = True
        self.is_wall = False
        self.is_visited = False
        self.is_active = False
        self.distance = float('inf')
        self.start_distance = float('inf')
        self.end_distance = float('inf')
        if self.is_start_node:
            global START_NODE
            self.is_start_node = False
            START_NODE = None
        elif self.is_end_node:
            global END_NODE
            self.is_end_node = False
            END_NODE = None
        # If drawn next to a start or end node,
        # Make sure it's behind that node.
        if self.is_next_to(START_NODE):
            MAZE.bring_figure_to_front(START_NODE.id)
        if self.is_next_to(END_NODE):
            MAZE.bring_figure_to_front(END_NODE.id)
        
    
    def make_visited_node(self) -> None:
        """Flags and styles a node as visited."""
        self.style(COLORS['visited'])
        self.is_visited = True
        
    def make_neighbor_node(self) -> None:
        """Styles a node as a neighbor."""
        self.style(COLORS['neighbor'])
        self.is_visited = True

    def make_active_node(self) -> None:
        """Flags and styles a node as active."""
        self.style(COLORS['active'], 
                   COLORS['black'], 
                   border_width=3)
        self.is_active = True

    def make_solution_node(self) -> None:
        """Styles a node as part of the solution path."""
        self.style(COLORS['white'], COLORS['white'], send_to_back=True)

    def make_error_node(self) -> None:
        """Styles a node red to indicate an unsovable maze."""
        self.style(COLORS['error'])


    def reset_node(self):
        """
        Removes removes is_visited, and is_active flags. 
        Returns original node color.
        """
        # reset flags
        self.is_visited = False
        self.is_active = False
        # reset colors
        if self.is_start_node:
            self.make_start_node()
        elif self.is_end_node:
            self.make_end_node()
        elif self.is_wall:
            self.make_wall_node()
        elif self.is_empty:
            self.make_empty_node()
            
            
            
"""
##     ##    ###    ######## ########
###   ###   ## ##        ##  ##
#### ####  ##   ##      ##   ##
## ### ## ##     ##    ##    ######
##     ## #########   ##     ##
##     ## ##     ##  ##      ##
##     ## ##     ## ######## ########

 ######  ##          ###     ######   ######
##    ## ##         ## ##   ##    ## ##    ##
##       ##        ##   ##  ##       ##
##       ##       ##     ##  ######   ######
##       ##       #########       ##       ##
 ######  ######## ##     ##  ######   ######
"""
class Maze(sg.Graph): # Extend PySimpleGUI Graph Class
    """Extension of the sg.Graph class."""
    
    def __init__(self, key, canvas_size, graph_bottom_left, graph_top_right, 
                 background_color, drag_submits, enable_events):
        super().__init__(key=key, 
                         canvas_size=canvas_size, 
                         graph_bottom_left=graph_bottom_left, 
                         graph_top_right=graph_top_right, 
                         background_color=background_color, 
                         drag_submits=drag_submits, 
                         enable_events=enable_events)
        # List of figures in the solution line
        self.solution_figures = []
        
        """
        sg.Graph Super Class Initialization Vars:
        self, canvas_size, graph_bottom_left, graph_top_right, 
        background_color=None, pad=None, p=None, change_submits=False, 
        drag_submits=False, enable_events=False, key=None, k=None, tooltip=None,
        right_click_menu=None, expand_x=False, expand_y=False, visible=True, 
        float_values=False, border_width=0, metadata=None
        """

    
    def resize_maze(self, nodes_across, nodes_down, node_size=NODE_SIZE) -> None:
        """Resizes the maze"""
        global MAZE
        global MAZE_WIDTH
        global MAZE_HEIGHT
        global NODE_SIZE
        global NODES
        MAZE_WIDTH = nodes_across
        MAZE_HEIGHT = nodes_down
        NODE_SIZE = node_size
        print(f"Resize maze:\n",
              f"\t{nodes_across} nodes wide,\n",
              f"\t{nodes_down} nodes down,\n",
              f"\twith a node size of {node_size}"
              )
        
        # Delete all figures
        for node in NODES.values():
            window['maze'].delete_figure(node.id)
        # Empty NODES dictionary
        NODES.clear()
        
        # Create a new graph
        MAZE.clear_solution()
        MAZE.change_coordinates(graph_bottom_left=(0, MAZE_HEIGHT*NODE_SIZE), 
                                graph_top_right=(MAZE_WIDTH*NODE_SIZE, 0))
        MAZE.set_size(size=(MAZE_WIDTH*NODE_SIZE, 
                            MAZE_HEIGHT*NODE_SIZE))
        
        # Initialize new nodes
        for x in range(MAZE_WIDTH):
            for y in range(MAZE_HEIGHT):
                init_node = Node(window['maze'], (x,y))
        
        
    def fill_maze(self) -> None:
        """Fills the entire maze with wall nodes."""
        clear()
        for node in NODES.values():
            node.make_wall_node()
            
    
    def highlight_solution(self, current_node):
        """
        Highlights the maze solution when an algorithm finishes.
        If there is no solution, all visited nodes are highlighted red.
        """
        maze_is_solvable = True
        # If the current node is not the solution node, the maze is unsolvable
        if not current_node.is_end_node:
            maze_is_solvable = False
            for node in [node for node in NODES.values() if node.is_visited]:
                node.make_error_node()
        # If the maze has been solved
        if maze_is_solvable:
            # Draw a path from the end node to the start node using node.parent
            self.solution_figures = []
            while current_node.parent is not None:
                if current_node.is_start_node == True:
                    break
                #current_node.make_solution_node()
                fig = self.draw_line(point_from=current_node.get_center(),
                                    point_to=current_node.parent.get_center(),
                                    color=COLORS['end'],
                                    width=3)
                window.refresh()
                self.solution_figures.append(fig)
                current_node = current_node.parent
        # Re-establish the maze end points    
        START_NODE.make_start_node()
        END_NODE.make_end_node()
        # Show popup if maze is unsolvable
        if not maze_is_solvable:
            sg.popup('Maze could not be solved.')


    def clear_solution(self) -> list:
        """
        Removes all figures drawn for the solution.
        Returns an empty list to be set as the solution figure id list.
        """
        if self.solution_figures:
            for figure_id in self.solution_figures:
                self.delete_figure(figure_id)
            self.solution_figures = []


    def bring_start_and_end_nodes_to_front(self):
        """Bring the starting and ending nodes to the front of the maze."""
        if START_NODE:
            self.bring_figure_to_front(START_NODE.id)
        if END_NODE:
            self.bring_figure_to_front(END_NODE.id)


"""
##      ## #### ##    ## ########   #######  ##      ##
##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ##
 ###  ###  #### ##    ## ########   #######   ###  ###
 
########  ######## ########    ###    ##     ## ##       ########  ######
##     ## ##       ##         ## ##   ##     ## ##          ##    ##    ##
##     ## ##       ##        ##   ##  ##     ## ##          ##    ##
##     ## ######   ######   ##     ## ##     ## ##          ##     ######
##     ## ##       ##       ######### ##     ## ##          ##          ##
##     ## ##       ##       ##     ## ##     ## ##          ##    ##    ##
########  ######## ##       ##     ##  #######  ########    ##     ######
"""
def create_settings_window(root_dir):
    sg.theme('SystemDefaultForReal')
    settings = read_settings()

    # Valid values for maze and node dimensions
    valid_maze_dims = tuple(range(2,201))
    valid_node_dims = tuple(range(5,31,5))
    
    col_1 = [
        [sg.Text('Default Maze:')],
        [sg.Text('Algorithm:')],
        [sg.Text('Speed:')],
        [sg.Text('Maze Width:')]
    ]
    col_2 = [  
        # Default Maze
        [sg.Input(key='default_settings_default_maze', 
                  default_text=settings['default_maze']), 
         sg.FileBrowse(file_types=[('Text Document', '*.txt')], 
                       initial_folder=root_dir)],
        # Default Algorithm
        [sg.Combo(key='default_settings_default_algorithm', 
                  default_value=settings['default_algorithm'], 
                  values=['Breadth-First Search', 
                          'Depth-First Search', 
                          'A* (A Star)'], 
                  size=20, 
                  readonly=True)],
        # Default Speed
        [sg.Combo(key='default_settings_default_speed', 
                  default_value=settings['default_speed'], 
                  values=[1,2,3,4,5], 
                  size=4, 
                  readonly=True)],
        # Maze Dimensions
        [sg.Spin(key='default_settings_maze_width', 
                 initial_value=settings['maze_width'], 
                 values=(valid_maze_dims), 
                 size=(5,1), 
                 expand_x=True), 
         sg.Text('Maze Height:'), 
         sg.Spin(key='default_settings_maze_height', 
                 initial_value=settings['maze_height'], 
                 values=(valid_maze_dims), 
                 size=(5,1), 
                 expand_x=True), 
         sg.Text('Node Size:'), 
         sg.Spin(key='default_settings_maze_node_size', 
                 initial_value=settings['node_size'], 
                 values=(valid_node_dims), 
                 size=(5,1), 
                 expand_x=True, 
                 readonly=True)],
    ]
    settings_layout = [
        [sg.Column(col_1), sg.Column(col_2)],
        [sg.Button('Save'), sg.Button('Close')]  
    ]
    settings_window = sg.Window('Set Defaults', 
                                layout=settings_layout, 
                                keep_on_top=True, 
                                finalize=True)
    return settings_window



"""
##      ## #### ##    ## ########   #######  ##      ##
##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ##
 ###  ###  #### ##    ## ########   #######   ###  ###
 
########  ########  ######  #### ######## ########
##     ## ##       ##    ##  ##       ##  ##
##     ## ##       ##        ##      ##   ##
########  ######    ######   ##     ##    ######
##   ##   ##             ##  ##    ##     ##
##    ##  ##       ##    ##  ##   ##      ##
##     ## ########  ######  #### ######## ########
"""
def create_resize_window():
    """Creates a window to resize the maze."""
    sg.theme('SystemDefaultForReal')
    col_1 = [
        [sg.Text('Maze Width:')],
        [sg.Text('Maze Height:')],
        [sg.Text('Node Size:')],
    ]
    col_2 = [  
        [sg.Spin(key="resize_window_maze_width", 
                 initial_value =MAZE_WIDTH, 
                 values=(list(range(200))), 
                 size=(5,1))], 
        [sg.Spin(key="resize_window_maze_height", 
                 initial_value =MAZE_HEIGHT, 
                 values=(list(range(200))), 
                 size=(5,1))], 
        [sg.Spin(key="resize_window_node_size", 
                 initial_value =NODE_SIZE, 
                 values=(list(range(200))), 
                 size=(5,1))],
    ]
    resize_layout = [
        [sg.Column(col_1), sg.Column(col_2)],
        [sg.Button('Resize'), sg.Button('Close')]  
    ]
    resize_window = sg.Window('Set Defaults', 
                              layout=resize_layout, 
                              keep_on_top=True, 
                              finalize=True)
    return resize_window
    


"""
##      ## #### ##    ## ########   #######  ##      ##
##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ##
 ###  ###  #### ##    ## ########   #######   ###  ###
 
##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##
"""
# Create the Window
def create_main_window() -> object:
    """Creates the main UI window."""
    # Establish color theme
    sg.theme('SystemDefaultForReal')
    
    # Maze graph
    global MAZE
    MAZE = Maze(key="maze",
                canvas_size=(MAZE_WIDTH*NODE_SIZE, MAZE_HEIGHT*NODE_SIZE), 
                graph_bottom_left=(0, MAZE_HEIGHT*NODE_SIZE), 
                graph_top_right=(MAZE_WIDTH*NODE_SIZE, 0), 
                background_color="#ff0000", 
                drag_submits=True, 
                enable_events=True)
    
    # Main menu
    menu = [['File', ['Open Maze', 'Save Maze', 'Exit']], 
            ['Tools', ['Generate Maze', 'Fill Maze']],
            ['Settings', ['Runtime Info', 'Maze Dimensions', 'Defaults']]]
    
    # Algorithm selection radios
    layout_algo_radios = [
        [sg.Radio(group_id='algo', key='radio_algo_bfs', enable_events=True, 
                  text='Breadth First Search', default=True)],
        [sg.Radio(group_id='algo', key='radio_algo_dfs', enable_events=True, 
                  text='Depth First Search')],
        # [sg.Radio(group_id='algo', 
        #           key='radio_algo_dijkstra', 
        #           enable_events=True, 
        #           text='Dijkstra')],
        [sg.Radio(group_id='algo', key='radio_algo_astar', enable_events=True, 
                  text='A* (A Star)')],
        ]
    
    # Maze draw mode buttons 
    layout_maze_tools = [
        [sg.Button(button_text='Wall', key='maze_tools_wall', expand_x=True, 
                   tooltip="Draw walls on the grid."), 
         sg.Button(button_text='Path', key='maze_tools_path', expand_x=True, 
                   tooltip="Erase walls and make paths.")],
        [sg.Button(button_text='Start Node', key='maze_tools_start', 
                   expand_x=True, tooltip="Designate a starting square.")], 
        [sg.Button(button_text='End Node', key='maze_tools_end', 
                   expand_x=True, tooltip="Designate an end square.")]
        ]
    
    # Algorithm controls
    layout_controls = [                             
        [sg.Button('Solve', key='controls_solve', expand_x=True, 
                   tooltip="Solves the maze using the selected algorithm.")],
        [sg.Button('\u23f8', key='controls_pause', expand_x=True, 
                   disabled=True, tooltip="Play/Pause"),
         sg.Button('\u23e9', key='controls_next', expand_x=True, 
                   disabled=True, tooltip="Step Forward")],
        [sg.Text(f'Speed:', key='controls_speed_label')],
        [sg.Slider(range=(1,5), default_value=5, key='controls_speed_slider', 
                   orientation='h', size=(10, 15), expand_x=True, 
                   enable_events=True, disable_number_display=True,
                   tooltip="Speed of the algorithm. Higher is faster.")]
        ]
    
    # Consolidated layout
    layout = [
        # Menu Row
        [sg.Menu(menu_definition=menu, key="main_menu", 
                 background_color='#f0f0f0', tearoff=False, pad=(200, 2))],
        # Maze Row
        [sg.Column(layout=[[MAZE]], 
                   element_justification='center', expand_x=True)],
        # Three frames in one row
        [sg.Frame(title='Algorithm', layout=layout_algo_radios, 
                 expand_y=True, expand_x=True),
         sg.Frame(title='Draw', layout=layout_maze_tools, 
                  expand_y=True, expand_x=True), 
         sg.Frame(title='Controls', layout=layout_controls, 
                  expand_y=True, expand_x=True)
            ],
        # Reset & Clear Buttons
        [sg.Button('Clear Maze', key='maze_tools_clear', expand_x=True, 
                   tooltip="Erases the entire maze, leaving an empty grid."), 
         sg.Button('Reset Current Maze', key='maze_tools_reset', 
                   expand_x=True, 
                   tooltip="Resets the current maze to its initial state.")]
    ]
    return sg.Window(f'PathyPyinder {VERSION}', layout=layout, 
                     icon='assets/icon.ico', finalize=True)

# Create the main window
window = create_main_window()
# Loads settings from settings.cfg from pathypyinder.py's directory
# Resorts to loading from default_settings if settings.cfg fails to load
apply_settings(path.join(path.dirname(__file__), 'settings.cfg'), 
               DEFAULT_SETTINGS)
set_draw_mode('wall')



"""
######## ##     ## ######## ##    ## ########
##       ##     ## ##       ###   ##    ##
##       ##     ## ##       ####  ##    ##
######   ##     ## ######   ## ## ##    ##
##        ##   ##  ##       ##  ####    ##
##         ## ##   ##       ##   ###    ##
########    ###    ######## ##    ##    ##

##        #######   #######  ########
##       ##     ## ##     ## ##     ##
##       ##     ## ##     ## ##     ##
##       ##     ## ##     ## ########
##       ##     ## ##     ## ##
##       ##     ## ##     ## ##
########  #######   #######  ##
"""
# Continuously read the main window for user input
while True:
    if window is None:
        window = create_main_window()
    event, values = window.read()
    # Break the loop if the window is closed
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    # Maze interactions
    if event == 'maze':
        if not MODE:
            pass
        else:
            # get (x,y) coordinates of the node that was clicked
            loc = (values['maze'][0] // NODE_SIZE, 
                   values['maze'][1] // NODE_SIZE)
            # make sure node location is in-bounds
            if -1 < loc[0] < MAZE_WIDTH and -1 < loc[1] < MAZE_HEIGHT:
                # set the current working node
                clicked_node = NODES[loc]
                # draw a node based on the draw mode
                if MODE == 'wall':
                    clicked_node.make_wall_node()
                elif MODE == 'path':
                    clicked_node.make_empty_node()
                elif MODE == 'start':
                    clicked_node.make_start_node()
                elif MODE == 'end':
                    clicked_node.make_end_node()
    
    # Algorithm radio switches
    elif event == 'radio_algo_bfs':
        set_algo('Breadth-First Search')
    elif event == 'radio_algo_dfs':
        set_algo('Depth-First Search')
    elif event == 'radio_algo_dijkstra':
        set_algo('Dijkstra')
    elif event == 'radio_algo_astar':
        set_algo('A* (A Star)')
        
    # Draw tools
    elif event == 'maze_tools_wall':
        set_draw_mode('wall')
    elif event == 'maze_tools_path':
        set_draw_mode('path')
    elif event == 'maze_tools_start':
        set_draw_mode('start')
    elif event == 'maze_tools_end':
        set_draw_mode('end')
        
    # Reset buttons
    elif event == 'maze_tools_clear':
        clear()
    elif event == 'maze_tools_reset':
        reset()
        
    # Algorithm controls
    elif event == 'controls_solve':
        solve_maze()
    elif event == 'controls_speed_slider':
        set_speed(values['controls_speed_slider'])
        
    # Menu
    elif event == 'Open Maze':
        open_maze_file(sg.filedialog.askopenfilename(
            filetypes=[('Text Document', '*.txt')], 
            defaultextension=[('Text Document', '*.txt')]))
    elif event == 'Save Maze':
        save_maze_file(sg.filedialog.asksaveasfile(
            filetypes=[('Text Document', '*.txt')], 
            defaultextension=[('Text Document', '*.txt')]))
    elif event == 'Generate Maze':
        generate_maze()
    elif event == 'Maze Dimensions':
        resize_window = create_resize_window()
        event, values = resize_window.read(close=True)
        if event == 'Resize':
            MAZE.resize_maze(values['resize_window_maze_width'],
                             values['resize_window_maze_height'],
                             values['resize_window_node_size'])
            resize_window.close()
        elif event in ('Close', sg.WIN_CLOSED):
            resize_window.close()
    elif event == 'Fill Maze':
        MAZE.fill_maze()
    elif event == 'Runtime Info':
        sg.popup_scrolled(sg.get_versions())
    elif event == 'Defaults':
        # Directory where pathpyinder.py is
        root_dir = path.join(path.dirname(__file__))
        settings_window = create_settings_window(root_dir)
        event, values = settings_window.read(close=True)
        if event == 'Save':
            save_settings(values)
        elif event in ('Close', sg.WIN_CLOSED):
            settings_window.close()
    
    # Log window event and values
    # print("Event: \t", event)
    # print("Values: ", values)

window.close()