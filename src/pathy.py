import PySimpleGUI as sg    # gui wrapper library for tkinter
import time                 # needed for speed setting
import collections          # using .deque() as a stack/queue datastructure for BFS/DFS algorithms





"""
 ######   ##        #######  ########     ###    ##        ######
##    ##  ##       ##     ## ##     ##   ## ##   ##       ##    ##
##        ##       ##     ## ##     ##  ##   ##  ##       ##
##   #### ##       ##     ## ########  ##     ## ##        ######
##    ##  ##       ##     ## ##     ## ######### ##             ##
##    ##  ##       ##     ## ##     ## ##     ## ##       ##    ##
 ######   ########  #######  ########  ##     ## ########  ######
"""
VERSION = '0.0.6'

DEFAULT_MAZE = None     # Filepath to the default maze file to load
DEFAULT_SPEED = 0

NODES = {}              # Node grid in a dictionary with (x,y) tuples as keys
START_NODE = None       # Will be an instance of Node
END_NODE = None         # Will be an instance of Node

ALGO = 'bfs'            # pathing algorithm to use
MODE = 'draw'           # maze draw mode -> can be set to None, 'draw', 'erase', 'start', or 'end'
DELAY = 0               # millisecond delay for algo animation

colors = {
    'empty': '#cccccc',     # grey
    'wall': '#003333',      # black
    'start': '#00cc00',     # green
    'end': '#ff3366',       # orange/red
    
    'active': '#FF0800',    # red
    'visited': '#999966',   # olive
    'neighbor': '#96E8FF',   # light blue
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
    # select the appropriate radio
    window[f'radio_algo_{new_algo}'].update(value=True)
    print(f"Algorithm changed to {new_algo.upper()}")
    
    
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
    for node in NODES.values():
        node.reset_node()
    if START_NODE:
        START_NODE.style(colors['start'], border_color=colors['start'], border_width=2)
    if END_NODE:
        END_NODE.style(colors['end'], border_color=colors['end'], border_width=2)
    

def clear():
    """Empties the entire grid, leaving only empty nodes."""
    global START_NODE
    global END_NODE
    START_NODE = None
    END_NODE = None
    for node in NODES.values():
        node.style(colors['empty'])
        node.is_empty = True
        node.is_wall = False
        node.is_visited = False
        node.is_active = False
        node.is_start_node = False
        node.is_end_node = False
    
    
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
    print(f'Delay set to {DELAY} ms.')


def wait(t) -> None:
    """Waits for t seconds."""
    time.sleep(t)
    
    
def enable_drawing_tools():
    """Enables the `draw`, `erase`, `start, and `end` buttons in the UI and sets the draw mode to 'draw'."""
    global MODE
    window['maze_tools_draw'].update(disabled=False)
    window['maze_tools_erase'].update(disabled=False)
    window['maze_tools_start'].update(disabled=False)
    window['maze_tools_end'].update(disabled=False)
    MODE = 'draw'
    
    
def disable_drawing_tools():
    """Disables the `draw`, `erase`, `start, and `end` buttons in the UI and sets the draw mode to `None`."""
    global MODE
    window['maze_tools_draw'].update(disabled=True, button_color=('#000', '#f0f0f0'))
    window['maze_tools_erase'].update(disabled=True, button_color=('#000', '#f0f0f0'))
    window['maze_tools_start'].update(disabled=True, button_color=('#000', '#f0f0f0'))
    window['maze_tools_end'].update(disabled=True, button_color=('#000', '#f0f0f0'))
    MODE = None



"""
########  ########  ######       ####       ########  ########  ######
##     ## ##       ##    ##     ##  ##      ##     ## ##       ##    ##
##     ## ##       ##            ####       ##     ## ##       ##
########  ######    ######      ####        ##     ## ######    ######
##     ## ##             ##    ##  ## ##    ##     ## ##             ##
##     ## ##       ##    ##    ##   ##      ##     ## ##       ##    ##
########  ##        ######      ####  ##    ########  ##        ######
"""
def bfs_dfs(nodes, start_node):
    """Traverses the maze using a depth-first search algorithm.
    Args:
        nodes (dict): dictionary of all the Nodes in the maze.
        start_node (instance of Node): The starting point for the algorithm.
    """
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
        # flag the current node as active
        current_node.make_active_node()
        # check if it's the end node
        if current_node.is_end_node:
            break
        # for all neighbor nodes
        for neighbor in current_node.get_neighbors():
            # as long as they're not walls, or have been visited
            if not nodes[neighbor].is_wall and not nodes[neighbor].is_visited:
                # nodes[neighbor].make_visited_node()
                nodes[neighbor].make_neighbor_node()
                # mark them as visited
                nodes[neighbor].make_visited_node()
                current_node.make_visited_node()
                nodes[neighbor].parent = current_node
                # 
                if ALGO == 'bfs':
                    stack.appendleft(nodes[neighbor])
                elif ALGO == 'dfs':
                    stack.append(nodes[neighbor])
                # refreseh the window
                window.refresh()
    
    # traverse backwards through parent nodes and mark the solution
    while current_node.parent is not None:
        if current_node.is_start_node == True:
            break
        current_node.make_solution_node()
        current_node = current_node.parent

        
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
        disable_drawing_tools()
        print('*'*40 + f'\nSolve started via {ALGO.upper()} algorithm.\n' + '*'*40)
        # Run algorithm
        if ALGO == 'bfs' or ALGO == 'dfs':
            bfs_dfs(NODES, START_NODE)
        elif ALGO == 'dijkstra':
            pass # TODO: implement algorithm
        elif ALGO == 'astar':
            pass # TODO: implement algorithm
    else:
        sg.popup('The maze needs a start and and end node for a solvable maze.', 'Set these nodes using the "start" and "end" buttons in the maze tools section.')
        print("Needs a start and and end node for a solvable maze.")




        
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
    """Loads a maze from a txt file. File should be formatted as a list of length 50, containing sublists of length 50 each. 
    Each sub-list would contain 50 integers, with each integer ranging from 0-3.
    Integer values represent nodes that are: 'empty', 'walls', 'start nodes', and 'end nodes', respectively."""
    
    # TODO: parse maze file and make sure it's valid
    def valid_maze_file(filename: str):
        if filename:
            return True
        else:
            return False
    
    if valid_maze_file(filename):
        print(f'Maze file to open: {filename}')
        # clear out the existing maze
        clear()
        
        # create a list of lists representing the new maze
        parsed_maze = []
        with open(f'{filename}') as new_maze:
            # for every line in the txt file
            for line in new_maze.readlines():
                # create an integer list representing that row and append it to the maze object
                parsed_maze.append([int(x) for x in line.split(' ')])
                
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
        
            
    with open(f'{filename.name}', 'w') as file_to_write:
        for row in range(50):
            file_to_write.writelines(maze_to_write[row])
            # write a new line at the end of each row, but not at the end of the last line
            if row != 49:
                file_to_write.write('\n')
            
    print(filename)
    
    
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
        sg.Frame('Draw', layout_maze_tools, expand_y=True, expand_x=True),
        sg.Frame('Controls', layout_controls, expand_y=True, expand_x=True)
    ]
]

