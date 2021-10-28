import PySimpleGUI as sg
import time
import collections
# from set_node import *
# from bfs import bfs
from test_maze import test_maze





"""
 ######   ##        #######  ########     ###    ##        ######
##    ##  ##       ##     ## ##     ##   ## ##   ##       ##    ##
##        ##       ##     ## ##     ##  ##   ##  ##       ##
##   #### ##       ##     ## ########  ##     ## ##        ######
##    ##  ##       ##     ## ##     ## ######### ##             ##
##    ##  ##       ##     ## ##     ## ##     ## ##       ##    ##
 ######   ########  #######  ########  ##     ## ########  ######
"""

NODES = {}          # Node grid in a dictionary with (x,y) tuples as keys
START_NODE = None   # Will be an instance of Node
END_NODE = None     # Will be an instance of Node

ALGO = 'bfs'        # pathing algorithm to use
MODE = 'draw'       # maze draw mode -> can be set to 'draw', 'erase', 'start', or 'end'
DELAY = 0           # millisecond delay for algo animation

SOLVED = False      # Flag for wwwhether the maze has been solved

colors = {
    'empty': '#cccccc',     # grey
    'wall': '#003333',      # black
    'start': '#00cc00',     # green
    'end': '#ff3366',       # orange/red
    
    'active': '#999966',    # olive
    'visited': '#0099ff',   # blue
    'solution': '#009900'   # dark green
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
def set_algo(new_algo:str) -> None:
    """Establishes which algorithm to use for the pathfinder. 
    Permissible values for `algo` are `bfs`, `dfs`, `dijkstra`, and `astar`. """
    global ALGO
    ALGO = new_algo
    print(f"Algorithm changed to {new_algo}")
    
    
def set_draw_mode(draw_mode:str) -> None:
    """Establishes a draw mode.
    `draw`: Draw walls in the maze by clicking and dragging on the grid.
    `erase`: Erase walls in the maze by clicking and dragging on the grid.
    `start`: Click somewhere on the grid to set a start point.
    `end`: Click somewhere on the grid to set an end point.
    """
    global MODE
    global window
    MODE = draw_mode
    # Depress all draw mode buttons and press the current one
    window['maze_tools_draw'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_erase'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_start'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_end'].update(button_color=('#000', '#f0f0f0'))
    window['maze_tools_'+draw_mode].update(button_color='white on green')
    print(f"Draw mode changed to {draw_mode}")
    

def reset() -> None:
    """Clears the solution from the maze and resets all nodes `is_visited`, and `is_active` statuses."""
    for node in NODES:
        NODES[node].reset_node()
    START_NODE.color(colors['start'])
    END_NODE.color(colors['end'])
    
    
def set_speed(speed: float) -> None:
    """Sets a delay (in seconds) between each algorithm iteration"""
    global DELAY
    speed = int(speed)
    if speed == 1:
        DELAY = 0.25
    elif speed == 2:
        DELAY = 0.1
    elif speed == 3:
        DELAY = 0.05
    elif speed == 4:
        DELAY = 0.01
    elif speed == 5:
        DELAY = 0.0


def wait(t) -> None:
    """Waits for t seconds."""
    time.sleep(t)

"""
########  ########  ######
##     ## ##       ##    ##
##     ## ##       ##
########  ######    ######
##     ## ##             ##
##     ## ##       ##    ##
########  ##        ######
"""
def bfs(nodes, start_node, end_node):
    
    # create a stack to be worked through in a first-in, first-out manner
    stack = collections.deque([])
    # add the starting node to the stack
    stack.append(start_node)
    
    # as long as the stack has a node
    while stack:
        # delay
        wait(DELAY)
        # set the top node as the currently active node
        current_node = stack.pop()
        loc = (current_node.x, current_node.y)
        # flag the current node as active
        set_active_node(loc)
        # check if it's the end node
        if current_node.is_end_node:
            break
        # for all neighbor nodes
        for neighbor in current_node.get_neighbors():
            # as long as they're not walls, or have been visited
            if not nodes[neighbor].is_wall and not nodes[neighbor].is_visited:
                # mark them as visited
                set_visited_node(nodes[neighbor].loc)
                nodes[neighbor].parent = current_node
                stack.appendleft(nodes[neighbor])
                # refreseh the window
                window.refresh()
    
    # traverse backwards through parent nodes and mark the solution
    while current_node.parent is not None:
        if current_node.is_start_node == True:
            break
        set_solution_node(current_node.loc)
        current_node = current_node.parent
        




"""
 ######  ######## ########    ##    ##  #######  ########  ########
##    ## ##          ##       ###   ## ##     ## ##     ## ##
##       ##          ##       ####  ## ##     ## ##     ## ##
 ######  ######      ##       ## ## ## ##     ## ##     ## ######
      ## ##          ##       ##  #### ##     ## ##     ## ##
##    ## ##          ##       ##   ### ##     ## ##     ## ##
 ######  ########    ##       ##    ##  #######  ########  ########
"""
def set_state(state, node_location):
    """Sets the boolean state flags of a node according to a passed argument.
    Valid states are: `is_empty`, `is_wall`, `is_visited`, `is_start_node`, `is_end_node`"""
    if state == 'is_empty':
        NODES[node_location].is_empty = True
        NODES[node_location].is_wall = False
    elif state == 'is_wall':
        NODES[node_location].is_empty = False
        NODES[node_location].is_wall = True
        NODES[node_location].is_visited = False
        NODES[node_location].is_start_node = False
        NODES[node_location].is_end_node = False
    elif state == 'is_visited':
        NODES[node_location].is_visited = True
    elif state == 'is_active':
        NODES[node_location].is_active = True
    elif state == 'is_start_node':
        NODES[node_location].is_empty = True
        NODES[node_location].is_wall = False
        NODES[node_location].is_start_node = True
        NODES[node_location].is_end_node = False
    elif state == 'is_end_node':
        NODES[node_location].is_empty = True
        NODES[node_location].is_wall = False
        NODES[node_location].is_start_node = False
        NODES[node_location].is_end_node = True
    
    
def set_start_node(location: tuple) -> None:
    """Set the start node"""
    global START_NODE
    # if there's already a start node, reset it to basic node status
    if START_NODE is not None:
        NODES[(START_NODE.x, START_NODE.y)].color(colors['empty'])
        NODES[(START_NODE.x, START_NODE.y)].is_start_node = False
    # establish the new start node
    START_NODE = NODES[location]
    NODES[location].color(colors['start'])
    set_state('is_start_node', location)
    
    
def set_end_node(location: tuple) -> None:
    """Set the end node"""
    global NODES
    global END_NODE
    # if there's already a end node, reset it to basic node status
    if END_NODE is not None:
        NODES[(END_NODE.x, END_NODE.y)].color(colors['empty'])
        NODES[(END_NODE.x, END_NODE.y)].is_end_node = False
    # establish the new end node
    END_NODE = NODES[location]
    NODES[location].color(colors['end'])
    set_state('is_end_node', location)
    

def set_wall_node(location: tuple) -> None:
    """Sets a wall node."""
    NODES[location].color(colors['wall'])
    set_state('is_wall', location)
    

def set_empty_node(location: tuple) -> None:
    """Sets an empty node."""
    NODES[location].color(colors['empty'])
    set_state('is_empty', location)
    
    
def set_visited_node(location: tuple) -> None:
    """Flags a node as visited."""
    NODES[location].color(colors['visited'])
    set_state('is_visited', location)
    

def set_active_node(location: tuple) -> None:
    """Flags a node as active."""
    NODES[location].color(colors['active'])
    set_state('is_active', location)


def set_solution_node(location: tuple) -> None:
    """Flags a node as part of the solution path."""
    NODES[location].color(colors['solution'])


def clear():
    """Resets the grid to its initial state"""
    for node in NODES.values():
        node.color(colors['empty'])
        node.is_empty = True
        node.is_wall = False
        node.is_visited = False
        node.is_active = False
        node.is_start_node = False
        node.is_end_node = False
        
        
def load_maze(maze_to_load):
    """Loads a maze from a list. List should be 50 sub-lists, with 50 integers in each sub-list.
    Integers can range from 0-3, representing node status' of None, 'wall', 'start', and 'end'"""
    x = 0
    y = 0
    for row in maze_to_load:
        for col in row:
            if col == 0:
                set_empty_node((x, y))
            elif col == 1:
                set_wall_node((x, y))
            elif col == 2:
                set_start_node((x, y))
            elif col == 3:
                set_end_node((x, y))
            else:
                set_empty_node((x, y))
            # reset the x coordinate after rows are finished
            if x < 49:
                x += 1
            else: 
                x = 0
        y += 1
                
    
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

menu = [['File', ['Open Maze', 'Save Maze', 'Exit']]]

layout_algo_radios = [
    [sg.Radio(group_id='algo', key='radio_algo_bfs', enable_events=True, text='Breadth First Search', default=True)],
    [sg.Radio(group_id='algo', key='radio_algo_dfs', enable_events=True, text='Depth First Search')],
    [sg.Radio(group_id='algo', key='radio_algo_dijkstra', enable_events=True, text='Dijkstra')],
    [sg.Radio(group_id='algo', key='radio_algo_astar', enable_events=True, text='A*')],
]
layout_maze_tools = [
    [sg.Button('Draw', key='maze_tools_draw', expand_x=True), sg.Button('Erase', key='maze_tools_erase', expand_x=True)],
    [sg.Button('Start', key='maze_tools_start', expand_x=True), sg.Button('End', key='maze_tools_end', expand_x=True)],
    [sg.Button('Clear', key='maze_tools_clear', expand_x=True), sg.Button('Reset', key='maze_tools_reset', expand_x=True)]
]
layout_controls = [                             
    [
        sg.Button('Solve', key='controls_solve', expand_x=True),    # Start
        sg.Button('\u23f8', key='controls_pause', expand_x=True),   # Pause
        sg.Button('\u25b6', key='controls_play', expand_x=True),    # Play
        sg.Button('\u23f9', key='controls_stop', expand_x=True)     # Stop
    ],
    [sg.HorizontalSeparator(pad=(5,15))],
    [sg.Text('Speed:'), sg.Slider(range=(0,5), default_value=5, key='controls_speed_slider', orientation='h', size=(10, 20), expand_x=True, enable_events=True)]
]
layout = [
    [sg.Menu(menu, background_color='#f0f0f0', tearoff=False, pad=(200, 2))],
    [sg.Graph(key="maze", # Might want to use a table instead
              canvas_size=(500, 500),
              graph_bottom_left=(0,500),
              graph_top_right=(500,0),
              background_color = "#ff0000",
              drag_submits = True,
              enable_events = True,)
    ],
    [
        sg.Frame('Algorithm', layout_algo_radios, expand_y=True, expand_x=True),
        sg.Frame('Maze', layout_maze_tools, expand_y=True, expand_x=True),
        sg.Frame('Controls', layout_controls, expand_y=True, expand_x=True)
    ]
]

# Create the Window
window = sg.Window('Pathy 0.0.1', layout)
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
        self.maze = maze        # reference to the window graph object
        self.x = location[0]    # x coordinate    
        self.y = location[1]    # y coordinate
        self.loc = location     # tuple of (x,y)
        
        # Status properties
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = False
        self.is_end_node = False
        self.is_visited = False
        self.is_active = False
        
        self.parent = None      # parent node for backtracking and highlighting maze solution
        
        # Draw the node on the graph and store it in the id
        self.id = maze.draw_rectangle(top_left=(self.x*10, self.y*10), 
                                      bottom_right=(self.x*10+10, self.y*10+10),
                                      fill_color=colors['empty'],
                                      line_color='#fff',
                                      line_width=1)
        
        # Add the node to the global nodes dictionary
        NODES[(location[0], location[1])] = self
        # Prints result
        print(f'Node created at {self.x}, {self.y}. Node id: {self.id}')

    def color(self, color, maze=window['maze']):
        """
        Updates a node color.

        Args:
            color (str): Hexidecimal string of a color. E.g. '#FFF' or '#2d2d2d'
            maze (object: Optional): The graph object in the main window. Defaults to window['maze'].
        """
        maze.delete_figure(self.id)
        self.id = maze.draw_rectangle(top_left=(self.x*10, self.y*10), 
                                      bottom_right=(self.x*10+10, self.y*10+10),
                                      fill_color=color,
                                      line_color='#fff',
                                      line_width=1)
        print(f'Node {self.x}, {self.y} color updated to {color}.')
        
    def get_neighbors(self):
        """Returns a list of coordinates for in-bound, accessible neighbor nodes. 
        Neighbor nodes are nodes that are above, below, left, or right of the current node."""
        neighbors = []  
        if self.y != 0:
            neighbors.append((self.x, self.y-1)) # top
        if self.x != 49:
            neighbors.append((self.x+1, self.y)) # right
        if self.y != 49:
            neighbors.append((self.x, self.y+1)) # bottom
        if self.x != 0:
            neighbors.append((self.x-1, self.y)) # left
        return neighbors
    
    def reset_node(self):
        """Resets a node (removes visited, and active flags, and returns original color.)"""
        # reset flags
        self.is_visited = False
        self.is_active = False
        # reset colors
        if self.is_wall:
            self.color(colors['wall'], self.maze)
        elif self.is_empty:
            self.color(colors['empty'], self.maze)
        
            





"""
 ######  ########  ########    ###    ######## ########    ##     ##    ###    ######## ########
##    ## ##     ## ##         ## ##      ##    ##          ###   ###   ## ##        ##  ##
##       ##     ## ##        ##   ##     ##    ##          #### ####  ##   ##      ##   ##
##       ########  ######   ##     ##    ##    ######      ## ### ## ##     ##    ##    ######
##       ##   ##   ##       #########    ##    ##          ##     ## #########   ##     ##
##    ## ##    ##  ##       ##     ##    ##    ##          ##     ## ##     ##  ##      ##
 ######  ##     ## ######## ##     ##    ##    ########    ##     ## ##     ## ######## ########
"""
# Create an empty node grid
for x in range(50):
    for y in range(50):
        make_rectangle = Node(window['maze'], (x,y))
        
# Load test maze
load_maze(test_maze)




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
    # continuously read the window for events
    event, values = window.read()
    # break the loop if the window is closed
    if event == sg.WIN_CLOSED:
        break
    
    if event == 'maze':
        loc = (values['maze'][0] // 10, values['maze'][1] // 10)
        if loc not in NODES:
            pass
        elif MODE == 'draw':
            set_wall_node(loc)
        elif MODE == 'erase':
            set_empty_node(loc)
        elif MODE == 'start':
            set_start_node(loc)
        elif MODE == 'end':
            set_end_node(loc)
    
    # switch for various buttons and UI controls
    elif event == 'radio_algo_bfs':
        set_algo('bfs')
    elif event == 'radio_algo_dfs':
        set_algo('dfs')
    elif event == 'radio_algo_dijkstra':
        set_algo('dijkstra')
    elif event == 'radio_algo_astar':
        set_algo('astar')
    elif event == 'maze_tools_draw':
        set_draw_mode('draw')
    elif event == 'maze_tools_erase':
        set_draw_mode('erase')
    elif event == 'maze_tools_start':
        set_draw_mode('solve')
    elif event == 'maze_tools_end':
        set_draw_mode('end')
    elif event == 'maze_tools_clear':
        clear()
    elif event == 'maze_tools_reset':
        reset()
    elif event == 'controls_solve':
        # Check to make sure there's a start and end
        if START_NODE and END_NODE:
            print('*'*40 + '\nStart button clicked.\n' + '*'*40)
            # Run algorithm
            if ALGO == 'bfs':
                bfs(NODES, START_NODE, END_NODE)
        else:
            print("Needs a start and and end node for a solvable maze.")
    elif event == 'controls_pause':
        print('Pause button clicked.')
    elif event == 'controls_play':
        print('Play button clicked.')
    elif event == 'controls_stop':
        print('Stop button clicked.')
    elif event == 'controls_speed_slider':
        set_speed(values['controls_speed_slider'])
        print(f'Delay set to {DELAY} ms.')
    
    print(event, type(event))
    print(values)

window.close()
