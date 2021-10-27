nodes = {}

class Node(object):
    """
    Creates a 10x10 pixel square on the `maze` graph at (location[0], location[1]) 
    """
    
    def __init__(self, maze: str, location: tuple) -> None:
        self.maze = maze
        self.x = location[0]
        self.y = location[1]
        
        # Draw the node on the graph and store it in the id
        self.id = maze.draw_rectangle(top_left=(self.x*10, self.y*10), 
                                      bottom_right=(self.x*10+10, self.y*10+10),
                                      fill_color='#3399ff',
                                      line_color='#fff',
                                      line_width=1)
        
        # Add the node to the global nodes dictionary
        nodes[(location[0], location[1])] = self

    def update(self, maze, color):
        """
        Updates a node color.

        Args:
            maze (object): The graph object in the main window
            color (str): Hexidecimal string of a color. E.g. '#FFF' or '#2d2d2d'
        """
        maze.delete_figure(self.id)
        self.id = maze.draw_rectangle(top_left=(self.x*10, self.y*10), 
                                      bottom_right=(self.x*10+10, self.y*10+10),
                                      fill_color='#3399ff',
                                      line_color=color,
                                      line_width=1)