# Create the Window
window = sg.Window(f'PathyPy {VERSION}', layout)
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
        # print(f'Node created at {self.x}, {self.y}. Node id: {self.id}')

    def style(self, color, border_color='#fff', border_width=1, maze=window['maze']):
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
                                      line_color=border_color,
                                      line_width=border_width)
        # print(f'Node {self.x}, {self.y} color updated to {color}.')
        
    def get_neighbors(self) -> None:
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
    
    
    def make_start_node(self) -> None:
        """Converts the node to a start_node."""
        global START_NODE
        # if there's already a start node, reset it to basic node status
        if START_NODE is not None:
            NODES[(START_NODE.x, START_NODE.y)].style(colors['empty'])
            NODES[(START_NODE.x, START_NODE.y)].is_start_node = False
        # establish the new start node
        START_NODE = self
        self.style(colors['start'], border_color=colors['start'], border_width=2)
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = True
        self.is_end_node = False
    
    
    def make_end_node(self) -> None:
        """Converts the node to an end node."""
        global NODES
        global END_NODE
        # if there's already a end node, reset it to basic node status
        if END_NODE is not None:
            NODES[(END_NODE.x, END_NODE.y)].style(colors['empty'])
            NODES[(END_NODE.x, END_NODE.y)].is_end_node = False
        # establish the new end node
        END_NODE = self
        self.style(colors['end'], border_color=colors['end'], border_width=2)
        self.is_empty = True
        self.is_wall = False
        self.is_start_node = False
        self.is_end_node = True
        

    def make_wall_node(self) -> None:
        """Converts the node to a wall node."""
        self.style(color=colors['wall'], border_color=colors['wall'])
        window['maze'].send_figure_to_back(self.id)
        self.is_empty = False
        self.is_wall = True
        self.is_visited = False
        self.is_start_node = False
        self.is_end_node = False
        

    def make_empty_node(self) -> None:
        """Converts the node to an empty node."""
        self.style(colors['empty'])
        self.is_empty = True
        self.is_wall = False
        if self.is_start_node:
            global START_NODE
            self.is_start_node = False
            START_NODE = None
        elif self.is_end_node:
            global END_NODE
            self.is_end_node = False
            END_NODE = None
        
        
    def make_visited_node(self) -> None:
        """Flags a node as visited."""
        self.style(colors['visited'])
        self.is_visited = True
        
        
    def make_neighbor_node(self) -> None:
        """Flags a node as a neighbor."""
        self.style(colors['neighbor'])
        

    def make_active_node(self) -> None:
        """Flags a node as active."""
        self.style(colors['active'], colors['active'], 3)
        self.is_active = True


    def make_solution_node(self) -> None:
        """Flags a node as part of the solution path."""
        self.style(colors['solution'], colors['solution'])
    
    
    def reset_node(self):
        """Resets a node (removes visited, and active flags, and returns original color.)"""
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
# Create an empty node grid
for x in range(50):
    for y in range(50):
        make_rectangle = Node(window['maze'], (x,y))
        
