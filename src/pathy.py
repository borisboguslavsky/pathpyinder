import PySimpleGUI as sg
#from maze_node import Node





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
START_NODE = None
END_NODE = None

ALGO = 'bfs'        # pathing algorithm to use
MODE = 'draw'       # maze draw mode -> can be set to 'draw', 'erase', 'start', or 'end'

colors = {
    'empty': '#cccccc',
    'wall': '#003333',
    'start': '#00cc00',
    'end': '#ff3366'
}



"""
##     ## ######## ##       ########  ######## ########   ######
##     ## ##       ##       ##     ## ##       ##     ## ##    ##
##     ## ##       ##       ##     ## ##       ##     ## ##
######### ######   ##       ########  ######   ########   ######
##     ## ##       ##       ##        ##       ##   ##         ##
##     ## ##       ##       ##        ##       ##    ##  ##    ##
##     ## ######## ######## ##        ######## ##     ##  ######
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


def set_start_node(location: tuple) -> None:
    """Set the start node"""
    global NODES
    global START_NODE
    # if there's already a start node, reset it to basic node status
    if START_NODE is not None:
        NODES[(START_NODE.x, START_NODE.y)].color(colors['empty'])
        NODES[(START_NODE.x, START_NODE.y)].status = None
    # establish the new start node
    START_NODE = NODES[location]
    NODES[location].color(colors['start'])
    NODES[location].status = 'start'
    
    
def set_end_node(location: tuple) -> None:
    """Set the end node"""
    global NODES
    global END_NODE
    # if there's already a end node, reset it to basic node status
    if END_NODE is not None:
        NODES[(END_NODE.x, END_NODE.y)].color(colors['empty'])
        NODES[(END_NODE.x, END_NODE.y)].status = None
    # establish the new start node
    END_NODE = NODES[location]
    NODES[location].color(colors['end'])
    NODES[location].status = 'end'
    

def clear():
    """Resets the grid to its initial state"""
    for node in NODES.values():
        node.color(colors['empty'])
        node.status = None
    
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

layout_algo_radios = [
    [sg.Radio(group_id='algo', key='radio_algo_bfs', enable_events=True, text='Breadth First Search', default=True)],
    [sg.Radio(group_id='algo', key='radio_algo_dfs', enable_events=True, text='Depth First Search')],
    [sg.Radio(group_id='algo', key='radio_algo_dijkstra', enable_events=True, text='Dijkstra')],
    [sg.Radio(group_id='algo', key='radio_algo_astar', enable_events=True, text='A*')],
]
layout_maze_tools = [
    [sg.Button('Draw', key='maze_tools_draw', expand_x=True), sg.Button('Erase', key='maze_tools_erase', expand_x=True)],
    [sg.Button('Start', key='maze_tools_start', expand_x=True), sg.Button('End', key='maze_tools_end', expand_x=True)],
    [sg.Button('Clear', key='maze_tools_clear', expand_x=True)]
]
layout_controls = [                             
    [
        sg.Button('Start', key='controls_start', expand_x=True),    # Start
        sg.Button('\u23f8', key='controls_pause', expand_x=True),   # Pause
        sg.Button('\u25b6', key='controls_play', expand_x=True),    # Play
        sg.Button('\u23f9', key='controls_stop', expand_x=True)     # Stop
    ],
    [sg.HorizontalSeparator(pad=(5,15))],
    [sg.Text('Speed:'), sg.Slider(range=(0,5), key='controls_speed_slider', orientation='h', size=(10, 20), expand_x=True, enable_events=True)]
]
layout = [
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
        self.status = None      # type of node: None, 'wall', 'start', 'end'
        
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







for x in range(50):
    for y in range(50):
        make_rectangle = Node(window['maze'], (x,y))




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
            NODES[loc].color(colors['wall'])
            NODES[loc].status = 'wall'
        elif MODE == 'erase':
            NODES[loc].color(colors['empty'])
            NODES[loc].status = None
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
        set_draw_mode('start')
    elif event == 'maze_tools_end':
        set_draw_mode('end')
    elif event == 'maze_tools_clear':
        clear()
    elif event == 'controls_start':
        print('Start button clicked.')
    elif event == 'controls_pause':
        print('Pause button clicked.')
    elif event == 'controls_play':
        print('Play button clicked.')
    elif event == 'controls_stop':
        print('Stop button clicked.')
    elif event == 'controls_speed_slider':
        print('Speed slider modified.')
    
    print(event, type(event))
    print(values)

window.close()