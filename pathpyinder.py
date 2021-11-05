import PySimpleGUI as sg                    # Gui wrapper library for tkinter
import time                                 # Needed for speed setting
import collections                          # Using collections.deque() as a stack & queue datastructure for BFS/DFS algorithms
from modules import priority_queue as pq    # Data structure used in Dijkstra's algorithm



"""
 ######   ##        #######  ########     ###    ##        ######
##    ##  ##       ##     ## ##     ##   ## ##   ##       ##    ##
##        ##       ##     ## ##     ##  ##   ##  ##       ##
##   #### ##       ##     ## ########  ##     ## ##        ######
##    ##  ##       ##     ## ##     ## ######### ##             ##
##    ##  ##       ##     ## ##     ## ##     ## ##       ##    ##
 ######   ########  #######  ########  ##     ## ########  ######
"""
VERSION = '1.2.0'

NODES = {}                      # Node grid in a dictionary with (x,y) tuples as keys
START_NODE = None               # An instance of Node. The node from which the algorithm starts.
END_NODE = None                 # An instance of Node. The node at which the maze is 'solved'.

ALGO = 'bfs'                    # Pathfinding algorithm to use.
MODE = 'wall'                   # Grid draw mode -> can be set to None, 'wall', 'path', 'start', or 'end'
TEMP_DELAY = None               # Temporary variable to store original DELAY while DELAY is overwritten with None for one loop iteration (used for next button)
DELAY = 0                       # Delay (in seconds) for every iteration of the algorithm loop
SPEED = None                    # Speed level (1-5) displayed above the speed slider, loaded on initialization

STOPPED = False
PAUSED = False

colors = {                      # Dictionary of colors to use in Node.style()
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
    
    'black': '000000',
    'white': 'FFFFFF',
}



"""
##     ## ####       ##     ## ######## ##       ########  ######## ########   ######
##     ##  ##        ##     ## ##       ##       ##     ## ##       ##     ## ##    ##
##     ##  ##        ##     ## ##       ##       ##     ## ##       ##     ## ##
##     ##  ##        ######### ######   ##       ########  ######   ########   ######
##     ##  ##        ##     ## ##       ##       ##        ##       ##   ##         ##
##     ##  ##        ##     ## ##       ##       ##        ##       ##    ##  ##    ##
 #######  ####       ##     ## ######## ######## ##        ######## ##     ##  ######
"""
def set_algo(new_algo: str) -> None:
    """Establishes which algorithm to use for the pathfinder. Valid values for `new_algo` are: 
    `'bfs'`: Breadth-first
    `'dfs'`: Depth-first
    `'dijkstra'`: Dijkstra
    `'astar'`: A*
    """
    global ALGO
    ALGO = new_algo
    # select the appropriate radio
    window[f'radio_algo_{new_algo}'].update(value=True)
    print(f"Algorithm set to {new_algo.upper()}")
    
    