# Load settings
def load_settings():
    global DEFAULT_MAZE
    global ALGO
    global DEFAULT_SPEED
    with open(f'settings.txt') as settings:
        lines = settings.readlines()
        maze = lines[0].rstrip()
        algo = lines[1].rstrip()
        speed = lines[2].rstrip()

    # Load speed
    if speed:
        window['controls_speed_slider'].update(value=speed)
        set_speed(speed)
    else:
        set_speed(5)
        
    # Load algo
    if algo:
        set_algo(algo)
    else:
        set_algo('bfs')
        
    # Load maze
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
    # continuously read the window for events
    event, values = window.read()
    # break the loop if the window is closed or the 'Exit' button from the menu is clicked
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    # maze interactions
    if event == 'maze':
        if not MODE:
            pass
        else:
            # get a floor division of the graph coordinates to get a node location
            loc = (values['maze'][0] // 10, values['maze'][1] // 10)
            # set the current working node
            clicked_node = NODES[loc]
            # if the location is out of bounds, pass
            if loc not in NODES:
                pass
            # draw a node based on the draw mode
            elif MODE == 'draw':
                clicked_node.make_wall_node()
            elif MODE == 'erase':
                clicked_node.make_empty_node()
            elif MODE == 'start':
                clicked_node.make_start_node()
            elif MODE == 'end':
                clicked_node.make_end_node()
    
    # algorithm radio switches
    elif event == 'radio_algo_bfs':
        set_algo('bfs')
    elif event == 'radio_algo_dfs':
        set_algo('dfs')
    elif event == 'radio_algo_dijkstra':
        set_algo('dijkstra')
    elif event == 'radio_algo_astar':
        set_algo('astar')
        
    # draw tools
    elif event == 'maze_tools_draw':
        set_draw_mode('draw')
    elif event == 'maze_tools_erase':
        set_draw_mode('erase')
    elif event == 'maze_tools_start':
        set_draw_mode('start')
    elif event == 'maze_tools_end':
        set_draw_mode('end')
    elif event == 'maze_tools_clear':
        clear()
        enable_drawing_tools()
    elif event == 'maze_tools_reset':
        reset()
        enable_drawing_tools()
        
    # algorithm controls
    elif event == 'controls_solve':
        solve_maze()
    elif event == 'controls_pause':
        print('Pause button clicked.')
    elif event == 'controls_play':
        print('Play button clicked.')
    elif event == 'controls_stop':
        print('Stop button clicked.')
    elif event == 'controls_speed_slider':
        set_speed(values['controls_speed_slider'])
        
    # menu
    elif event == 'Open Maze':
        open_maze_file(sg.filedialog.askopenfilename(filetypes=[('Text Document', '*.txt')], defaultextension=[('Text Document', '*.txt')]))
    elif event == 'Save Maze':
        save_maze_file(sg.filedialog.asksaveasfile(filetypes=[('Text Document', '*.txt')], defaultextension=[('Text Document', '*.txt')]))
    elif event == 'Runtime Info':
        sg.popup_scrolled(sg.get_versions())
    
    # print out event and values dict
    print("Event: ", end="")
    print(event)
    print("Values: ", end="")
    print(values)

window.close()