def set_draw_mode(draw_mode: str) -> None:
    """Establishes a draw mode. Valid values for draw_mode are:
    `'wall'`: Draw walls in the maze by clicking and dragging on the grid.
    `'path'`: Erase walls in the maze by clicking and dragging on the grid.
    `'start'`: Click somewhere on the grid to set a start point.
    `'end'`: Click somewhere on the grid to set an end point.
    """
    global MODE
    global window
    MODE = draw_mode
    # Depress all draw mode buttons and press the current one
    window['maze_tools_wall'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_wall'].Widget.configure(relief='raised')
    window['maze_tools_path'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_path'].Widget.configure(relief='raised')
    window['maze_tools_start'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_start'].Widget.configure(relief='raised')
    window['maze_tools_end'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_end'].Widget.configure(relief='raised')
    window['maze_tools_'+draw_mode].update(button_color='white on grey')
    window['maze_tools_'+draw_mode].Widget.configure(relief='sunken')
    print(f"Draw mode set to '{draw_mode}'")
    

def maze_tooltip() -> str:
    """Returns the tooltip for the maze."""
    return 'Tooltip'


def maze_right_click_menu() -> list:
    """The menu that will open when a maze node is right clicked."""
    return ['',['Coordinates', 'Item2']]


def bring_start_and_end_nodes_to_front():
    """Bring the starting and ending nodes to the front of the maze."""
    if START_NODE:
        window['maze'].bring_figure_to_front(START_NODE.id)
    if END_NODE:
        window['maze'].bring_figure_to_front(END_NODE.id)

def reset() -> None:
    """Clears the solution from the maze and sets all nodes' `is_visited`, and `is_active` flags to `False` via the `Node.reset()` method."""
    for node in NODES.values():
        node.reset_node()
    bring_start_and_end_nodes_to_front()
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
    

def clear() -> None:
    """Empties the entire grid, leaving only path/empty nodes."""
    for node in NODES.values():
        node.make_empty_node()
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
    
    
def set_speed(speed: float) -> None:
    """Sets a delay (in milliseconds) between each algorithm iteration"""
    global DELAY
    global TEMP_DELAY
    global SPEED
    SPEED = int(speed)
    window['controls_speed_label'].update(value=f'Speed: {SPEED}')
    if SPEED == 1:
        DELAY = 1500
        TEMP_DELAY = 1500
    elif SPEED == 2:
        DELAY = 750
        TEMP_DELAY = 750
    elif SPEED == 3:
        DELAY = 250
        TEMP_DELAY = 250
    elif SPEED == 4:
        DELAY = 50
        TEMP_DELAY = 50
    elif SPEED == 5:
        DELAY = 0
        TEMP_DELAY = 0
    print(f'Delay set to: {DELAY}ms.')


def wait(t) -> None:
    """Waits for t seconds."""
    time.sleep(t)
    
    
def disable_element(sg_key) -> None:
    """Disables a button."""
    window[sg_key].update(disabled=True)


def enable_element(sg_key) -> None:
    """Enables a button."""
    window[sg_key].update(disabled=False)


def raise_button(sg_key, colors=('#000', '#f0f0f0')) -> None:
    """
    Styles a button to be de-pressed
    
    Args:
        `sg_key` (str): The PySimpleGUI Key for the button
        `button_color` (tuple or str): Two colors for the button text, and background, respectively.
            Example: 'white on grey', ('#000', '#f0f0f0')
    """
    window[sg_key].update(button_color=colors)
    window[sg_key].Widget.configure(relief='raised')
    

def recess_button(sg_key, colors=('#000', '#f0f0f0')) -> None:
    """
    Styles a button to be pressed
    
    Args:
        `sg_key` (str): The PySimpleGUI Key for the button
        `button_color` (tuple or str): Two colors for the button text, and background, respectively.
            Example: 'white on grey', ('#000', '#f0f0f0')
    """
    window[sg_key].update(button_color=colors)
    window[sg_key].Widget.configure(relief='sunken')
    
    
def enable_drawing_tools() -> None:
    """Enables the `wall`, `path`, `start, and `end` buttons in the UI and sets the draw mode to 'wall'."""
    for button in ['maze_tools_wall', 'maze_tools_path', 'maze_tools_start', 'maze_tools_end']: 
        enable_element(button)
    
    
def disable_drawing_tools() -> None:
    """Disables the `wall`, `path`, `start, and `end` buttons in the UI and sets the draw mode to `None`."""
    for button in ['maze_tools_wall', 'maze_tools_path', 'maze_tools_start', 'maze_tools_end']: 
        window[button].update(disabled=True, button_color=('#000', '#f0f0f0'))


def enable_algo_radios() -> None:
    """Enables the algorithm selection radios."""
    for radio in ['radio_algo_bfs', 'radio_algo_dfs', 'radio_algo_dijkstra', 'radio_algo_astar']:
        enable_element(radio)


def disable_algo_radios() -> None:
    """Disables the algorithm selection radios."""
    for radio in ['radio_algo_bfs', 'radio_algo_dfs', 'radio_algo_dijkstra', 'radio_algo_astar']:
        disable_element(radio)
    
    
def read_algo_controls(timeout=None) -> bool:
    """Reads inputs from the control panel while the algorithm is running.
    Returns `True` to continue running. Returns `False` to break out of the algorithm loop."""
    event, values = window.read(timeout)
    # Break out of the function if it's just a timeout event
    if event == '__TIMEOUT__':
        return True # Keep going
    
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
        return True
        
    # Next Button
    elif event == 'controls_next':
        TEMP_DELAY = DELAY
        DELAY = None
        return True
    
    # Speed Slider
    elif event == 'controls_speed_slider':
        set_speed(values['controls_speed_slider'])
        if PAUSED:
            return read_algo_controls(timeout=None)
        return True
        
    # Reset/Clear Buttons
    elif event == 'maze_tools_clear':
        clear()
        return False
    elif event == 'maze_tools_reset':
        reset()
        return False
    # Log window event and values
    print("Event: \t", event)
    print("Values: ", values)
    return True

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
    """Traverses the maze using either a breadth-first or depth-first search algorithm.
    The two are the same except for the underlying data structure used. 
    Breadth-first uses a queue (first in, first out).
    Depth first uses a stack (last in, first out).
    """
    interrupted = False
    # use a stack suitable for both bfs and dfs, allowing for both lifo and fifo operations
    stack = collections.deque([])
    # add the starting node to the stack
    stack.append(START_NODE)
    
    # as long as the stack has a node
    while stack:
        # set the top node as the currently active node
        current_node = stack.pop()
        current_node.make_active_node()
        
        # Check for user input.
        # Break out of the loop if read_algo_controls() returns False
        if not read_algo_controls(timeout=DELAY): 
            interrupted = True
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
                if ALGO == 'bfs': # queue: first in, first out
                    stack.appendleft(neighbor)
                elif ALGO == 'dfs': # stack: last in, first out
                    stack.append(neighbor)
    
    # Mark the solution path
    if not interrupted: highlight_solution(current_node)



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
    
    # Initialize an updateable priority queue with the start node in it, at priority 0
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
        
        # Check for user input.
        # Break out of the loop if read_algo_controls() returns False
        if not read_algo_controls(timeout=DELAY): 
            interrupted = True
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
                window.refresh()
                # Calculate the distance of that node to the start node
                min_distance = min(neighbor.distance, current_node.distance + 1)
                if min_distance != neighbor.distance:
                    neighbor.distance = min_distance
                    # Change queue priority for the nieghbor since it's now closer
                    queue.push(neighbor.loc, neighbor.distance)
                    # Set the current node as the parent node for each neighbor
                    neighbor.parent = current_node
        # Mark the current node as visited
        current_node.make_visited_node()
            
    # Mark the solution path
    if not interrupted: highlight_solution(current_node)



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
    """Finds the solution to the maze using the A-star (A*) algorithm.
    """
    interrupted = False
    
    # Initialize an updateable priority queue with the start node in it, at priority 0
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
        
        # Check for user input.
        # Break out of the loop if read_algo_controls() returns False
        if not read_algo_controls(timeout=DELAY): 
            interrupted = True
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
                window.refresh()
                # Set distance to be the manhattan distance from the neighbor to the end node
                neighbor.distance = (abs(END_NODE.x - neighbor.x) + abs(END_NODE.y - neighbor.y))
                # Update the queue with the new distance. queue.push() adds a new entry, or updates an existing one
                queue.push(neighbor.loc, neighbor.distance)
                # Establish parent node
                neighbor.parent = current_node
                
        # Mark the current node as visited
        current_node.make_visited_node()
            
    # Mark the solution path
    if not interrupted: highlight_solution(current_node)


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
        # 
        enable_element('controls_pause')
        disable_element('controls_solve')
        recess_button('controls_solve')
        disable_drawing_tools()
        disable_algo_radios()
        
        print('*'*40 + f'\nSolve started via {ALGO.upper()} algorithm.\n' + '*'*40)
        # Run algorithm
        if ALGO == 'bfs' or ALGO == 'dfs':
            bfs_dfs()
        elif ALGO == 'dijkstra':
            dijkstra()
        elif ALGO == 'astar':
            astar()
    # Show a popup message if there's not both a start and end node
    else:
        sg.popup('The maze needs a start and and end node for a solvable maze.', 'Set these nodes using the "Start Node" and "End Node" buttons in the maze tools section.')


def highlight_solution(current_node):
    """Walks back all the parents from the current node and highlights them green."""
    disable_element('controls_pause')
    raise_button('controls_pause')
    disable_element('controls_next')
    while current_node.parent is not None:
        if current_node.is_start_node == True:
            break
        current_node.make_solution_node()
        current_node = current_node.parent
        window.refresh()
    START_NODE.make_start_node()
    END_NODE.make_end_node()

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
    """Loads a maze from a txt file. File should be formatted as a .txt file with 50 rows and 99 columns. 
    Each row should contain 50 integers separated by a space, with each integer ranging from 0-3. The last character of each row should not have a space after it.
    Integer values represent nodes types:
    0: Path node
    1: Wall node
    2: Start node
    3: End node
    """
    
    # TODO: parse maze file and make sure it's valid
    def valid_maze_file(filename: str):
        if filename:
            return True
        else:
            return False
    
    if valid_maze_file(filename):
        try:
            print(f'Open maze file: {filename}')
            # clear out the existing maze
            clear()
            
            # create a list of lists representing the new maze
            parsed_maze = []
            with open(f'{filename}') as new_maze:
                # for every line in the txt file
                for line in new_maze.readlines():
                    # create an integer list representing that row and append it to the maze object
                    parsed_maze.append([int(x) for x in line.split(' ')])
                    
            # convert nodes according to the list
            x = 0
            y = 0
            for row in parsed_maze:
                for col in row:
                    if col == 0:
                        NODES[(x,y)].make_empty_node()
                    elif col == 1:
                        NODES[(x,y)].make_wall_node()
                    elif col == 2:
                        NODES[(x,y)].make_start_node()
                    elif col == 3:
                        NODES[(x,y)].make_end_node()
                        
                    # reset the x coordinate after rows are finished
                    if x < 49:
                        x += 1
                    else: 
                        x = 0
                y += 1
            bring_start_and_end_nodes_to_front()
        except:
            sg.popup('Error loading maze')



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
    if not filename:
        return False
    
    """Saves the maze to a file."""
    # list that stores the maze
    maze_to_write = []
    for col in range(50):
        row_list = []
        for row in range(50):
            if NODES[(row, col)].is_start_node:
                row_list.append('2 ')
            elif NODES[(row, col)].is_end_node:
                row_list.append('3 ')
            elif NODES[(row, col)].is_empty:
                row_list.append('0 ')
            elif NODES[(row, col)].is_wall:
                row_list.append('1 ')
        maze_to_write.append(row_list)
    
    # remove trailing space from the last node in each row
    for row in maze_to_write:
        row[49] = row[49][0]
        
    # write maze_to_write to a file
    with open(f'{filename.name}', 'w') as file_to_write:
        for row in range(50):
            file_to_write.writelines(maze_to_write[row])
            # write a new line at the end of each row, but not at the end of the last line
            if row != 49:
                file_to_write.write('\n')
            
    print(f'Save maze to: {filename}')
    


"""
##     ## ####
##     ##  ##
##     ##  ##
##     ##  ##
##     ##  ##
##     ##  ##
 #######  ####
"""
sg.theme('SystemDefaultForReal')

menu = [['File', ['Open Maze', 'Save Maze', 'Exit']], 
        ['About', ['Runtime Info']],]

layout_algo_radios = [
    [sg.Radio(group_id='algo', key='radio_algo_bfs', enable_events=True, text='Breadth First Search', default=True)],
    [sg.Radio(group_id='algo', key='radio_algo_dfs', enable_events=True, text='Depth First Search')],
    [sg.Radio(group_id='algo', key='radio_algo_dijkstra', enable_events=True, text='Dijkstra')],
    [sg.Radio(group_id='algo', key='radio_algo_astar', enable_events=True, text='A*')],
]
layout_maze_tools = [
    [
        sg.Button('Wall', key='maze_tools_wall', expand_x=True, tooltip="Draw walls on the grid."), 
        sg.Button('Path', key='maze_tools_path', expand_x=True, tooltip="Erase walls and make paths.")
    ],
    [sg.Button('Start Node', key='maze_tools_start', expand_x=True, tooltip="Designate a starting square.")], 
    [sg.Button('End Node', key='maze_tools_end', expand_x=True, tooltip="Designate an end square.")]
]
layout_controls = [                             
    [
        sg.Button('Solve', key='controls_solve', expand_x=True, tooltip="Solves the maze using the selected algorithm."),    # Solve
    ],
    [
        sg.Button('\u23f8', key='controls_pause', expand_x=True, disabled=True, tooltip="Play/Pause"),   # Play/pause
        sg.Button('\u23e9', key='controls_next', expand_x=True, disabled=True, tooltip="Step Forward"),    # Next
    ],
    [
        sg.Text(f'Speed:', key='controls_speed_label'), 
    ],
    [
        sg.Slider(range=(1,5), 
                  default_value=5, 
                  key='controls_speed_slider', 
                  orientation='h', 
                  size=(10, 15), 
                  expand_x=True, 
                  enable_events=True, 
                  disable_number_display=True,
                  tooltip="Speed of the algorithm. Higher is faster.")
    ]
]
layout = [
    [sg.Menu(menu, background_color='#f0f0f0', tearoff=False, pad=(200, 2))],
    [sg.Graph(key="maze", # Might want to use a table instead
              canvas_size=(500, 500),
              graph_bottom_left=(0,500),
              graph_top_right=(500,0),
              background_color="#ff0000",
              drag_submits=True,
              enable_events=True,
              right_click_menu=maze_right_click_menu())
    ],
    [
        [sg.Frame('Algorithm', layout_algo_radios, expand_y=True, expand_x=True),
        sg.Frame('Draw', layout_maze_tools, expand_y=True, expand_x=True), 
        sg.Frame('Controls', layout_controls, expand_y=True, expand_x=True)],
        [
            sg.Button('Clear Maze', key='maze_tools_clear', expand_x=True, tooltip="Erases the entire maze, leaving an empty grid."), 
            sg.Button('Reset Current Maze', key='maze_tools_reset', expand_x=True, tooltip="Resets the current maze to its initial state.")
        ]
    ]
]

# Create the Window
window = sg.Window(f'PathyPyinder {VERSION}', layout)
window.Finalize()



"""
##    ##  #######  ########  ########     ######  ##          ###     ######   ######
###   ## ##     ## ##     ## ##          ##    ## ##         ## ##   ##    ## ##    ##
####  ## ##     ## ##     ## ##          ##       ##        ##   ##  ##       ##
## ## ## ##     ## ##     ## ######      ##       ##       ##     ##  ######   ######
##  #### ##     ## ##     ## ##          ##       ##       #########       ##       ##
##   ### ##     ## ##     ## ##          ##    ## ##       ##     ## ##    ## ##    ##
##    ##  #######  ########  ########     ######  ######## ##     ##  ######   ######
"""
class Node(object):
    """
    Creates a maze node on the window graph at (location[0], location[1]) represented as a 10x10 pixel square.
    The graph is 500x500px, so there can be a total of 50x50 nodes in the window.
    """
    def __init__(self, maze: str, location: tuple) -> None:
        self.maze = maze                    # reference to the window graph object
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
        
        self.parent = None                  # parent node for backtracking and highlighting maze solution
        self.distance = float('inf')        # generic distance attribute of the node (used in dijkstra and astar algorithms)
        #self.start_distance = float('inf')  # distance of the node from the start node (used in astar algorithm)
        #self.end_distance = float('inf')    # distance of the node from the end node (used in astar algorithm)
        
        # Draw the node on the graph and store the drawn figure in the id attribute
        self.id = maze.draw_rectangle(top_left=(self.x*10, self.y*10), 
                                      bottom_right=(self.x*10+10, self.y*10+10),
                                      fill_color=colors['empty'],
                                      line_color='#fff',
                                      line_width=1)
        
        # Add the node to the global nodes dictionary
        NODES[(location[0], location[1])] = self
        # print(f'Node created at {self.x}, {self.y}. Node id: {self.id}')


    def style(self, color, border_color='#fff', border_width=1):
        """
        Updates a node color.

        Args:
            `color` (str: Optional): Hexidecimal string of a color. E.g. `'#FFF'` or `'#2D2D2D'`
            `border_color` (str: Optional): Hexidecimal string of a color.
            `border_width` (int: Optional): Width of the border in pixels.
        """
        self.maze.delete_figure(self.id)
        self.id = self.maze.draw_rectangle(top_left=(self.x*10, self.y*10), 
                                           bottom_right=(self.x*10+10, self.y*10+10),
                                           fill_color=color,
                                           line_color=border_color,
                                           line_width=border_width)
        # print(f'Node {self.x}, {self.y} color updated to {color}.')
    

    def get_neighbors(self) -> None:
        """Returns a list of nodes for in-bound, accessible neighbor nodes that have not been visited. 
        Neighbor nodes are nodes that are above, below, left, or right of the node this method was called on."""
        neighbors = []  
        if self.y != 0:
            neighbors.append(NODES[(self.x, self.y-1)]) # top
        if self.x != 49:
            neighbors.append(NODES[(self.x+1, self.y)]) # right
        if self.y != 49:
            neighbors.append(NODES[(self.x, self.y+1)]) # bottom
        if self.x != 0:
            neighbors.append(NODES[(self.x-1, self.y)]) # left
        # Prune neighbors list to remove visited nodes and wall nodes
        return [node for node in neighbors if not node.is_wall and not node.is_visited]
    

    def make_start_node(self) -> None:
        """Converts the node to a start node."""
        global START_NODE
        # Remove existing start node
        if START_NODE:
            START_NODE.make_empty_node()
        START_NODE = self
        self.style(colors['start'], border_color=colors['start_border'], border_width=4)
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
        self.style(colors['end'], border_color=colors['end_border'], border_width=4)
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = False
        self.is_end_node = True
        self.distance = float('inf')
        self.start_distance = float('inf')
        self.end_distance = float('inf')
        

    def make_wall_node(self) -> None:
        """Converts the node to a wall node."""
        self.style(color=colors['wall'], border_color=colors['wall'])
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
        self.style(colors['empty'])
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
        
    
    def make_visited_node(self) -> None:
        """Flags and styles a node as visited."""
        self.style(colors['visited'])
        self.is_visited = True
        
    def make_neighbor_node(self) -> None:
        """Styles a node as a neighbor."""
        self.style(colors['neighbor'])
        self.is_visited = True

    def make_active_node(self) -> None:
        """Flags and styles a node as active."""
        self.style(colors['active'], colors['black'], border_width=3)
        self.is_active = True

    def make_solution_node(self) -> None:
        """Styles a node as part of the solution path."""
        self.style(colors['solution'], colors['solution'])


    def reset_node(self):
        """Resets a node (removes visited, and active flags, and returns original style.)"""
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
#### ##    ## #### ########
 ##  ###   ##  ##     ##
 ##  ####  ##  ##     ##
 ##  ## ## ##  ##     ##
 ##  ##  ####  ##     ##
 ##  ##   ###  ##     ##
#### ##    ## ####    ##
"""
# Create an empty node grid to initialize all nodes
for x in range(50):
    for y in range(50):
        init_node = Node(window['maze'], (x,y))

# Load settings
def load_settings():
    # Read settings file
    with open(f'settings.txt') as settings:
        lines = settings.readlines()
        maze = lines[0].rstrip()
        algo = lines[1].rstrip()
        speed = lines[2].rstrip()
        
    # Set initial speed
    if speed:
        window['controls_speed_slider'].update(value=speed)
        set_speed(speed)
    else:
        set_speed(5)
        
    # Set initial algorithm
    if algo:
        set_algo(algo)
    else:
        set_algo('bfs')
        
    # Set initial draw mode
    set_draw_mode('wall')
    
    # Open default maze
    if maze:
        open_maze_file(maze)
    
load_settings()



"""
######## ##     ## ######## ##    ## ########    ##        #######   #######  ########
##       ##     ## ##       ###   ##    ##       ##       ##     ## ##     ## ##     ##
##       ##     ## ##       ####  ##    ##       ##       ##     ## ##     ## ##     ##
######   ##     ## ######   ## ## ##    ##       ##       ##     ## ##     ## ########
##        ##   ##  ##       ##  ####    ##       ##       ##     ## ##     ## ##
##         ## ##   ##       ##   ###    ##       ##       ##     ## ##     ## ##
########    ###    ######## ##    ##    ##       ########  #######   #######  ##
"""
while True:
    # Continuously read the window for events
    event, values = window.read()
    # Break the loop if the window is closed or the 'Exit' button from the menu is clicked
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    # Maze interactions
    if event == 'maze':
        if not MODE:
            pass
        else:
            # get a floor division of the graph coordinates to get a node location
            loc = (values['maze'][0] // 10, values['maze'][1] // 10)
            # make sure node location is in-bounds
            if -1 < loc[0] < 50 and -1 < loc[1] < 50:
                # set the current working node
                clicked_node = NODES[loc]
                # if the location is out of bounds, pass
                if loc not in NODES:
                    pass
                # draw a node based on the draw mode
                elif MODE == 'wall':
                    clicked_node.make_wall_node()
                elif MODE == 'path':
                    clicked_node.make_empty_node()
                elif MODE == 'start':
                    clicked_node.make_start_node()
                elif MODE == 'end':
                    clicked_node.make_end_node()
            # In case a path or well overlaps next to a start/end node
            bring_start_and_end_nodes_to_front()
    
    # Algorithm radio switches
    elif event == 'radio_algo_bfs':
        set_algo('bfs')
    elif event == 'radio_algo_dfs':
        set_algo('dfs')
    elif event == 'radio_algo_dijkstra':
        set_algo('dijkstra')
    elif event == 'radio_algo_astar':
        set_algo('astar')
        
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
        open_maze_file(sg.filedialog.askopenfilename(filetypes=[('Text Document', '*.txt')], defaultextension=[('Text Document', '*.txt')]))
    elif event == 'Save Maze':
        save_maze_file(sg.filedialog.asksaveasfile(filetypes=[('Text Document', '*.txt')], defaultextension=[('Text Document', '*.txt')]))
    elif event == 'Runtime Info':
        sg.popup_scrolled(sg.get_versions())
    
    # Log window event and values
    print("Event: \t", event)
    print("Values: ", values)

window.close()
